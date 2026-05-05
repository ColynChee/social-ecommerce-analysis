<template>
  <div class="product-insights">
    <!-- 空数据占位提示 -->
    <div v-if="!hasData" class="empty-state">
      <div class="empty-icon">📊</div>
      <div class="empty-title">当前组合下样本量不足</div>
      <div class="empty-hint">请调整筛选条件，或选择更宽泛的维度组合</div>
    </div>

    <template v-else>
      <!-- 上半部分：热力图 + 分组柱状图 并排 -->
      <div class="charts-row">
        <!-- 图表 A：价格×折扣转化热力图 -->
        <div class="chart-card">
          <div class="chart-header">
            <div class="header-left">
              <h2>价格 × 折扣 转化热力图</h2>
              <p class="chart-hint">点击色块查看该组合下的类目详情，再次点击取消选中</p>
            </div>
            <button class="zoom-btn" @click="openZoom('heatmap')" title="放大查看">⤢</button>
          </div>
          <svg ref="heatmapRef" :viewBox="`0 0 ${heatmapWidth} ${heatmapHeight}`" preserveAspectRatio="xMidYMid meet"></svg>
        </div>

        <!-- 图表 B：类目行为对比分组柱状图 -->
        <div class="chart-card">
          <div class="chart-header">
            <div class="header-left">
              <h2>
                类目行为对比
                <span v-if="selectedCell" class="filter-tag">
                  {{ selectedCell.price_group }} / {{ selectedCell.discount_group }}
                  <button class="clear-btn" @click="clearSelection">✕</button>
                </span>
              </h2>
              <div class="legend-row">
                <span class="legend-item"><span class="dot pv"></span>浏览量(归一化)</span>
                <span class="legend-item"><span class="dot cart"></span>加购率(归一化)</span>
                <span class="legend-item"><span class="dot purchase"></span>购买率(归一化)</span>
              </div>
            </div>
            <button class="zoom-btn" @click="openZoom('bar')" title="放大查看">⤢</button>
          </div>
          <svg ref="barChartRef" :viewBox="`0 0 ${barWidth} ${barHeight}`" preserveAspectRatio="xMidYMid meet"></svg>
        </div>
      </div>

      <!-- 下半部分：价格敏感度面积图 -->
      <div class="charts-row single">
        <div class="chart-card full-width">
          <div class="chart-header">
            <div class="header-left">
              <h2>价格敏感度曲线</h2>
              <p class="chart-hint">展示价格提升对购买转化率的衰减效应</p>
            </div>
            <button class="zoom-btn" @click="openZoom('area')" title="放大查看">⤢</button>
          </div>
          <svg ref="areaChartRef" :viewBox="`0 0 ${areaWidth} ${areaHeight}`" preserveAspectRatio="xMidYMid meet"></svg>
        </div>
      </div>
    </template>

    <!-- 放大 Modal（Teleport 到 body）-->
    <Teleport to="body">
      <div v-if="zoomedChart" class="zoom-overlay" @click.self="closeZoom">
        <div class="zoom-content" @click.stop>
          <div class="zoom-header">
            <h2>{{ zoomTitle }}</h2>
            <button class="zoom-close" @click="closeZoom">✕</button>
          </div>
          <div class="zoom-body">
            <svg ref="zoomSvgRef" class="zoom-svg"></svg>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as d3 from 'd3'

export default {
  name: 'ProductInsights',
  props: {
    data: { type: Object, default: null },
    isDark: { type: Boolean, default: true }
  },
  setup(props) {
    // ========== 模板引用 ==========
    const heatmapRef = ref(null)
    const barChartRef = ref(null)
    const areaChartRef = ref(null)
    const zoomSvgRef = ref(null)

    // ========== 尺寸配置（正常模式） ==========
    const heatmapWidth = 620
    const heatmapHeight = 480
    const barWidth = 620
    const barHeight = 480
    const areaWidth = 1280
    const areaHeight = 340

    // ========== 交互状态 ==========
    const selectedCell = ref(null)
    const zoomedChart = ref(null) // null | 'heatmap' | 'bar' | 'area'

    // ========== 计算属性 ==========
    const hasData = computed(() => {
      return props.data && props.data.heatmap && props.data.heatmap.length > 0
    })

    const zoomTitle = computed(() => {
      const titles = {
        heatmap: '价格 × 折扣 转化热力图',
        bar: '类目行为对比',
        area: '价格敏感度曲线'
      }
      return titles[zoomedChart.value] || ''
    })

    // ========== 工具函数 ==========
    const getTextColor = () => props.isDark ? 'white' : '#1a1a2e'
    const getAxisColor = () => props.isDark ? 'white' : '#666'

    // ========== 核心绘制函数（接受目标 SVG 和尺寸参数） ==========

    /**
     * 热力图绘制
     * @param {Element} svgEl - 目标 SVG DOM 元素
     * @param {number} w - 画布宽度
     * @param {number} h - 画布高度
     */
    const drawHeatmapTo = (svgEl, w, h) => {
      if (!svgEl || !props.data || !props.data.heatmap || !props.data.heatmap.length) return

      const svg = d3.select(svgEl)
      svg.selectAll('*').remove()

      const textColor = getTextColor()
      const axisColor = getAxisColor()
      const { heatmap, price_bins, discount_bins } = props.data

      // 边距配置（按比例缩放）
      const scale = w / heatmapWidth
      const margin = {
        top: 20 * scale,
        right: 120 * scale,
        bottom: 50 * scale,
        left: 90 * scale
      }
      const innerWidth = w - margin.left - margin.right
      const innerHeight = h - margin.top - margin.bottom

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // ---- 比例尺配置 ----
      const xScale = d3.scaleBand()
        .domain(price_bins)
        .range([0, innerWidth])
        .padding(0.08)

      const yScale = d3.scaleBand()
        .domain(discount_bins)
        .range([0, innerHeight])
        .padding(0.08)

      const maxRate = d3.max(heatmap, d => d.purchase_rate) || 1
      const colorScale = d3.scaleLinear()
        .domain([0, maxRate])
        .range(['rgba(0, 212, 255, 0.05)', 'rgba(124, 58, 237, 0.85)'])
        .interpolate(d3.interpolateRgb)

      // ---- 绘制色块（D3 join）----
      g.selectAll('.heatmap-cell')
        .data(heatmap, d => `${d.price_group}-${d.discount_group}`)
        .join(
          enter => enter.append('rect')
            .attr('class', 'heatmap-cell')
            .attr('x', d => xScale(d.price_group))
            .attr('y', d => yScale(d.discount_group))
            .attr('width', xScale.bandwidth())
            .attr('height', yScale.bandwidth())
            .attr('rx', 4 * scale)
            .attr('fill', d => {
              if (d.count === 0) return props.isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)'
              if (!d.is_reliable) return 'rgba(255,255,255,0.08)'
              return colorScale(d.purchase_rate)
            })
            .attr('stroke', d => {
              if (selectedCell.value &&
                  selectedCell.value.price_group === d.price_group &&
                  selectedCell.value.discount_group === d.discount_group) {
                return '#00d4ff'
              }
              return 'rgba(255,255,255,0.1)'
            })
            .attr('stroke-width', d => {
              if (selectedCell.value &&
                  selectedCell.value.price_group === d.price_group &&
                  selectedCell.value.discount_group === d.discount_group) {
                return 3 * scale
              }
              return scale
            })
            .attr('opacity', 0)
            .on('mouseover', function (event, d) {
              d3.select(this)
                .transition().duration(150)
                .attr('opacity', 1)
                .attr('stroke', '#00d4ff')
                .attr('stroke-width', 2 * scale)
              showHeatmapTooltip(g, d, xScale, yScale, textColor, scale)
            })
            .on('mouseout', function (event, d) {
              const isSelected = selectedCell.value &&
                selectedCell.value.price_group === d.price_group &&
                selectedCell.value.discount_group === d.discount_group
              d3.select(this)
                .transition().duration(150)
                .attr('opacity', 1)
                .attr('stroke', isSelected ? '#00d4ff' : 'rgba(255,255,255,0.1)')
                .attr('stroke-width', isSelected ? 3 * scale : scale)
              g.selectAll('.heatmap-tooltip').remove()
            })
            .on('click', function (event, d) {
              handleCellClick(d)
            })
            .call(enter => enter.transition().duration(500).attr('opacity', 1))
        )

      // ---- 色块内文字 ----
      g.selectAll('.cell-label')
        .data(heatmap, d => `${d.price_group}-${d.discount_group}`)
        .join('text')
        .attr('class', 'cell-label')
        .attr('x', d => xScale(d.price_group) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.discount_group) + yScale.bandwidth() / 2)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', `${12 * scale}px`)
        .attr('font-weight', '600')
        .attr('fill', d => {
          if (d.count === 0) return 'rgba(255,255,255,0.3)'
          if (!d.is_reliable) return 'rgba(255,255,255,0.5)'
          return d.purchase_rate > maxRate * 0.6 ? 'white' : textColor
        })
        .attr('pointer-events', 'none')
        .text(d => d.count === 0 ? '—' : `${(d.purchase_rate * 100).toFixed(1)}%`)

      // ---- 坐标轴 ----
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('fill', axisColor)
        .attr('font-size', `${12 * scale}px`)
        .attr('transform', 'rotate(-25)')
        .attr('text-anchor', 'end')

      g.append('text')
        .attr('x', innerWidth / 2)
        .attr('y', innerHeight + 45 * scale)
        .attr('text-anchor', 'middle')
        .attr('font-size', `${13 * scale}px`)
        .attr('fill', axisColor)
        .text('价格区间（元）')

      g.append('g')
        .call(d3.axisLeft(yScale))
        .selectAll('text')
        .attr('fill', axisColor)
        .attr('font-size', `${12 * scale}px`)

      g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -innerHeight / 2)
        .attr('y', -65 * scale)
        .attr('text-anchor', 'middle')
        .attr('font-size', `${13 * scale}px`)
        .attr('fill', axisColor)
        .text('折扣区间')

      g.selectAll('.domain, .tick line').attr('stroke', axisColor)

      // ---- 色阶图例 ----
      const legendHeight = innerHeight
      const legendWidth = 14 * scale
      const legendX = innerWidth + 25 * scale

      const legendScale = d3.scaleLinear()
        .domain([0, maxRate])
        .range([legendHeight, 0])

      const defs = svg.append('defs')
      const gradient = defs.append('linearGradient')
        .attr('id', `heatmap-legend-${w}`)
        .attr('x1', '0%').attr('y1', '100%')
        .attr('x2', '0%').attr('y2', '0%')
      gradient.append('stop').attr('offset', '0%').attr('stop-color', 'rgba(0, 212, 255, 0.05)')
      gradient.append('stop').attr('offset', '100%').attr('stop-color', 'rgba(124, 58, 237, 0.85)')

      const legend = g.append('g').attr('transform', `translate(${legendX},0)`)
      legend.append('rect')
        .attr('width', legendWidth).attr('height', legendHeight)
        .attr('fill', `url(#heatmap-legend-${w})`).attr('rx', 3 * scale)

      legend.append('g')
        .attr('transform', `translate(${legendWidth},0)`)
        .call(d3.axisRight(legendScale).ticks(5).tickFormat(d => `${(d * 100).toFixed(0)}%`))
        .selectAll('text').attr('fill', axisColor).attr('font-size', `${11 * scale}px`)
      legend.selectAll('.domain, .tick line').attr('stroke', axisColor)

      legend.append('text')
        .attr('x', legendWidth / 2).attr('y', -8 * scale)
        .attr('text-anchor', 'middle')
        .attr('font-size', `${11 * scale}px`).attr('fill', axisColor)
        .text('购买率')
    }

    const showHeatmapTooltip = (g, d, xScale, yScale, textColor, scale) => {
      g.selectAll('.heatmap-tooltip').remove()
      const tooltipX = xScale(d.price_group) + xScale.bandwidth() / 2
      const tooltipY = yScale(d.discount_group) - 10 * scale
      const showBelow = tooltipY < 120 * scale
      const tooltip = g.append('g').attr('class', 'heatmap-tooltip')
      const boxY = showBelow ? tooltipY + 20 * scale : tooltipY - 130 * scale

      tooltip.append('rect')
        .attr('x', tooltipX - 120 * scale).attr('y', boxY)
        .attr('width', 240 * scale).attr('height', 115 * scale)
        .attr('fill', props.isDark ? 'rgba(0, 20, 40, 0.95)' : 'rgba(255, 255, 255, 0.95)')
        .attr('stroke', '#00d4ff').attr('stroke-width', 1.5 * scale).attr('rx', 8 * scale)

      if (!d.is_reliable) {
        tooltip.append('text')
          .attr('x', tooltipX).attr('y', boxY + 17 * scale)
          .attr('text-anchor', 'middle')
          .attr('font-size', `${11 * scale}px`).attr('fill', '#ff6b6b')
          .text('⚠ 样本量不足，仅供参考')
      }

      const lines = [
        `价格: ${d.price_group}元 | 折扣: ${d.discount_group}`,
        `记录数: ${d.count.toLocaleString()} | 购买率: ${(d.purchase_rate * 100).toFixed(1)}%`,
        `加购率: ${(d.cart_rate * 100).toFixed(1)}% | 平均消费: ¥${d.avg_spend.toFixed(0)}`,
        `平均浏览: ${d.avg_pv.toFixed(1)} | 平均点赞: ${d.avg_like.toFixed(1)}`
      ]
      const textX = tooltipX - 105 * scale
      lines.forEach((line, i) => {
        tooltip.append('text')
          .attr('x', textX).attr('y', boxY + (d.is_reliable ? 22 : 34) * scale + i * 18 * scale)
          .attr('font-size', `${12 * scale}px`)
          .attr('fill', i === 0 ? '#00d4ff' : textColor)
          .text(line)
      })
    }

    /**
     * 分组柱状图绘制
     */
    const drawBarChartTo = (svgEl, w, h) => {
      if (!svgEl || !props.data) return

      const svg = d3.select(svgEl)
      svg.selectAll('*').remove()

      const textColor = getTextColor()
      const axisColor = getAxisColor()

      let chartData = []
      if (selectedCell.value && props.data.heatmap) {
        const cell = props.data.heatmap.find(
          hc => hc.price_group === selectedCell.value.price_group &&
                hc.discount_group === selectedCell.value.discount_group
        )
        if (cell && cell.category_breakdown && cell.category_breakdown.length > 0) {
          const pvs = cell.category_breakdown.map(c => c.pv_count_avg)
          const carts = cell.category_breakdown.map(c => c.cart_rate)
          const purchases = cell.category_breakdown.map(c => c.purchase_rate)
          const pvMin = Math.min(...pvs), pvMax = Math.max(...pvs)
          const cartMin = Math.min(...carts), cartMax = Math.max(...carts)
          const purchaseMin = Math.min(...purchases), purchaseMax = Math.max(...purchases)
          const norm = (val, vmin, vmax) => vmax === vmin ? 0.5 : (val - vmin) / (vmax - vmin)

          chartData = cell.category_breakdown.map(c => ({
            category: c.category,
            normalized_pv: norm(c.pv_count_avg, pvMin, pvMax),
            normalized_cart_rate: norm(c.cart_rate, cartMin, cartMax),
            normalized_purchase_rate: norm(c.purchase_rate, purchaseMin, purchaseMax),
            raw_pv: c.pv_count_avg, raw_cart_rate: c.cart_rate,
            raw_purchase_rate: c.purchase_rate, count: c.count
          }))
        }
      }
      if (chartData.length === 0 && props.data.category_behavior) {
        chartData = props.data.category_behavior.map(c => ({
          category: c.category,
          normalized_pv: c.normalized_pv, normalized_cart_rate: c.normalized_cart_rate,
          normalized_purchase_rate: c.normalized_purchase_rate,
          raw_pv: c.pv_count_avg, raw_cart_rate: c.cart_rate,
          raw_purchase_rate: c.purchase_rate, count: c.count
        }))
      }
      if (chartData.length === 0) return

      const scale = w / barWidth
      const margin = { top: 15 * scale, right: 30 * scale, bottom: 60 * scale, left: 55 * scale }
      const innerWidth = w - margin.left - margin.right
      const innerHeight = h - margin.top - margin.bottom

      const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

      const x0 = d3.scaleBand()
        .domain(chartData.map(d => d.category))
        .range([0, innerWidth]).paddingInner(0.2).paddingOuter(0.1)

      const x1 = d3.scaleBand()
        .domain(['pv', 'cart', 'purchase'])
        .range([0, x0.bandwidth()]).padding(0.08)

      const y = d3.scaleLinear().domain([0, 1]).range([innerHeight, 0])

      const metricColors = {
        pv: { fill: 'rgba(0, 212, 255, 0.7)', hover: '#00d4ff' },
        cart: { fill: 'rgba(124, 58, 237, 0.7)', hover: '#7c3aed' },
        purchase: { fill: 'rgba(0, 255, 136, 0.7)', hover: '#00ff88' }
      }

      const getValue = (d, metric) => {
        if (metric === 'pv') return d.normalized_pv
        if (metric === 'cart') return d.normalized_cart_rate
        return d.normalized_purchase_rate
      }

      const categoryGroups = g.selectAll('.category-group')
        .data(chartData, d => d.category)
        .join('g').attr('class', 'category-group')
        .attr('transform', d => `translate(${x0(d.category)},0)`)

      const metrics = ['pv', 'cart', 'purchase']
      metrics.forEach(metric => {
        categoryGroups.selectAll(`.bar-${metric}`)
          .data(d => [{ ...d, metric }])
          .join(
            enter => enter.append('rect')
              .attr('class', `bar-${metric}`)
              .attr('x', d => x1(metric))
              .attr('width', x1.bandwidth())
              .attr('y', innerHeight).attr('height', 0)
              .attr('fill', metricColors[metric].fill).attr('rx', 3 * scale)
              .on('mouseover', function (event, d) {
                d3.select(this).transition().duration(150)
                  .attr('fill', metricColors[metric].hover).attr('opacity', 1)
                showBarTooltip(g, d, metric, event, innerWidth, innerHeight, textColor, scale)
              })
              .on('mouseout', function () {
                d3.select(this).transition().duration(150)
                  .attr('fill', metricColors[metric].fill).attr('opacity', 0.85)
                g.selectAll('.bar-tooltip').remove()
              })
              .call(enter => enter.transition().duration(600).ease(d3.easeCubicOut)
                .attr('y', d => y(getValue(d, metric)))
                .attr('height', d => innerHeight - y(getValue(d, metric)))
              ),
            update => update.call(update => update.transition().duration(600).ease(d3.easeCubicOut)
              .attr('y', d => y(getValue(d, metric)))
              .attr('height', d => innerHeight - y(getValue(d, metric)))
              .attr('fill', metricColors[metric].fill)
            )
          )
      })

      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x0))
        .selectAll('text')
        .attr('fill', axisColor).attr('font-size', `${11 * scale}px`)
        .attr('transform', 'rotate(-30)').attr('text-anchor', 'end')

      g.append('g')
        .call(d3.axisLeft(y).ticks(5).tickFormat(d => `${(d * 100).toFixed(0)}%`))
        .selectAll('text').attr('fill', axisColor).attr('font-size', `${11 * scale}px`)

      g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -innerHeight / 2).attr('y', -42 * scale)
        .attr('text-anchor', 'middle')
        .attr('font-size', `${12 * scale}px`).attr('fill', axisColor)
        .text('相对强度（归一化）')

      g.selectAll('.domain, .tick line').attr('stroke', axisColor)
    }

    const showBarTooltip = (g, d, metric, event, innerWidth, innerHeight, textColor, scale) => {
      g.selectAll('.bar-tooltip').remove()
      const metricLabel = metric === 'pv' ? '浏览量' : metric === 'cart' ? '加购率' : '购买率'
      const rawValue = metric === 'pv' ? d.raw_pv :
                       metric === 'cart' ? `${(d.raw_cart_rate * 100).toFixed(1)}%` :
                       `${(d.raw_purchase_rate * 100).toFixed(1)}%`
      const tooltip = g.append('g').attr('class', 'bar-tooltip')
      const [mouseX, mouseY] = d3.pointer(event, g.node())
      const boxWidth = 180 * scale, boxHeight = 55 * scale
      const boxX = mouseX + boxWidth > innerWidth ? mouseX - boxWidth - 10 * scale : mouseX + 10 * scale
      const boxY = Math.max(0, mouseY - boxHeight / 2)

      tooltip.append('rect')
        .attr('x', boxX).attr('y', boxY)
        .attr('width', boxWidth).attr('height', boxHeight)
        .attr('fill', props.isDark ? 'rgba(0, 20, 40, 0.95)' : 'rgba(255, 255, 255, 0.95)')
        .attr('stroke', '#00d4ff').attr('stroke-width', scale).attr('rx', 6 * scale)

      tooltip.append('text')
        .attr('x', boxX + 10 * scale).attr('y', boxY + 20 * scale)
        .attr('font-size', `${12 * scale}px`).attr('fill', '#00d4ff')
        .text(`${d.category} · ${metricLabel}`)

      tooltip.append('text')
        .attr('x', boxX + 10 * scale).attr('y', boxY + 40 * scale)
        .attr('font-size', `${12 * scale}px`).attr('fill', textColor)
        .text(`原始值: ${rawValue} | 样本: ${d.count.toLocaleString()}`)
    }

    /**
     * 面积图绘制
     */
    const drawAreaChartTo = (svgEl, w, h) => {
      if (!svgEl || !props.data || !props.data.price_sensitivity) return

      const svg = d3.select(svgEl)
      svg.selectAll('*').remove()

      const textColor = getTextColor()
      const axisColor = getAxisColor()
      const { price_sensitivity } = props.data
      if (price_sensitivity.length === 0) return

      const scale = w / areaWidth
      const margin = { top: 20 * scale, right: 40 * scale, bottom: 50 * scale, left: 65 * scale }
      const innerWidth = w - margin.left - margin.right
      const innerHeight = h - margin.top - margin.bottom

      const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

      const xScale = d3.scaleLinear()
        .domain(d3.extent(price_sensitivity, d => d.price_midpoint))
        .range([0, innerWidth])

      const maxRate = d3.max(price_sensitivity, d => d.purchase_rate) || 1
      const yScale = d3.scaleLinear()
        .domain([0, maxRate * 1.1]).range([innerHeight, 0])

      const defs = svg.append('defs')
      const areaGradient = defs.append('linearGradient')
        .attr('id', `area-gradient-${w}`)
        .attr('x1', '0%').attr('y1', '0%').attr('x2', '0%').attr('y2', '100%')
      areaGradient.append('stop').attr('offset', '0%').attr('stop-color', 'rgba(0, 212, 255, 0.4)')
      areaGradient.append('stop').attr('offset', '100%').attr('stop-color', 'rgba(0, 212, 255, 0.02)')

      const area = d3.area()
        .x(d => xScale(d.price_midpoint)).y0(innerHeight).y1(d => yScale(d.purchase_rate))
        .curve(d3.curveMonotoneX)

      g.append('path').datum(price_sensitivity)
        .attr('fill', `url(#area-gradient-${w})`).attr('d', area)
        .attr('opacity', 0).transition().duration(800).attr('opacity', 1)

      const line = d3.line()
        .x(d => xScale(d.price_midpoint)).y(d => yScale(d.purchase_rate))
        .curve(d3.curveMonotoneX)

      const path = g.append('path').datum(price_sensitivity)
        .attr('fill', 'none').attr('stroke', '#00d4ff').attr('stroke-width', 2.5 * scale).attr('d', line)

      const totalLength = path.node().getTotalLength()
      path.attr('stroke-dasharray', `${totalLength} ${totalLength}`)
        .attr('stroke-dashoffset', totalLength)
        .transition().duration(1200).ease(d3.easeCubicInOut)
        .attr('stroke-dashoffset', 0)

      g.selectAll('.area-dot')
        .data(price_sensitivity)
        .join('circle')
        .attr('class', 'area-dot')
        .attr('cx', d => xScale(d.price_midpoint))
        .attr('cy', d => yScale(d.purchase_rate))
        .attr('r', 0)
        .attr('fill', '#00d4ff')
        .attr('stroke', props.isDark ? '#0a0e27' : 'white')
        .attr('stroke-width', 2 * scale)
        .on('mouseover', function (event, d) {
          d3.select(this).transition().duration(150).attr('r', 7 * scale)
          g.selectAll('.ref-line').remove()
          g.append('line').attr('class', 'ref-line')
            .attr('x1', xScale(d.price_midpoint)).attr('x2', xScale(d.price_midpoint))
            .attr('y1', 0).attr('y2', innerHeight)
            .attr('stroke', 'rgba(0, 212, 255, 0.3)').attr('stroke-width', scale)
            .attr('stroke-dasharray', '4,4')
          g.selectAll('.area-tooltip').remove()
          const tooltip = g.append('g').attr('class', 'area-tooltip')
          const boxX = xScale(d.price_midpoint) + 10 * scale
          const boxY = yScale(d.purchase_rate) - 45 * scale
          const adjustedX = boxX + 170 * scale > innerWidth ? boxX - 180 * scale : boxX
          tooltip.append('rect')
            .attr('x', adjustedX).attr('y', boxY)
            .attr('width', 170 * scale).attr('height', 60 * scale)
            .attr('fill', props.isDark ? 'rgba(0, 20, 40, 0.95)' : 'rgba(255, 255, 255, 0.95)')
            .attr('stroke', '#00d4ff').attr('stroke-width', scale).attr('rx', 6 * scale)
          tooltip.append('text')
            .attr('x', adjustedX + 10 * scale).attr('y', boxY + 20 * scale)
            .attr('font-size', `${12 * scale}px`).attr('fill', '#00d4ff')
            .text(`价格区间: ${d.price_range}元`)
          tooltip.append('text')
            .attr('x', adjustedX + 10 * scale).attr('y', boxY + 40 * scale)
            .attr('font-size', `${12 * scale}px`).attr('fill', textColor)
            .text(`购买率: ${(d.purchase_rate * 100).toFixed(1)}% | n=${d.count.toLocaleString()}`)
        })
        .on('mouseout', function () {
          d3.select(this).transition().duration(150).attr('r', 4.5 * scale)
          g.selectAll('.ref-line').remove()
          g.selectAll('.area-tooltip').remove()
        })
        .transition().delay((d, i) => 800 + i * 80).duration(300).attr('r', 4.5 * scale)

      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale).ticks(8).tickFormat(d => `¥${d}`))
        .selectAll('text').attr('fill', axisColor).attr('font-size', `${11 * scale}px`)

      g.append('text')
        .attr('x', innerWidth / 2).attr('y', innerHeight + 42 * scale)
        .attr('text-anchor', 'middle')
        .attr('font-size', `${13 * scale}px`).attr('fill', axisColor)
        .text('商品价格（元）')

      g.append('g')
        .call(d3.axisLeft(yScale).ticks(5).tickFormat(d => `${(d * 100).toFixed(0)}%`))
        .selectAll('text').attr('fill', axisColor).attr('font-size', `${11 * scale}px`)

      g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -innerHeight / 2).attr('y', -50 * scale)
        .attr('text-anchor', 'middle')
        .attr('font-size', `${13 * scale}px`).attr('fill', axisColor)
        .text('购买转化率')

      g.selectAll('.domain, .tick line').attr('stroke', axisColor)

      if (price_sensitivity.length >= 2) {
        const first = price_sensitivity[0], last = price_sensitivity[price_sensitivity.length - 1]
        const drop = ((first.purchase_rate - last.purchase_rate) / first.purchase_rate * 100).toFixed(1)
        g.append('text')
          .attr('x', innerWidth - 5 * scale).attr('y', 18 * scale)
          .attr('text-anchor', 'end')
          .attr('font-size', `${12 * scale}px`).attr('fill', axisColor).attr('opacity', 0.8)
          .text(`价格从 ${first.price_range} 到 ${last.price_range}，购买率下降约 ${drop}%`)
      }
    }

    // ========== 交互逻辑 ==========
    const handleCellClick = (d) => {
      if (selectedCell.value &&
          selectedCell.value.price_group === d.price_group &&
          selectedCell.value.discount_group === d.discount_group) {
        selectedCell.value = null
      } else {
        selectedCell.value = { price_group: d.price_group, discount_group: d.discount_group }
      }
      drawHeatmapTo(heatmapRef.value, heatmapWidth, heatmapHeight)
      drawBarChartTo(barChartRef.value, barWidth, barHeight)
      // 如果在放大状态，也更新放大视图
      if (zoomedChart.value === 'heatmap') {
        nextTick(() => drawZoomChart())
      }
    }

    const clearSelection = () => {
      selectedCell.value = null
      drawHeatmapTo(heatmapRef.value, heatmapWidth, heatmapHeight)
      drawBarChartTo(barChartRef.value, barWidth, barHeight)
      if (zoomedChart.value) nextTick(() => drawZoomChart())
    }

    // ========== 放大功能 ==========
    const openZoom = (chartType) => {
      zoomedChart.value = chartType
    }

    const closeZoom = () => {
      zoomedChart.value = null
    }

    const drawZoomChart = () => {
      if (!zoomSvgRef.value || !zoomedChart.value) return
      // 计算放大后的尺寸
      const w = window.innerWidth * 0.88
      const h = window.innerHeight * 0.78
      const svg = d3.select(zoomSvgRef.value)
        .attr('width', w).attr('height', h)

      if (zoomedChart.value === 'heatmap') drawHeatmapTo(zoomSvgRef.value, w, h)
      if (zoomedChart.value === 'bar') drawBarChartTo(zoomSvgRef.value, w, h)
      if (zoomedChart.value === 'area') drawAreaChartTo(zoomSvgRef.value, w, h)
    }

    // ESC 键关闭放大
    const handleEsc = (e) => {
      if (e.key === 'Escape' && zoomedChart.value) closeZoom()
    }

    // ========== 生命周期 ==========
    onMounted(() => {
      nextTick(() => {
        drawHeatmapTo(heatmapRef.value, heatmapWidth, heatmapHeight)
        drawBarChartTo(barChartRef.value, barWidth, barHeight)
        drawAreaChartTo(areaChartRef.value, areaWidth, areaHeight)
      })
      document.addEventListener('keydown', handleEsc)
    })

    onBeforeUnmount(() => {
      document.removeEventListener('keydown', handleEsc)
    })

    watch(() => [props.data, props.isDark], () => {
      selectedCell.value = null
      nextTick(() => {
        drawHeatmapTo(heatmapRef.value, heatmapWidth, heatmapHeight)
        drawBarChartTo(barChartRef.value, barWidth, barHeight)
        drawAreaChartTo(areaChartRef.value, areaWidth, areaHeight)
      })
    }, { deep: true })

    watch(zoomedChart, (newVal) => {
      if (newVal) {
        nextTick(() => drawZoomChart())
      }
    })

    return {
      heatmapRef, barChartRef, areaChartRef, zoomSvgRef,
      heatmapWidth, heatmapHeight, barWidth, barHeight, areaWidth, areaHeight,
      selectedCell, zoomedChart, hasData, zoomTitle,
      clearSelection, openZoom, closeZoom
    }
  }
}
</script>

<style scoped>
.product-insights {
  display: flex;
  flex-direction: column;
  gap: 30px;
  width: 100%;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.charts-row.single {
  display: block;
}

.chart-card {
  background: var(--bg-card, rgba(15, 23, 41, 0.8));
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color, rgba(0, 212, 255, 0.3));
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 0 20px var(--shadow-glow, rgba(0, 212, 255, 0.2)),
              inset 0 0 20px rgba(0, 212, 255, 0.05);
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0 40px var(--shadow-glow, rgba(0, 212, 255, 0.3)),
              0 0 80px rgba(124, 58, 237, 0.2),
              inset 0 0 20px var(--shadow-glow, rgba(0, 212, 255, 0.1));
  border-color: var(--border-hover, rgba(0, 212, 255, 0.6));
}

.chart-card.full-width {
  width: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}

.header-left {
  flex: 1;
  min-width: 0;
}

.chart-header h2 {
  margin: 0 0 6px 0;
  color: var(--text-primary, white);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.6));
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.chart-hint {
  margin: 0;
  font-size: 13px;
  opacity: 0.65;
  color: var(--text-primary, white);
}

/* 放大按钮 */
.zoom-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color, rgba(0, 212, 255, 0.3));
  background: var(--bg-btn, rgba(10, 14, 39, 0.6));
  color: var(--text-accent, #00d4ff);
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
  line-height: 1;
}

.zoom-btn:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: #00d4ff;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.4);
  transform: scale(1.08);
}

/* 空数据占位 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: var(--bg-card, rgba(15, 23, 41, 0.8));
  border: 1px dashed var(--border-color, rgba(0, 212, 255, 0.3));
  border-radius: 16px;
  gap: 16px;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.6;
}

.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary, white);
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.6));
}

.empty-hint {
  font-size: 14px;
  color: var(--text-primary, white);
  opacity: 0.55;
}

/* 筛选标签 */
.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.4);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: #00d4ff;
}

.clear-btn {
  background: none;
  border: none;
  color: #00d4ff;
  cursor: pointer;
  font-size: 14px;
  padding: 0 2px;
  line-height: 1;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.clear-btn:hover { opacity: 1; }

.legend-row {
  display: flex;
  gap: 20px;
  margin-top: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-primary, white);
  opacity: 0.8;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.dot.pv { background: rgba(0, 212, 255, 0.7); }
.dot.cart { background: rgba(124, 58, 237, 0.7); }
.dot.purchase { background: rgba(0, 255, 136, 0.7); }

svg {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.2));
}

/* ========== 放大 Modal ========== */
.zoom-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.25s ease;
}

.zoom-content {
  width: 92vw;
  height: 88vh;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1729 100%);
  border: 1px solid rgba(0, 212, 255, 0.4);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 60px rgba(0, 212, 255, 0.3), 0 0 120px rgba(124, 58, 237, 0.2);
  animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.zoom-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.zoom-header h2 {
  margin: 0;
  font-size: 22px;
  color: white;
  font-weight: 700;
  text-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
}

.zoom-close {
  width: 40px;
  height: 40px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: rgba(0, 212, 255, 0.1);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
}

.zoom-close:hover {
  background: rgba(255, 100, 100, 0.2);
  border-color: rgba(255, 100, 100, 0.5);
  color: #ff6b6b;
}

.zoom-body {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.zoom-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.3));
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from { transform: scale(0.92); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@media (max-width: 1024px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
