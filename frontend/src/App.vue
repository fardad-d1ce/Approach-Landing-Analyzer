<script setup>
import { ref } from 'vue'

const statusMessage = ref('')
const isLoading = ref(false)
const selectedFile = ref(null)

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  } else {
    selectedFile.value = null
  }
}

const triggerAnalysis = async () => {
  isLoading.value = true
  statusMessage.value = 'Running analysis...'
  
  try {
    const formData = new FormData()
    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    }

    const response = await fetch('http://127.0.0.1:8000/analyze', {
      method: 'POST',
      body: selectedFile.value ? formData : null
    })
    const data = await response.json()
    
    if (data.status === 'success') {
      statusMessage.value = '✅ ' + data.message
    } else {
      statusMessage.value = '❌ Error: ' + data.message
    }
  } catch (error) {
    statusMessage.value = '❌ Failed to connect to the backend. Is the Python API running?'
    console.error(error)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="container">
    <h1>✈️ Approach & Landing Analyzer</h1>
    <p>Upload a CSV file or run analysis with the default dataset configured in <code>config.toml</code>.</p>
    
    <div class="upload-section">
      <input 
        type="file" 
        accept=".csv" 
        @change="handleFileChange" 
        class="file-input"
        id="csv-upload"
      />
      <label for="csv-upload" class="file-label">
        {{ selectedFile ? selectedFile.name : 'Upload CSV (Optional)' }}
      </label>
    </div>

    <button @click="triggerAnalysis" :disabled="isLoading" class="action-btn">
      {{ isLoading ? 'Processing...' : (selectedFile ? 'Analyze Uploaded Data' : 'Run Analysis') }}
    </button>

    <div v-if="statusMessage" class="status-box" :class="{ 'is-loading': isLoading }">
      {{ statusMessage }}
    </div>
  </main>
</template>

<style scoped>
.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  font-family: sans-serif;
  text-align: center;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.upload-section {
  margin: 2rem 0;
}

.file-input {
  display: none;
}

.file-label {
  display: inline-block;
  padding: 10px 20px;
  background-color: #f0f2f5;
  color: #2c3e50;
  border: 2px dashed #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.file-label:hover {
  border-color: #42b883;
  background-color: #f8fafc;
}

.action-btn {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 1.1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;
}

.action-btn:hover:not(:disabled) {
  background-color: #33a06f;
}

.action-btn:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

.status-box {
  margin-top: 2rem;
  padding: 1rem;
  border-radius: 4px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #333;
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
