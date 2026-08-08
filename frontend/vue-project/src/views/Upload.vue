<template>
  <v-app>
    <v-main class="bg-background text-on-background">
      <v-container fluid class="pa-8 d-flex flex-column" style="min-height: 100vh;">
        
        <!-- Header -->
        <v-row class="flex-grow-0 mb-12 mt-8" justify="center">
          <v-col cols="12" md="10" lg="8" class="text-center">
            <h1 class="text-h2 font-weight-black text-primary d-flex align-center justify-center">
              <v-icon icon="mdi-chart-line-variant" size="64" class="mr-4" />
              Churn Intelligence Platform
            </h1>
            <p class="text-h5 mt-6 font-weight-regular" style="color: #263238;">
              Predict customer churn and continuously improve model performance via the MLOps feedback loop.
            </p>
          </v-col>
        </v-row>

        <!-- Actions -->
        <v-row justify="center" class="flex-grow-1">
          <!-- Prediction Upload -->
          <v-col cols="12" md="5" lg="4">
            <v-card elevation="4" class="h-100 rounded-xl" border="start xl primary">
              <v-card-item class="pa-8">
                <template v-slot:prepend>
                  <v-avatar color="primary-lighten-5" size="64" class="mr-4">
                    <v-icon color="primary" size="36" icon="mdi-cloud-upload" />
                  </v-avatar>
                </template>
                <v-card-title class="text-h4 font-weight-bold">Run Predictions</v-card-title>
                <v-card-subtitle class="text-h6 mt-2">Upload current customer metrics CSV</v-card-subtitle>
              </v-card-item>
              <v-card-text class="px-8 pb-8 mt-4">
                <v-file-input
                  label="Select Customer Data (.csv)"
                  accept=".csv"
                  variant="outlined"
                  density="comfortable"
                  prepend-icon=""
                  prepend-inner-icon="mdi-file-delimited"
                  @update:model-value="upload"
                  color="primary"
                  hide-details
                  class="mb-4"
                />
                <v-btn v-if="loadingPredictions" loading block color="primary" size="x-large" class="rounded-lg mt-4">Analyzing...</v-btn>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Feedback Upload -->
          <v-col cols="12" md="5" lg="4">
            <v-card elevation="4" class="h-100 rounded-xl" border="start xl secondary">
              <v-card-item class="pa-8">
                <template v-slot:prepend>
                  <v-avatar color="secondary-lighten-5" size="64" class="mr-4">
                    <v-icon color="secondary" size="36" icon="mdi-database-sync" />
                  </v-avatar>
                </template>
                <v-card-title class="text-h4 font-weight-bold">MLOps Feedback</v-card-title>
                <v-card-subtitle class="text-h6 mt-2">Upload actual outcomes to retrain model</v-card-subtitle>
              </v-card-item>
              <v-card-text class="px-8 pb-8 mt-4">
                <v-file-input
                  v-model="feedbackFile"
                  label="Select Actual Outcomes (.csv)"
                  accept=".csv"
                  variant="outlined"
                  density="comfortable"
                  prepend-icon=""
                  prepend-inner-icon="mdi-file-check"
                  color="secondary"
                  hide-details
                  class="mb-4"
                />
                <v-btn
                  color="secondary"
                  size="x-large"
                  block
                  class="rounded-lg mt-4 font-weight-bold"
                  @click="submitFeedback"
                  :disabled="!feedbackFile"
                  :loading="loadingFeedback"
                  elevation="2"
                >
                  Submit Outcomes
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Snackbar for feedback -->
        <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="4000" location="bottom center" elevation="24">
          <div class="d-flex align-center">
            <v-icon :icon="snackbar.color === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle'" class="mr-3" />
            <span class="text-h6 font-weight-medium">{{ snackbar.text }}</span>
          </div>
        </v-snackbar>

      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const feedbackFile = ref(null)
const snackbar = ref({ show: false, text: "", color: "success" })
const loadingPredictions = ref(false)
const loadingFeedback = ref(false)

function showSnackbar(text, color = 'success') {
  snackbar.value = { show: true, text, color }
}

async function upload(file) {
  if (!file) return

  loadingPredictions.value = true

  const formData = new FormData()

  formData.append(
    "file",
    Array.isArray(file)
      ? file[0]
      : file
  )

  try {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000"
    const res = await axios.post(
      `${apiUrl}/predict`,
      formData,
      {
        headers: {
          "Content-Type":
            "multipart/form-data"
        }
      }
    )

    console.log("Response:", res.data)

    localStorage.setItem(
      "churn_predictions",
      JSON.stringify(res.data)
    )

    router.push("/dashboard")

  } catch (err) {
    console.error(err)

    showSnackbar(
      "Failed to run predictions",
      "error"
    )

  } finally {
    loadingPredictions.value = false
  }
}

async function submitFeedback() {
  if (!feedbackFile.value) return
  loadingFeedback.value = true
  try {
    const data = new FormData()
    data.append("file", feedbackFile.value)
    const apiUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000"
    const res = await axios.post(`${apiUrl}/feedback`, data)
    let msg = `Feedback processed! ${res.data.matched_customers || 0} records matched. Total labeled: ${res.data.total_labeled}`
    if (res.data.retrained) {
      msg += ` Model was retrained successfully!`
    }
    showSnackbar(msg, "success")
    feedbackFile.value = null
  } catch (e) {
    showSnackbar(e.response?.data?.error || "Error submitting feedback.", "error")
  } finally {
    loadingFeedback.value = false
  }
}
</script>
