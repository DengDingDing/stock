import { defineStore } from 'pinia'

const generateRandomData = () => {
  const data = []
  for (let i = 0; i < 7; i++) {
    data.push(Math.floor(Math.random() * (100 - 40 + 1)) + 40)
  }
  return data
}

export const useStockStore = defineStore('stock', {
  state: () => ({
    stocks: [
      { name: '苹果', symbol: 'AAPL' },
      { name: '谷歌', symbol: 'GOOGL' },
      { name: '微软', symbol: 'MSFT' },
      { name: '亚马逊', symbol: 'AMZN' },
      { name: 'Facebook', symbol: 'META' },
    ],
    selectedSymbol: 'AAPL',
    stockData: {
      'AAPL': {
        labels: ['一月', '二月', '三月', '四月', '五月', '六月', '七月'],
        datasets: [{
          label: '苹果 (AAPL)',
          backgroundColor: '#007bff',
          borderColor: '#007bff',
          data: generateRandomData(),
          tension: 0.1
        }]
      },
      'GOOGL': {
        labels: ['一月', '二月', '三月', '四月', '五月', '六月', '七月'],
        datasets: [{
          label: '谷歌 (GOOGL)',
          backgroundColor: '#28a745',
          borderColor: '#28a745',
          data: generateRandomData(),
          tension: 0.1
        }]
      },
      'MSFT': {
        labels: ['一月', '二月', '三月', '四月', '五月', '六月', '七月'],
        datasets: [{
          label: '微软 (MSFT)',
          backgroundColor: '#dc3545',
          borderColor: '#dc3545',
          data: generateRandomData(),
          tension: 0.1
        }]
      },
      'AMZN': {
        labels: ['一月', '二月', '三月', '四月', '五月', '六月', '七月'],
        datasets: [{
          label: '亚马逊 (AMZN)',
          backgroundColor: '#ffc107',
          borderColor: '#ffc107',
          data: generateRandomData(),
          tension: 0.1
        }]
      },
      'META': {
        labels: ['一月', '二月', '三月', '四月', '五月', '六月', '七月'],
        datasets: [{
          label: 'Facebook (META)',
          backgroundColor: '#17a2b8',
          borderColor: '#17a2b8',
          data: generateRandomData(),
          tension: 0.1
        }]
      }
    }
  }),
  getters: {
    selectedStockData: (state) => {
      return state.stockData[state.selectedSymbol]
    },
    selectedStock: (state) => {
        return state.stocks.find(s => s.symbol === state.selectedSymbol)
    }
  },
  actions: {
    selectStock(symbol) {
      this.selectedSymbol = symbol
    }
  }
})
