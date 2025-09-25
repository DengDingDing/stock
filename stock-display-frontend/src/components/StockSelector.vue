<template>
  <div class="card shadow-sm">
    <div class="card-header fw-bold">股票列表</div>
    <div class="list-group list-group-flush">
      <a
        href="#"
        class="list-group-item list-group-item-action"
        v-for="stock in stockStore.stocks"
        :key="stock.symbol"
        :class="{ 'active': stock.symbol === stockStore.selectedSymbol }"
        @click.prevent="stockStore.selectStock(stock.symbol)"
      >
        <div class="d-flex w-100 justify-content-between">
          <h6 class="mb-1">{{ stock.name }}</h6>
          <small>{{ stock.symbol }}</small>
        </div>
      </a>
    </div>
  </div>
</template>

<script setup>
import { useStockStore } from '../stores/stock'

const stockStore = useStockStore()
</script>

<style scoped>
.list-group-item.active {
  background-color: #007bff;
  border-color: #007bff;
}
</style>
