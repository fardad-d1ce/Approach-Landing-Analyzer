<script setup>
import { onMounted, ref } from 'vue'

const API_BASE_URL = 'http://127.0.0.1:8000'

const statusMessage = ref('')
const isLoading = ref(false)
const selectedFile = ref(null)
const latestResults = ref(null)
const evaluationTableHtml = ref('')

const handleFileChange = (event) => {
  const file = event.target.files[0]
  selectedFile.value = file || null
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
  latestResults.value = results
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
          />
          <label for="csv-upload" class="file-label">
            {{ selectedFile ? selectedFile.name : 'Upload CSV (Optional)' }}
          </label>
        </div>

        <button @click="triggerAnalysis" :disabled="isLoading" class="action-btn">
          {{ isLoading ? 'Processing...' : (selectedFile ? 'Analyze Uploaded Data' : 'Run Analysis') }}
        </button>
      </div>

      <div v-if="statusMessage" class="status-box" :class="{ 'is-loading': isLoading }">
        {{ statusMessage }}
      </div>
    </section>

    <section v-if="latestResults" class="results-section">
      <div class="section-heading">
        <h2>Pilots Landing Evaluation</h2>
        <p>{{ latestResults.folder_name }}</p>
      </div>

      <div v-if="evaluationTableHtml" class="table-shell">
        <div class="table-scroll" v-html="evaluationTableHtml"></div>
      </div>
      <div v-else-if="latestResults.evaluation_table_image_url" class="fallback-image-card">
        <img
          :src="toApiUrl(latestResults.evaluation_table_image_url)"
          alt="Pilots landing evaluation table"
          class="result-image"
        />
      </div>
      <p v-else class="empty-state">No landing evaluation table was generated for this run.</p>
    </section>

    <section v-if="latestResults" class="results-section">
      <div class="section-heading">
        <h2>Pilots Landing Charts</h2>
        <p>{{ latestResults.landing_charts.length }} chart(s)</p>
      </div>

      <div v-if="latestResults.landing_charts.length" class="chart-grid">
        <article
          v-for="chart in latestResults.landing_charts"
          :key="chart.name"
          class="chart-card"
        >
          <img
            :src="toApiUrl(chart.url)"
            :alt="chart.title"
            class="chart-image"
            loading="lazy"
          />
          <div class="chart-meta">
            <h3>{{ chart.title }}</h3>
            <p>{{ chart.name }}</p>
          </div>
        </article>
      </div>
      <p v-else class="empty-state">No landing charts were generated for this run.</p>
    </section>
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
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
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
