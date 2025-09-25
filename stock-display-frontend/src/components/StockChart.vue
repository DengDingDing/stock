<template>
  <div class="card shadow-sm">
    <div class="card-header fw-bold">
      {{ stockStore.selectedStock.name }} ({{ stockStore.selectedStock.symbol }}) 价格走势
    </div>
    <div class="card-body">
      <Line v-if="stockStore.selectedStockData" :data="stockStore.selectedStockData" :options="chartOptions" :key="stockStore.selectedSymbol" />
    </div>
  </div>
</template>

<script setup>
import { useStockStore } from '../stores/stock'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
)

const stockStore = useStockStore()

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      ticks: {
        callback: function (value) {
          return '$' + value;
        },
      },
    },
  },
}
</script>

<style scoped>
.card-body {
  height: 400px;
}
</style>