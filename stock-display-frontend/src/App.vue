<template>
  <div id="app">
    <Header />
    <main class="container-fluid mt-4">
      <div class="row">
        <div class="col-lg-3 col-md-4">
          <StockSelector />
        </div>
        <div class="col-lg-9 col-md-8">
          <StockChart />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import Header from './components/Header.vue'
import StockSelector from './components/StockSelector.vue'
import StockChart from './components/StockChart.vue'
</script>

<style>
body {
  background-color: #f0f2f5;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.container-fluid {
  padding-left: 30px;
  padding-right: 30px;
}
</style>
