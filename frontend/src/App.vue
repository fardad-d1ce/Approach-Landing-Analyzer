<script setup>
import { ref } from 'vue'

const API_BASE_URL = 'http://127.0.0.1:8000'

const statusMessage = ref('')
const isLoading = ref(false)
const selectedFile = ref(null)
const analysisResults = ref(null)
const evaluationTableHtml = ref('')
const fileInput = ref(null)
const selectedChartUrl = ref(null)

const openModal = (url) => {
  selectedChartUrl.value = url
}

const closeModal = () => {
  selectedChartUrl.value = null
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  selectedFile.value = file || null
}

const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const toApiUrl = (path) => {
  if (!path) {
    return ''
  }

  return path.startsWith('http') ? path : `${API_BASE_URL}${path}`
}

const loadEvaluationTableHtml = async (results) => {
  evaluationTableHtml.value = ''

  if (!results?.evaluation_table_html_url) {
    return
  }

  try {
    const response = await fetch(toApiUrl(results.evaluation_table_html_url))
    if (!response.ok) {
      throw new Error('Failed to load landing evaluation table.')
    }
    evaluationTableHtml.value = await response.text()
  } catch (error) {
    console.error(error)
  }
}

const applyResults = async (results) => {
  analysisResults.value = results
  await loadEvaluationTableHtml(results)
}

const parseApiResponse = async (response) => {
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || data.message || 'The backend request failed.')
  }

  return data
}

const triggerAnalysis = async () => {
  isLoading.value = true
  statusMessage.value = 'Running analysis...'

  try {
    const formData = new FormData()
    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    }

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: selectedFile.value ? formData : null
    })
    const data = await parseApiResponse(response)

    await applyResults(data.results)
    statusMessage.value = `Success: ${data.message}`
  } catch (error) {
    statusMessage.value = error.message || 'Failed to connect to the backend. Is the Python API running?'
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const loadLatest = async () => {
  isLoading.value = true
  statusMessage.value = 'Loading cached results...'

  try {
    const response = await fetch(`${API_BASE_URL}/latest`)
    const data = await parseApiResponse(response)

    await applyResults(data.results)
    statusMessage.value = `Success: ${data.message}`
  } catch (error) {
    statusMessage.value = error.message || 'Failed to load latest results.'
    console.error(error)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="container">
    <section class="hero">
      <h1>Approach &amp; Landing Analyzer</h1>
      <p>
        Upload a CSV file or run analysis with the default dataset configured in
        <code>config.toml</code>.
      </p>

      <div class="controls">
        <div class="upload-section">
          <input
            id="csv-upload"
            type="file"
            accept=".csv"
            @change="handleFileChange"
            class="file-input"
            ref="fileInput"
          />
          <div class="file-label-wrapper">
            <label for="csv-upload" class="file-label" :class="{ 'has-file': selectedFile }">
              {{ selectedFile ? selectedFile.name : 'Upload CSV Telemetry Data' }}
            </label>
            <button 
              v-if="selectedFile" 
              @click.prevent="removeFile" 
              class="remove-btn" 
              title="Remove file"
            >
              ✕
            </button>
          </div>
        </div>

        <button @click="triggerAnalysis" :disabled="isLoading" class="action-btn">
          {{ isLoading ? 'Processing...' : (selectedFile ? 'Analyze Uploaded Data' : 'Run Analysis') }}
        </button>

        <button @click="loadLatest" :disabled="isLoading" class="action-btn secondary-btn" title="Load the last successful analysis to test UI without waiting">
          Load Latest Run
        </button>
      </div>

      <div v-if="statusMessage" class="status-box" :class="{ 'is-loading': isLoading }">
        {{ statusMessage }}
      </div>
    </section>

    <section v-if="analysisResults" class="results-section">
      <div class="section-heading">
        <h2>Pilots Landing Evaluation</h2>
        <p>{{ analysisResults.folder_name }}</p>
      </div>

      <div v-if="evaluationTableHtml" class="table-shell">
        <div class="table-scroll" v-html="evaluationTableHtml"></div>
      </div>
      <div v-else-if="analysisResults.evaluation_table_image_url" class="fallback-image-card">
        <img
          :src="toApiUrl(analysisResults.evaluation_table_image_url)"
          alt="Pilots landing evaluation table"
          class="result-image"
        />
      </div>
      <p v-else class="empty-state">No landing evaluation table was generated for this run.</p>
    </section>

    <section v-if="analysisResults" class="results-section">
      <div class="section-heading">
        <h2>Pilots Landing Charts</h2>
        <p>{{ analysisResults.landing_charts.length }} chart(s)</p>
      </div>

      <div v-if="analysisResults.landing_charts.length" class="chart-grid">
        <article
          v-for="chart in analysisResults.landing_charts"
          :key="chart.title"
          class="chart-card"
        >
          <img
            :src="toApiUrl(chart.url)"
            :alt="chart.title"
            class="chart-image clickable-chart"
            loading="lazy"
            @click="openModal(toApiUrl(chart.url))"
          />
          <div class="chart-meta">
            <h3>{{ chart.title }}</h3>
            <!-- <p>{{ chart.filename }}</p> -->
          </div>
        </article>
      </div>
      <p v-else class="empty-state">No landing charts were generated for this run.</p>
    </section>

    <!-- Modal for Enlarged Chart -->
    <Teleport to="body">
      <div v-if="selectedChartUrl" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <button class="close-modal-btn" @click="closeModal" title="Close">✕</button>
          <img :src="selectedChartUrl" alt="Enlarged Chart" class="enlarged-image" />
        </div>
      </div>
    </Teleport>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  background: #f4f7fb;
  color: #1f2937;
  font-family: Inter, "Segoe UI", Tahoma, sans-serif;
}

:global(*) {
  box-sizing: border-box;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.hero,
.results-section {
  background: #ffffff;
  border: 1px solid #dbe4ee;
  border-radius: 18px;
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
}

.hero {
  padding: 2rem;
}

.hero h1,
.section-heading h2 {
  margin: 0;
  color: #102a43;
}

.hero p,
.section-heading p,
.chart-meta p,
.empty-state {
  color: #52606d;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  margin-top: 1.5rem;
}

.upload-section {
  flex: 1 1 320px;
}

.file-input {
  display: none;
}

.file-label-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.file-label {
  display: block;
  width: 100%;
  padding: 1rem 1.25rem;
  background: #f8fbff;
  color: #243b53;
  border: 2px dashed #bcccdc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-label.has-file {
  padding-right: 3rem;
  border-style: solid;
  border-color: #bcccdc;
  background: #f0f4f8;
}

.remove-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #9aa5b1;
  font-size: 1.2rem;
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  color: #e25c5c;
  background: #ffe3e3;
}

.file-label:hover {
  border-color: #42b883;
  background: #f2fffa;
}

.action-btn {
  border: none;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  background: linear-gradient(135deg, #42b883, #2f9e6f);
  color: #ffffff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(66, 184, 131, 0.22);
}

.action-btn:disabled {
  background: #9aa5b1;
  cursor: not-allowed;
}

.secondary-btn {
  background: #ffffff;
  color: #102a43;
  border: 1px solid #bcccdc;
}

.secondary-btn:hover:not(:disabled) {
  background: #f8fbff;
  border-color: #829ab1;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}

.status-box {
  margin-top: 1.5rem;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #d9e2ec;
}

.results-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: baseline;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.table-shell,
.fallback-image-card,
.chart-card {
  border: 1px solid #d9e2ec;
  border-radius: 16px;
  background: #fcfdff;
}

.table-shell {
  overflow: hidden;
}

.table-scroll {
  overflow-x: auto;
  padding: 1rem;
}

.fallback-image-card,
.chart-card {
  padding: 1rem;
}

.result-image,
.chart-image {
  width: 100%;
  display: block;
  border-radius: 12px;
  background: #ffffff;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 600px), 1fr));
  gap: 1.5rem;
}

.chart-meta h3 {
  margin: 0.85rem 0 0.25rem;
  font-size: 1rem;
  color: #102a43;
}

.chart-meta p {
  margin: 0;
  font-size: 0.9rem;
  word-break: break-word;
}

.clickable-chart {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.clickable-chart:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  position: relative;
  width: 80vw;
  height: 80vh;
  background: #ffffff;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.close-modal-btn {
  position: absolute;
  top: -16px;
  right: -16px;
  background: #ffffff;
  border: 1px solid #d9e2ec;
  color: #102a43;
  font-size: 1.2rem;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
  z-index: 1001;
}

.close-modal-btn:hover {
  background: #f8fbff;
  color: #e25c5c;
  transform: scale(1.1);
}

.enlarged-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.empty-state {
  margin: 0;
  padding: 1rem 0;
}

.is-loading {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
