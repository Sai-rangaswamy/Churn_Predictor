<template>
  <v-app>
    <v-main class="bg-background text-on-background">
      <v-container fluid class="pa-8">
        
        <!-- Header -->
        <v-row class="mb-6 align-center">
          <v-col class="d-flex align-center">
            <v-btn icon="mdi-arrow-left" variant="tonal" color="primary" class="mr-6" @click="$router.push('/')"></v-btn>
            <div>
              <h1 class="text-h3 font-weight-black text-primary d-flex align-center">
                <v-icon icon="mdi-chart-line-variant" size="48" class="mr-4" />
                Prediction Dashboard
              </h1>
              <p class="text-h6 mt-2 font-weight-regular" style="color: #263238;">
                Analyzing {{ customers.length }} records
              </p>
            </div>
          </v-col>
        </v-row>

        <!-- Dashboard Content -->
        <v-slide-y-transition>
          <div v-if="customers.length > 0" class="mt-4">

            <!-- KPI Cards -->
            <v-row>
              <v-col cols="12" sm="6" md="3" v-for="(card, i) in cards" :key="i">
                <v-card
                  @click="setFilter(card.value)"
                  :elevation="riskFilter === card.value ? 8 : 2"
                  :color="riskFilter === card.value ? card.bgColor : 'white'"
                  class="rounded-xl cursor-pointer transition-swing h-100"
                  :border="riskFilter === card.value ? false : `start lg ${card.color}`"
                >
                  <v-card-text class="d-flex flex-column align-center justify-center pa-6 h-100">
                    <div class="text-subtitle-1 font-weight-bold text-uppercase mb-2" :class="riskFilter === card.value ? 'text-white' : 'text-grey-darken-1'">
                      {{ card.title }}
                    </div>
                    <div class="text-h2 font-weight-black" :class="riskFilter === card.value ? 'text-white' : `text-${card.color}`">
                      {{ card.count }}
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- Charts -->
            <v-row class="mt-6">
              <v-col cols="12" md="5">
                <v-card elevation="2" class="rounded-xl h-100">
                  <v-card-title class="font-weight-bold pa-6 pb-0 text-h5">Risk Distribution</v-card-title>
                  <v-card-text class="d-flex justify-center align-center h-100 pa-6">
                    <div style="width: 100%; max-width: 320px;">
                      <Pie :data="chartData" />
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" md="7">
                <v-card elevation="2" class="rounded-xl h-100">
                  <v-card-title class="font-weight-bold pa-6 pb-0 text-h5">Probability Distribution</v-card-title>
                  <v-card-text class="pa-6">
                    <Bar :data="probabilityData" :options="barOptions" style="max-height: 300px" />
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- Table Section -->
            <v-card elevation="2" class="mt-8 rounded-xl overflow-hidden">
              <v-card-title class="d-flex align-center pa-6 bg-surface border-b">
                <v-icon icon="mdi-table" class="mr-3" color="primary" />
                <span class="text-h5 font-weight-bold" style="color: #263238;">Customer Details</span>
                <v-spacer />
                <v-text-field
                  v-model="searchInput"
                  prepend-inner-icon="mdi-magnify"
                  label="Search Customer ID"
                  variant="outlined"
                  density="compact"
                  hide-details
                  style="max-width: 350px;"
                  rounded="lg"
                />
              </v-card-title>

              <v-data-table
                :items="filteredCustomers"
                :headers="headers"
                :item-value="'Customer_ID'"
                hover
                @click:row="(_, r) => { selected = r.item; drawer = true }"
                class="bg-white"
                :items-per-page="10"
              >
                <!-- Probability Format -->
                <template v-slot:item.final_churn_probability="{ value }">
                  <span class="font-weight-bold text-grey-darken-3">
                    {{ (value * 100).toFixed(1) }}%
                  </span>
                </template>

                <!-- Risk Chip Format -->
                <template v-slot:item.Risk_Level="{ value }">
                  <v-chip
                    :color="getRiskColor(value)"
                    size="small"
                    class="font-weight-bold text-uppercase elevation-1"
                    variant="flat"
                  >
                    {{ value }}
                  </v-chip>
                </template>
              </v-data-table>
            </v-card>

          </div>
        </v-slide-y-transition>

        <!-- Details Drawer -->
        <v-navigation-drawer v-model="drawer" location="right" temporary width="450" class="elevation-10">
          <v-toolbar color="white" class="border-b" elevation="0">
            <v-toolbar-title class="font-weight-bold text-primary">Customer Insights</v-toolbar-title>
            <template v-slot:append>
              <v-btn icon="mdi-close" variant="text" @click="drawer = false" />
            </template>
          </v-toolbar>

          <div v-if="selected" class="pa-8">
            <div class="d-flex flex-column align-center mb-8">
              <v-avatar color="grey-lighten-4" size="100" class="mb-4 elevation-2">
                <v-icon icon="mdi-account-circle" size="64" color="grey-darken-1" />
              </v-avatar>
              <h2 class="text-h4 font-weight-black text-grey-darken-4">{{ selected.Customer_ID }}</h2>
              <v-chip :color="getRiskColor(selected.Risk_Level)" size="large" class="mt-4 font-weight-bold elevation-1" variant="flat">
                {{ selected.Risk_Level }}
              </v-chip>
            </div>

            <v-card variant="elevated" elevation="2" class="rounded-lg">
              <v-list lines="two" class="bg-grey-lighten-5">
                <v-list-item class="px-6 py-4">
                  <template v-slot:prepend>
                    <v-avatar color="primary-lighten-4" class="mr-4">
                      <v-icon icon="mdi-percent-outline" color="primary" />
                    </v-avatar>
                  </template>
                  <v-list-item-title class="font-weight-black text-h5 text-primary">
                    {{ (selected.final_churn_probability * 100).toFixed(1) }}%
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-subtitle-1 mt-1">Churn Probability</v-list-item-subtitle>
                </v-list-item>

                <v-divider />

                <v-list-item class="px-6 py-4">
                  <template v-slot:prepend>
                    <v-avatar color="warning-lighten-4" class="mr-4">
                      <v-icon icon="mdi-alert-decagram-outline" color="warning-darken-1" />
                    </v-avatar>
                  </template>
                  <v-list-item-title class="font-weight-bold text-h6 text-grey-darken-4 text-wrap">
                    {{ selected.Primary_Reason }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-subtitle-1 mt-1">Primary Driver of Risk</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card>
          </div>
        </v-navigation-drawer>
        


      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { Pie, Bar } from "vue-chartjs"
import {
  Chart,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from "chart.js"

Chart.register(
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
)

// State
const router = useRouter()
const customers = ref([])
const selected = ref(null)
const drawer = ref(false)
const searchInput = ref("")
const riskFilter = ref(null)

onMounted(() => {
  const saved = localStorage.getItem("churn_predictions")
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      customers.value = Array.isArray(parsed) ? parsed : []
    } catch(e) {
      console.error("Failed to parse local storage data")
      customers.value = []
    }
  } else {
    // If no data, send them back to upload page
    router.push("/")
  }
})

// Table Headers
const headers = [
  { title: 'Customer ID', key: 'Customer_ID', sortable: true, width: '25%' },
  { title: 'Churn Probability', key: 'final_churn_probability', sortable: true, width: '25%' },
  { title: 'Risk Level', key: 'Risk_Level', sortable: true, width: '25%' },
  { title: 'Primary Risk Factor', key: 'Primary_Reason', sortable: true, width: '25%' }
]

// Methods
function getRiskColor(level) {
  if (level === 'High Risk') return 'error'
  if (level === 'Medium Risk') return 'warning'
  if (level === 'Low Risk') return 'success'
  return 'grey'
}

function setFilter(v) {
  riskFilter.value = riskFilter.value === v ? null : v
}

// Computed
const high = computed(() => customers.value.filter(x => x.Risk_Level === "High Risk").length)
const medium = computed(() => customers.value.filter(x => x.Risk_Level === "Medium Risk").length)
const low = computed(() => customers.value.filter(x => x.Risk_Level === "Low Risk").length)

const cards = computed(() => [
  { title: "Total Analyzed", count: customers.value.length, value: null, color: "primary", bgColor: "primary" },
  { title: "High Risk", count: high.value, value: "High Risk", color: "primary", bgColor: "primary" },
  { title: "Medium Risk", count: medium.value, value: "Medium Risk", color: "primary", bgColor: "primary" },
  { title: "Low Risk", count: low.value, value: "Low Risk", color: "primary", bgColor: "primary" }
])

const filteredCustomers = computed(() => {
  return customers.value.filter(c => {
    const matchSearch = c.Customer_ID.toLowerCase().includes(searchInput.value.toLowerCase())
    const matchRisk = riskFilter.value ? c.Risk_Level === riskFilter.value : true
    return matchSearch && matchRisk
  })
})

// Charts Data
const chartData = computed(() => ({
  labels: ["High", "Medium", "Low"],
  datasets: [{
    data: [high.value, medium.value, low.value],
    backgroundColor: ["#303F9F", "#00897B", "#B0BEC5"], // Primary, Secondary, Neutral
    borderWidth: 0,
    hoverOffset: 8
  }]
}))

const probabilityData = computed(() => {
  const buckets = { "0–20": 0, "20–40": 0, "40–60": 0, "60–80": 0, "80–100": 0 }
  customers.value.forEach(c => {
    const p = c.final_churn_probability * 100
    if (p < 20) buckets["0–20"]++
    else if (p < 40) buckets["20–40"]++
    else if (p < 60) buckets["40–60"]++
    else if (p < 80) buckets["60–80"]++
    else buckets["80–100"]++
  })
  return {
    labels: Object.keys(buckets),
    datasets: [{
      label: "Customers",
      data: Object.values(buckets),
      backgroundColor: ["#303F9F"], // All bars use Primary color
      borderRadius: 6
    }]
  }
})

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (ctx) => `Probability: ${ctx[0].label}%`,
        label: (ctx) => `${ctx.raw} customers`
      }
    }
  },
  scales: {
    x: { 
      grid: { display: false },
      ticks: { color: '#263238' },
      title: { display: true, text: "Churn Probability Range (%)", color: '#263238', font: { weight: 'bold' } }
    },
    y: { 
      beginAtZero: true,
      border: { display: false },
      ticks: { color: '#263238' },
      title: { display: true, text: "Number of Customers", color: '#263238', font: { weight: 'bold' } }
    }
  }
}

</script>

<style>
/* Optional: Make the scrollbar a bit nicer */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1; 
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8; 
}
</style>