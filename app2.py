from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import uvicorn

app = FastAPI(title="股票K线图分析系统", description="基于FastAPI的实时股票数据分析")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求模型
class KlineRequest(BaseModel):
    stockCode: str = "sh.600000"
    frequency: str = "d"
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class StockSearchResponse(BaseModel):
    success: bool
    data: List[dict] = []
    error: Optional[str] = None


class KlineResponse(BaseModel):
    success: bool
    data: List[dict] = []
    stockCode: Optional[str] = None
    frequency: Optional[str] = None
    error: Optional[str] = None


# HTML内容 - 修改为显示高亮点数据
HTML_CONTENT = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票K线图分析系统</title>
    <script src="https://cdn.jsdelivr.net/npm/vue@3.2.0/dist/vue.global.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.0/dist/echarts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios@1.0.0/dist/axios.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .control-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }

        .control-item {
            display: flex;
            flex-direction: column;
            min-width: 150px;
            position: relative;
        }

        label {
            font-weight: bold;
            margin-bottom: 5px;
            color: #555;
        }

        input, select, button {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }

        button {
            background: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }

        button:hover {
            background: #45a049;
        }

        button:disabled {
            background: #cccccc;
            cursor: not-allowed;
        }

        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            min-height: 600px;
            position: relative;
        }

        #chart {
            width: 100%;
            height: 500px;
        }

        .chart-controls {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
        }

        .chart-control-btn {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .chart-control-btn:hover {
            background: #f0f0f0;
            transform: scale(1.1);
        }

        .chart-control-btn:active {
            transform: scale(0.95);
        }

        .zoom-info {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            border: 1px solid #ddd;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }

        .stock2-info {
            background: white;
            padding: 15px;
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .stock2-info.highlighted {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 2px solid #ffc107;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 5px;
            transition: all 0.3s ease;
        }

        .info-item.highlight {
            background: #e7f3ff;
            border-left: 4px solid #007bff;
        }

        .price-up {
            color: #e74c3c;
            font-weight: bold;
        }

        .price-down {
            color: #2ecc71;
            font-weight: bold;
        }

        .loading {
            text-align: center;
            padding: 20px;
            font-size: 18px;
            color: #666;
        }

        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }

        .search-results {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .search-item {
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
        }

        .search-item:hover {
            background: #f5f5f5;
        }

        .empty-data {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 16px;
        }

        .current-stock2 {
            margin-top: 5px;
            font-size: 12px;
            color: #666;
        }

        .search-input-container {
            position: relative;
        }

        .clear-search {
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #999;
            cursor: pointer;
            font-size: 16px;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .clear-search:hover {
            color: #666;
        }

        .keyboard-shortcuts {
            margin-top: 10px;
            font-size: 12px;
            color: #666;
        }

        .shortcut-item {
            display: inline-block;
            margin-right: 15px;
        }

        .shortcut-key {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            border: 1px solid #ddd;
            font-family: monospace;
        }

        .hint-text {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 10px;
            font-style: italic;
        }

        .data-highlight {
            background: #fff3cd;
            padding: 3px 6px;
            border-radius: 3px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="container">
            <div class="header">
                <h1>股票K线图分析系统 - FastAPI</h1>
                <p>基于Python量化分析技术的实时股票数据展示</p>
            </div>

            <div class="controls">
                <div class="control-group">
                    <div class="control-item">
                        <label for="stockSearch">股票搜索:</label>
                        <div class="search-input-container">
                            <input type="text" id="stockSearch" v-model="searchKeyword" 
                                   @input="searchStocks" placeholder="输入股票名称或代码" 
                                   @blur="onSearchBlur" @focus="onSearchFocus">
                            <button class="clear-search" @click="clearSearch" v-if="searchKeyword">×</button>
                        </div>
                        <div class="search-results" v-if="showSearchResults">
                            <div class="search-item" v-for="stock2 in searchResults" 
                                 @click="selectStock(stock2)" @mousedown.prevent>
                                <strong>{{ stock2.name }}</strong> ({{ stock2.code }})
                            </div>
                        </div>
                        <div class="current-stock2" v-if="stockName">
                            当前: {{ stockName }} ({{ stockCode }})
                        </div>
                    </div>

                    <div class="control-item">
                        <label for="frequency">时间周期:</label>
                        <select id="frequency" v-model="frequency">
                            <option value="5">5分钟</option>
                            <option value="15">15分钟</option>
                            <option value="30">30分钟</option>
                            <option value="60">60分钟</option>
                            <option value="d">日线</option>
                            <option value="w">周线</option>
                            <option value="m">月线</option>
                        </select>
                    </div>

                    <div class="control-item">
                        <label for="startDate">开始日期:</label>
                        <input type="date" id="startDate" v-model="startDate">
                    </div>

                    <div class="control-item">
                        <label for="endDate">结束日期:</label>
                        <input type="date" id="endDate" v-model="endDate">
                    </div>

                    <div class="control-item">
                        <label>&nbsp;</label>
                        <button @click="loadData" :disabled="loading">
                            <span v-if="loading">加载中...</span>
                            <span v-else>加载数据</span>
                        </button>
                    </div>
                </div>
            </div>

            <div class="error" v-if="error">
                {{ error }}
            </div>

            <div class="loading" v-if="loading">
                数据加载中...
            </div>

            <div class="chart-container">
                <div class="zoom-info" v-if="zoomLevel !== 100">
                    缩放: {{ zoomLevel }}%
                </div>
                <div id="chart"></div>
                <div class="empty-data" v-if="!hasData && !loading && !error">
                    暂无数据，请选择股票和时间周期后点击"加载数据"
                </div>
            </div>

            <div class="stock2-info" :class="{ 'highlighted': isHighlighted }" v-if="hasData && !loading">
                <h3>
                    <span v-if="isHighlighted" class="data-highlight">📊 当前高亮数据</span>
                    <span v-else>📈 最新数据</span>
                    ({{ currentData.date }})
                </h3>
                <div class="hint-text" v-if="!isHighlighted">
                    👆 鼠标悬停在K线图上查看具体时间点的数据
                </div>
                <div class="info-grid">
                    <div class="info-item" :class="{ 'highlight': isHighlighted }">
                        <span>开盘价:</span>
                        <span :class="getPriceClass(currentData.open, currentData.close)">
                            {{ formatPrice(currentData.open) }}
                        </span>
                    </div>
                    <div class="info-item" :class="{ 'highlight': isHighlighted }">
                        <span>收盘价:</span>
                        <span :class="getPriceClass(currentData.close, currentData.open)">
                            {{ formatPrice(currentData.close) }}
                        </span>
                    </div>
                    <div class="info-item" :class="{ 'highlight': isHighlighted }">
                        <span>最高价:</span>
                        <span>{{ formatPrice(currentData.high) }}</span>
                    </div>
                    <div class="info-item" :class="{ 'highlight': isHighlighted }">
                        <span>最低价:</span>
                        <span>{{ formatPrice(currentData.low) }}</span>
                    </div>
                    <div class="info-item" :class="{ 'highlight': isHighlighted }">
                        <span>成交量:</span>
                        <span>{{ formatVolume(currentData.volume) }}</span>
                    </div>
                    <div class="info-item" :class="{ 'highlight': isHighlighted }" v-if="currentData.pctChg !== undefined">
                        <span>涨跌幅:</span>
                        <span :class="currentData.pctChg >= 0 ? 'price-up' : 'price-down'">
                            {{ currentData.pctChg !== undefined ? currentData.pctChg.toFixed(2) + '%' : '--' }}
                        </span>
                    </div>
                    <div class="info-item" :class="{ 'highlight': isHighlighted }" v-if="currentData.turn !== undefined">
                        <span>换手率:</span>
                        <span>{{ currentData.turn !== undefined ? currentData.turn.toFixed(2) + '%' : '--' }}</span>
                    </div>
                    <div class="info-item" :class="{ 'highlight': isHighlighted }">
                        <span>成交额:</span>
                        <span>{{ formatAmount(currentData.amount) }}</span>
                    </div>
                </div>
                <div class="hint-text" v-if="isHighlighted">
                    ✨ 正在显示鼠标悬停位置的数据
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp } = Vue;

        createApp({
            data() {
                return {
                    stockCode: 'sh.600000',
                    stockName: '浦发银行',
                    frequency: 'd',
                    startDate: this.getDefaultDate(-90),
                    endDate: this.getDefaultDate(0),
                    klineData: [],
                    currentData: {},
                    loading: false,
                    error: null,
                    chart: null,
                    searchKeyword: '',
                    searchResults: [],
                    searchTimer: null,
                    showSearchResults: false,
                    zoomLevel: 100,
                    dataZoomStart: 0,
                    dataZoomEnd: 100,
                    isDragging: false,
                    dragStartX: 0,
                    currentStart: 0,
                    isHighlighted: false,
                    highlightTimer: null
                };
            },
            computed: {
                hasData() {
                    return this.klineData.length > 0;
                },
                visibleDataCount() {
                    if (!this.klineData.length) return 0;
                    const total = this.klineData.length;
                    const visible = Math.round(total * (this.dataZoomEnd - this.dataZoomStart) / 100);
                    return visible;
                }
            },
            mounted() {
                console.log('组件挂载完成');
                this.initChart();
                this.bindKeyboardEvents();
            },
            beforeUnmount() {
                this.unbindKeyboardEvents();
            },
            methods: {
                getDefaultDate(daysOffset) {
                    const date = new Date();
                    date.setDate(date.getDate() + daysOffset);
                    return date.toISOString().split('T')[0];
                },

                initChart() {
                    console.log('初始化图表...');
                    const chartDom = document.getElementById('chart');
                    if (chartDom && typeof echarts !== 'undefined') {
                        try {
                            this.chart = echarts.init(chartDom);
                            console.log('图表初始化成功');

                            // 窗口大小变化时重绘图表
                            window.addEventListener('resize', () => {
                                if (this.chart) {
                                    this.chart.resize();
                                }
                            });

                            // 绑定鼠标滚轮事件
                            this.bindMouseWheel(chartDom);

                            // 绑定拖拽事件
                            this.bindDragEvents(chartDom);

                            // 绑定图表事件
                            this.bindChartEvents();

                            // 初始显示空图表
                            this.chart.setOption({
                                title: {
                                    text: '请选择股票并加载数据',
                                    left: 'center',
                                    top: 'center',
                                    textStyle: {
                                        fontSize: 16,
                                        color: '#999'
                                    }
                                }
                            });

                        } catch (error) {
                            console.error('图表初始化失败:', error);
                        }
                    } else {
                        console.error('图表容器或ECharts未找到');
                    }
                },

                bindChartEvents() {
                    if (!this.chart) return;

                    // 鼠标悬停事件
                    this.chart.on('mouseover', (params) => {
                        if (params.componentType === 'series' && params.seriesType === 'candlestick') {
                            this.updateHighlightedData(params.dataIndex);
                        }
                    });

                    // 鼠标移动事件（用于更精确的跟踪）
                    this.chart.on('globalout', () => {
                        this.clearHighlight();
                    });

                    // 点击事件也可以触发高亮
                    this.chart.on('click', (params) => {
                        if (params.componentType === 'series' && params.seriesType === 'candlestick') {
                            this.updateHighlightedData(params.dataIndex);
                        }
                    });
                },

                updateHighlightedData(dataIndex) {
                    if (this.highlightTimer) {
                        clearTimeout(this.highlightTimer);
                    }

                    // 添加轻微延迟，避免频繁更新
                    this.highlightTimer = setTimeout(() => {
                        if (dataIndex >= 0 && dataIndex < this.klineData.length) {
                            this.currentData = { ...this.klineData[dataIndex] };
                            this.isHighlighted = true;
                        }
                    }, 50);
                },

                clearHighlight() {
                    if (this.highlightTimer) {
                        clearTimeout(this.highlightTimer);
                    }

                    // 延迟清除高亮，避免闪烁
                    this.highlightTimer = setTimeout(() => {
                        if (this.klineData.length > 0) {
                            // 恢复到显示最新数据
                            this.currentData = { ...this.klineData[this.klineData.length - 1] };
                            this.isHighlighted = false;
                        }
                    }, 300);
                },

                bindMouseWheel(chartDom) {
                    chartDom.addEventListener('wheel', (e) => {
                        if (!this.hasData) return;

                        e.preventDefault();
                        const delta = e.deltaY;

                        if (delta < 0) {
                            // 滚轮向上 - 放大
                            this.zoomIn();
                        } else {
                            // 滚轮向下 - 缩小
                            this.zoomOut();
                        }
                    }, { passive: false });
                },

                bindDragEvents(chartDom) {
                    chartDom.addEventListener('mousedown', (e) => {
                        if (!this.hasData) return;

                        this.isDragging = true;
                        this.dragStartX = e.clientX;
                        this.currentStart = this.dataZoomStart;
                        chartDom.style.cursor = 'grabbing';
                    });

                    document.addEventListener('mousemove', (e) => {
                        if (!this.isDragging || !this.hasData) return;

                        const deltaX = e.clientX - this.dragStartX;
                        const totalWidth = chartDom.offsetWidth;
                        const movePercent = (deltaX / totalWidth) * 100;

                        // 计算新的起始位置
                        let newStart = this.currentStart - movePercent;
                        newStart = Math.max(0, Math.min(newStart, 100 - (this.dataZoomEnd - this.dataZoomStart)));

                        if (newStart !== this.dataZoomStart) {
                            this.dataZoomStart = newStart;
                            this.dataZoomEnd = newStart + (this.dataZoomEnd - this.dataZoomStart);
                            this.applyDataZoom();
                        }
                    });

                    document.addEventListener('mouseup', () => {
                        if (this.isDragging) {
                            this.isDragging = false;
                            chartDom.style.cursor = 'default';
                        }
                    });
                },

                bindKeyboardEvents() {
                    document.addEventListener('keydown', this.handleKeyDown);
                },

                unbindKeyboardEvents() {
                    document.removeEventListener('keydown', this.handleKeyDown);
                },

                handleKeyDown(e) {
                    if (!this.hasData) return;

                    switch(e.key) {
                        case '+':
                        case '=':
                            e.preventDefault();
                            this.zoomIn();
                            break;
                        case '-':
                        case '_':
                            e.preventDefault();
                            this.zoomOut();
                            break;
                        case 'ArrowLeft':
                            e.preventDefault();
                            this.moveLeft();
                            break;
                        case 'ArrowRight':
                            e.preventDefault();
                            this.moveRight();
                            break;
                        case '0':
                            e.preventDefault();
                            this.resetZoom();
                            break;
                    }
                },

                zoomIn() {
                    if (!this.hasData) return;

                    const zoomFactor = 0.8; // 缩小显示范围，相当于放大
                    const currentRange = this.dataZoomEnd - this.dataZoomStart;
                    const newRange = currentRange * zoomFactor;
                    const center = (this.dataZoomStart + this.dataZoomEnd) / 2;

                    this.dataZoomStart = Math.max(0, center - newRange / 2);
                    this.dataZoomEnd = Math.min(100, center + newRange / 2);

                    this.applyDataZoom();
                    this.updateZoomLevel();
                },

                zoomOut() {
                    if (!this.hasData) return;

                    const zoomFactor = 1.2; // 扩大显示范围，相当于缩小
                    const currentRange = this.dataZoomEnd - this.dataZoomStart;
                    const newRange = Math.min(100, currentRange * zoomFactor);
                    const center = (this.dataZoomStart + this.dataZoomEnd) / 2;

                    this.dataZoomStart = Math.max(0, center - newRange / 2);
                    this.dataZoomEnd = Math.min(100, center + newRange / 2);

                    this.applyDataZoom();
                    this.updateZoomLevel();
                },

                moveLeft() {
                    if (!this.hasData) return;

                    const moveStep = 10; // 移动步长百分比
                    const newStart = Math.max(0, this.dataZoomStart - moveStep);
                    const range = this.dataZoomEnd - this.dataZoomStart;

                    this.dataZoomStart = newStart;
                    this.dataZoomEnd = newStart + range;

                    this.applyDataZoom();
                },

                moveRight() {
                    if (!this.hasData) return;

                    const moveStep = 10; // 移动步长百分比
                    const range = this.dataZoomEnd - this.dataZoomStart;
                    const newEnd = Math.min(100, this.dataZoomEnd + moveStep);

                    this.dataZoomEnd = newEnd;
                    this.dataZoomStart = newEnd - range;

                    this.applyDataZoom();
                },

                resetZoom() {
                    this.dataZoomStart = 0;
                    this.dataZoomEnd = 100;
                    this.zoomLevel = 100;
                    this.applyDataZoom();
                },

                applyDataZoom() {
                    if (!this.chart) return;

                    this.chart.setOption({
                        dataZoom: [
                            {
                                start: this.dataZoomStart,
                                end: this.dataZoomEnd
                            },
                            {
                                start: this.dataZoomStart,
                                end: this.dataZoomEnd
                            }
                        ]
                    });
                },

                updateZoomLevel() {
                    const visiblePercent = this.dataZoomEnd - this.dataZoomStart;
                    this.zoomLevel = Math.round((100 / visiblePercent) * 100);
                },

                async loadData() {
                    if (!this.stockCode) {
                        this.error = '请先选择股票';
                        return;
                    }

                    this.loading = true;
                    this.error = null;

                    try {
                        console.log('开始加载数据...');
                        const response = await axios.post('/api/stock2/kline', {
                            stockCode: this.stockCode,
                            frequency: this.frequency,
                            startDate: this.startDate,
                            endDate: this.endDate
                        });

                        console.log('API响应:', response.data);

                        if (response.data.success) {
                            this.klineData = response.data.data;
                            if (this.klineData.length > 0) {
                                // 初始化显示最新数据
                                this.currentData = { ...this.klineData[this.klineData.length - 1] };
                                this.isHighlighted = false;
                                this.resetZoom(); // 重置缩放状态
                                this.updateChart();
                            } else {
                                this.error = '没有获取到数据';
                                this.clearChart();
                            }
                        } else {
                            this.error = response.data.error || '获取数据失败';
                            this.clearChart();
                        }
                    } catch (err) {
                        this.error = '加载数据失败: ' + err.message;
                        console.error('API请求错误:', err);
                        this.clearChart();
                    } finally {
                        this.loading = false;
                    }
                },

                clearChart() {
                    if (this.chart) {
                        this.chart.setOption({
                            title: {
                                text: '数据加载失败或暂无数据',
                                left: 'center',
                                top: 'center',
                                textStyle: {
                                    fontSize: 16,
                                    color: '#999'
                                }
                            }
                        });
                    }
                    this.klineData = [];
                    this.currentData = {};
                    this.zoomLevel = 100;
                    this.isHighlighted = false;
                },

                updateChart() {
                    if (!this.chart || this.klineData.length === 0) {
                        console.error('图表未初始化或数据为空');
                        return;
                    }

                    try {
                        // 处理日期显示
                        const dates = this.klineData.map(item => {
                            const dateStr = item.date;
                            if (['5', '15', '30', '60'].includes(this.frequency)) {
                                // 分钟数据：显示时间
                                if (dateStr.includes(' ')) {
                                    return dateStr.split(' ')[1].substr(0, 5); // HH:MM
                                }
                                return dateStr.substr(11, 5);
                            } else {
                                // 日、周、月数据：显示日期
                                if (dateStr.includes(' ')) {
                                    return dateStr.split(' ')[0]; // YYYY-MM-DD
                                }
                                return dateStr;
                            }
                        });

                        // K线数据
                        const klineValues = this.klineData.map(item => [
                            parseFloat(item.open) || 0,
                            parseFloat(item.close) || 0,
                            parseFloat(item.low) || 0,
                            parseFloat(item.high) || 0
                        ]);

                        // 成交量数据
                        const volumes = this.klineData.map(item => parseFloat(item.volume) || 0);

                        // 创建图表配置
                        const option = {
                            animation: true,
                            title: {
                                text: `${this.stockName} (${this.stockCode}) ${this.getFrequencyText()}K线图`,
                                left: 'center',
                                textStyle: {
                                    fontSize: 16,
                                    fontWeight: 'bold'
                                }
                            },
                            tooltip: {
                                trigger: 'axis',
                                axisPointer: {
                                    type: 'cross',
                                    label: {
                                        backgroundColor: '#6a7985'
                                    }
                                },
                                formatter: (params) => {
                                    const dataIndex = params[0].dataIndex;
                                    const item = this.klineData[dataIndex];
                                    let html = `<div style="font-weight: bold; margin-bottom: 5px;">${item.date}</div>`;
                                    html += `<div>开盘: ${this.formatPrice(item.open)}</div>`;
                                    html += `<div>收盘: ${this.formatPrice(item.close)}</div>`;
                                    html += `<div>最高: ${this.formatPrice(item.high)}</div>`;
                                    html += `<div>最低: ${this.formatPrice(item.low)}</div>`;
                                    html += `<div>成交量: ${this.formatVolume(item.volume)}</div>`;
                                    if (item.amount > 0) {
                                        html += `<div>成交额: ${this.formatAmount(item.amount)}</div>`;
                                    }
                                    if (item.pctChg !== undefined) {
                                        const color = item.pctChg >= 0 ? '#e74c3c' : '#2ecc71';
                                        html += `<div>涨跌幅: <span style="color:${color}">${item.pctChg.toFixed(2)}%</span></div>`;
                                    }
                                    return html;
                                }
                            },
                            legend: {
                                data: ['K线', '成交量'],
                                top: 30
                            },
                            grid: [
                                {
                                    left: '50px',
                                    right: '50px',
                                    bottom: '100px',
                                    height: '60%'
                                },
                                {
                                    left: '50px',
                                    right: '50px',
                                    bottom: '30px',
                                    height: '20%'
                                }
                            ],
                            xAxis: [
                                {
                                    type: 'category',
                                    data: dates,
                                    scale: true,
                                    boundaryGap: false,
                                    axisLine: { onZero: false },
                                    splitLine: { show: false },
                                    splitNumber: 20,
                                    min: 'dataMin',
                                    max: 'dataMax'
                                },
                                {
                                    type: 'category',
                                    gridIndex: 1,
                                    data: dates,
                                    scale: true,
                                    boundaryGap: false,
                                    axisLine: { onZero: false },
                                    axisTick: { show: false },
                                    splitLine: { show: false },
                                    axisLabel: { show: false },
                                    splitNumber: 20,
                                    min: 'dataMin',
                                    max: 'dataMax'
                                }
                            ],
                            yAxis: [
                                {
                                    scale: true,
                                    splitArea: {
                                        show: true
                                    }
                                },
                                {
                                    scale: true,
                                    gridIndex: 1,
                                    splitNumber: 2,
                                    axisLabel: { show: false },
                                    axisLine: { show: false },
                                    axisTick: { show: false },
                                    splitLine: { show: false }
                                }
                            ],
                            dataZoom: [
                                {
                                    type: 'inside',
                                    xAxisIndex: [0, 1],
                                    start: this.dataZoomStart,
                                    end: this.dataZoomEnd,
                                    zoomOnMouseWheel: false,  // 禁用默认滚轮缩放，使用自定义
                                    moveOnMouseMove: true,
                                    moveOnMouseWheel: false
                                },
                                {
                                    show: true,
                                    xAxisIndex: [0, 1],
                                    type: 'slider',
                                    bottom: 10,
                                    start: this.dataZoomStart,
                                    end: this.dataZoomEnd,
                                    height: 20,
                                    brushSelect: false,
                                    fillerColor: 'rgba(67,128,226,0.2)',
                                    borderColor: '#ddd',
                                    handleStyle: {
                                        color: '#4380e2'
                                    }
                                }
                            ],
                            series: [
                                {
                                    name: 'K线',
                                    type: 'candlestick',
                                    data: klineValues,
                                    itemStyle: {
                                        color: '#ef232a',
                                        color0: '#14b143',
                                        borderColor: '#ef232a',
                                        borderColor0: '#14b143'
                                    },
                                    emphasis: {
                                        itemStyle: {
                                            borderWidth: 2,
                                            shadowBlur: 10,
                                            shadowColor: 'rgba(0, 0, 0, 0.3)'
                                        }
                                    }
                                },
                                {
                                    name: '成交量',
                                    type: 'bar',
                                    xAxisIndex: 1,
                                    yAxisIndex: 1,
                                    data: volumes,
                                    itemStyle: {
                                        color: (params) => {
                                            const index = params.dataIndex;
                                            const item = this.klineData[index];
                                            return item.close >= item.open ? '#ef232a' : '#14b143';
                                        }
                                    }
                                }
                            ]
                        };

                        this.chart.setOption(option, true);
                        // 重新绑定图表事件
                        this.bindChartEvents();
                        console.log('图表更新成功');

                    } catch (error) {
                        console.error('更新图表时出错:', error);
                        this.error = '图表渲染失败: ' + error.message;
                    }
                },

                getFrequencyText() {
                    const freqMap = {
                        '5': '5分钟', '15': '15分钟', '30': '30分钟', '60': '60分钟',
                        'd': '日', 'w': '周', 'm': '月'
                    };
                    return freqMap[this.frequency] || this.frequency;
                },

                formatPrice(price) {
                    return price ? price.toFixed(2) : '--';
                },

                formatVolume(volume) {
                    if (!volume) return '--';
                    if (volume >= 100000000) {
                        return (volume / 100000000).toFixed(2) + '亿';
                    } else if (volume >= 10000) {
                        return (volume / 10000).toFixed(2) + '万';
                    }
                    return volume.toFixed(0);
                },

                formatAmount(amount) {
                    if (!amount) return '--';
                    return (amount / 100000000).toFixed(2) + '亿元';
                },

                getPriceClass(current, compare) {
                    if (!current || !compare) return '';
                    return current >= compare ? 'price-up' : 'price-down';
                },

                async searchStocks() {
                    if (this.searchTimer) {
                        clearTimeout(this.searchTimer);
                    }

                    this.searchTimer = setTimeout(async () => {
                        if (this.searchKeyword.trim().length < 2) {
                            this.searchResults = [];
                            this.showSearchResults = false;
                            return;
                        }

                        try {
                            const response = await axios.get('/api/stock2/search', {
                                params: { keyword: this.searchKeyword.trim() }
                            });

                            if (response.data.success) {
                                this.searchResults = response.data.data;
                                this.showSearchResults = this.searchResults.length > 0;
                            } else {
                                this.searchResults = [];
                                this.showSearchResults = false;
                            }
                        } catch (err) {
                            console.error('搜索股票失败:', err);
                            this.searchResults = [];
                            this.showSearchResults = false;
                        }
                    }, 500);
                },

                selectStock(stock2) {
                    this.stockCode = stock2.code;
                    this.stockName = stock2.name;
                    this.searchKeyword = stock2.name;
                    this.searchResults = [];
                    this.showSearchResults = false;
                    console.log(`选择了股票: ${stock2.name} (${stock2.code})`);
                },

                onSearchBlur() {
                    setTimeout(() => {
                        this.showSearchResults = false;
                    }, 200);
                },

                onSearchFocus() {
                    if (this.searchKeyword.trim().length >= 2 && this.searchResults.length > 0) {
                        this.showSearchResults = true;
                    }
                },

                clearSearch() {
                    this.searchKeyword = '';
                    this.searchResults = [];
                    this.showSearchResults = false;
                }
            }
        }).mount('#app');
    </script>
</body>
</html>
'''


# 后端代码保持不变...
def prepare_kline_data(df, frequency):
    """数据预处理函数"""
    if df.empty:
        print("数据为空")
        return pd.DataFrame()

    try:
        print(f"原始数据列: {df.columns.tolist()}")
        print(f"数据行数: {len(df)}")

        # 转换数值类型
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 处理其他数值字段
        if 'turn' in df.columns:
            df['turn'] = pd.to_numeric(df['turn'], errors='coerce')
        if 'pctChg' in df.columns:
            df['pctChg'] = pd.to_numeric(df['pctChg'], errors='coerce')

        # 处理日期
        if frequency in ["5", "15", "30", "60"] and 'time' in df.columns:
            print("处理分钟数据日期")
            df['date'] = df.apply(lambda row: datetime.strptime(
                f"{row['date']} {row['time'][8:10]}:{row['time'][10:12]}", "%Y-%m-%d %H:%M"), axis=1)
        else:
            print("处理日线数据日期")
            df['date'] = pd.to_datetime(df['date'])

        # 按日期排序
        df = df.sort_values('date')

        print(f"处理后的数据行数: {len(df)}")
        return df

    except Exception as e:
        print(f"数据预处理错误: {e}")
        import traceback
        traceback.print_exc()
        return df


@app.get("/", response_class=HTMLResponse)
async def index():
    """首页 - 直接返回HTML内容"""
    return HTML_CONTENT


@app.post("/api/stock2/kline", response_model=KlineResponse)
async def get_kline_data(request_data: KlineRequest):
    """获取K线数据API"""
    try:
        stock_code = request_data.stockCode
        frequency = request_data.frequency
        start_date = request_data.startDate
        end_date = request_data.endDate

        print(f"请求参数: stock_code={stock_code}, frequency={frequency}, start_date={start_date}, end_date={end_date}")

        # 设置默认日期
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # 登录Baostock
        lg = bs.login()
        if lg.error_code != '0':
            return KlineResponse(
                success=False,
                error=f'Baostock登录失败: {lg.error_msg}'
            )

        print("Baostock登录成功")

        # 构建查询字段
        fields = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"
        if frequency in ["5", "15", "30", "60"]:
            fields = "date,time,code,open,high,low,close,volume,amount,adjustflag"

        print(f"查询字段: {fields}")

        # 查询数据
        rs = bs.query_history_k_data_plus(
            stock_code,
            fields,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag="3"
        )

        if rs.error_code != '0':
            bs.logout()
            return KlineResponse(
                success=False,
                error=f'查询数据失败: {rs.error_msg}'
            )

        # 获取数据
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())

        print(f"获取到 {len(data_list)} 条数据")

        if len(data_list) == 0:
            bs.logout()
            return KlineResponse(
                success=True,
                data=[],
                stockCode=stock_code,
                frequency=frequency
            )

        # 创建DataFrame
        result = pd.DataFrame(data_list, columns=rs.fields)
        print(f"DataFrame列名: {result.columns.tolist()}")

        # 数据处理
        kline_data = prepare_kline_data(result, frequency)

        # 转换为JSON格式
        output_data = []
        for index, row in kline_data.iterrows():
            # 确保所有必需字段都存在
            item = {
                'date': row['date'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row['date'], 'strftime') else str(
                    row['date']),
                'open': float(row['open']) if pd.notna(row.get('open')) else 0,
                'high': float(row['high']) if pd.notna(row.get('high')) else 0,
                'low': float(row['low']) if pd.notna(row.get('low')) else 0,
                'close': float(row['close']) if pd.notna(row.get('close')) else 0,
                'volume': float(row['volume']) if pd.notna(row.get('volume')) else 0,
                'amount': float(row.get('amount', 0)) if pd.notna(row.get('amount')) else 0
            }

            # 添加可选字段
            if 'turn' in row and pd.notna(row['turn']):
                item['turn'] = float(row['turn'])
            if 'pctChg' in row and pd.notna(row['pctChg']):
                item['pctChg'] = float(row['pctChg'])

            output_data.append(item)

        print(f"返回 {len(output_data)} 条数据")
        bs.logout()

        return KlineResponse(
            success=True,
            data=output_data,
            stockCode=stock_code,
            frequency=frequency
        )

    except Exception as e:
        print(f"API错误: {str(e)}")
        import traceback
        traceback.print_exc()

        return KlineResponse(
            success=False,
            error=f'服务器错误: {str(e)}'
        )


@app.get("/api/stock2/search", response_model=StockSearchResponse)
async def search_stock(keyword: str = ""):
    """搜索股票API"""
    try:
        print(f"搜索股票: {keyword}")

        if not keyword or len(keyword) < 2:
            return StockSearchResponse(
                success=True,
                data=[]
            )

        # 登录Baostock
        lg = bs.login()
        if lg.error_code != '0':
            return StockSearchResponse(
                success=False,
                error=f'Baostock登录失败: {lg.error_msg}'
            )

        stocks = []
        rs = bs.query_stock_basic(code_name=keyword)

        if rs.error_code != '0':
            bs.logout()
            return StockSearchResponse(
                success=False,
                error=f'查询股票失败: {rs.error_msg}'
            )

        while (rs.error_code == '0') & rs.next():
            data = rs.get_row_data()
            stocks.append({
                'code': data[0],
                'name': data[1],
                'industry': data[2] if len(data) > 2 else '',
                'area': data[3] if len(data) > 3 else ''
            })

        print(f"找到 {len(stocks)} 只股票")
        bs.logout()

        return StockSearchResponse(
            success=True,
            data=stocks
        )

    except Exception as e:
        print(f"搜索股票错误: {str(e)}")
        return StockSearchResponse(
            success=False,
            error=str(e)
        )


@app.get("/docs")
async def get_docs():
    """FastAPI自动文档"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


if __name__ == '__main__':
    print("启动股票K线图分析系统 (FastAPI)...")
    print("访问地址: http://127.0.0.1:8000")
    print("API文档: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)