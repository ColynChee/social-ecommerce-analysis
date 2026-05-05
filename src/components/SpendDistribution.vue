<template>
  <div class="spend-distribution">
    <h2 v-if="!isExpanded">消费金额分布</h2>
    <h2 v-else class="expanded-title">消费金额分布（{{ ageGroup === 'overview' ? '数据总览' : ageGroup }}）</h2>
    <svg ref="svgRef" :width="width" :height="height"></svg>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as d3 from 'd3'

export default {
  props: {
    isDark: { type: Boolean, default: true },
    data: Object,
    isExpanded: { type: Boolean, default: false },
    ageGroup: { type: String, default: null }
  },
  setup(props) {
    const svgRef = ref(null)
    const width = props.isExpanded ? window.innerWidth * 0.9 : 500
    const height = props.isExpanded ? window.innerHeight * 0.79 : 545
    const margin = props.isExpanded
      ? { top: 40, right: 50, bottom: 80, left: 120 }
      : { top: 30, right: 30, bottom: 80, left: 70 }

    const drawChart = () => {
      if (!svgRef.value || !props.data || !props.data.spend_distribution.length) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const textColor = props.isDark ? 'white' : '#1a1a2e'
      const axisColor = props.isDark ? 'white' : '#666'

      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom

      let chartData = props.data.spend_distribution

      // 非展开时，将10001及以后的数据合并为"10000+"
      if (!props.isExpanded) {
        const simplified = []
        let sum10000Plus = 0

        for (const item of chartData) {
          const rangeStart = parseInt(item.range.split('-')[0])
          if (rangeStart >= 10001 || item.range === '50000+') {
            sum10000Plus += item.count
          } else {
            simplified.push(item)
          }
        }

        if (sum10000Plus > 0) {
          simplified.push({
            range: '10000+',
            count: sum10000Plus,
            top5_categories: []
          })
        }

        chartData = simplified
      }

      const xScale = d3.scaleBand()
        .domain(chartData.map(d => d.range))
        .range([0, innerWidth])
        .padding(0.2)

      const maxCount = d3.max(chartData, d => d.count)
      let roundedMax, tickInterval

      if (maxCount <= 200) {
        tickInterval = 20
        roundedMax = Math.ceil(maxCount / 20) * 20
      } else if (maxCount <= 500) {
        tickInterval = 50
        roundedMax = Math.ceil(maxCount / 50) * 50
      } else if (maxCount <= 2000) {
        tickInterval = 200
        roundedMax = Math.ceil(maxCount / 200) * 200
      } else if (maxCount <= 3000) {
        tickInterval = 500
        roundedMax = Math.ceil(maxCount / 500) * 500
      } else {
        tickInterval = 1000
        roundedMax = Math.ceil(maxCount / 1000) * 1000
      }

      const yScale = d3.scaleLinear()
        .domain([0, roundedMax])
        .range([innerHeight, 0])

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // Bars
      g.selectAll('.bar')
        .data(chartData)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => xScale(d.range))
        .attr('y', d => yScale(d.count))
        .attr('width', xScale.bandwidth())
        .attr('height', d => innerHeight - yScale(d.count))
        .attr('fill', '#667eea')
        .attr('opacity', 0.7)
        .on('mouseover', function() {
          d3.select(this)
            .attr('opacity', 1)
            .attr('fill', '#764ba2')
        })
        .on('mouseout', function() {
          d3.select(this)
            .attr('opacity', 0.7)
            .attr('fill', '#667eea')
        })
        .on('click', function(event, d) {
          if (!props.isExpanded || !d.top5_categories) return

          g.selectAll('.top5-tooltip').remove()

          const tooltipX = xScale(d.range) + xScale.bandwidth() / 2
          let tooltipY = yScale(d.count) - 20

          // 检测tooltip是否会超出上边界，如果会则显示在下方
          const tooltipHeight = 155
          const tooltipTopY = tooltipY - 160
          const isAboveBar = tooltipTopY < 0

          if (isAboveBar) {
            tooltipY = yScale(d.count) + 20
          }

          const tooltip = g.append('g')
            .attr('class', 'top5-tooltip')

          tooltip.append('rect')
            .attr('x', tooltipX - 150)
            .attr('y', isAboveBar ? tooltipY : tooltipY - 160)
            .attr('width', 280)
            .attr('height', 150)
            .attr('fill', props.isDark ? 'rgba(0, 20, 40, 0.95)' : 'rgba(255, 255, 255, 0.95)')
            .attr('stroke', props.isDark ? '#FF6B9D' : '#E63384')
            .attr('stroke-width', 2)
            .attr('rx', 5)

          tooltip.append('text')
            .attr('x', tooltipX)
            .attr('y', isAboveBar ? tooltipY + 25 : tooltipY - 135)
            .attr('text-anchor', 'middle')
            .attr('font-size', '18px')
            .attr('font-weight', 'bold')
            .attr('fill', props.isDark ? '#FF6B9D' : '#E63384')
            .text('最受欢迎的商品类别Top5')

          d.top5_categories.forEach((item, index) => {
            tooltip.append('text')
              .attr('x', tooltipX - 140)
              .attr('y', isAboveBar ? tooltipY + 50 + index * 20 : tooltipY - 110 + index * 20)
              .attr('font-size', '16px')
              .attr('fill', props.isDark ? '#00d4ff' : '#0099cc')
              .text(`${index + 1}. ${item.category} (${item.count}次)`)
          })
        })

      // Calculate density curve using Gaussian KDE
      const densityData = []
      const xValues = chartData.map((d, i) => i)
      const yValues = chartData.map(d => d.count)

      for (let i = 0; i < chartData.length; i++) {
        let density = 0
        const bandwidth = 0.8
        for (let j = 0; j < chartData.length; j++) {
          const distance = (i - j) / bandwidth
          density += yValues[j] * Math.exp(-0.5 * distance * distance)
        }
        densityData.push({ x: i, y: density / Math.sqrt(2 * Math.PI * bandwidth * bandwidth) })
      }

      // Density curve
      const line = d3.line()
        .x(d => xScale.bandwidth() / 2 + xScale(chartData[d.x].range))
        .y(d => yScale(d.y))

      g.append('path')
        .datum(densityData)
        .attr('fill', 'none')
        .attr('stroke', props.isDark ? '#FF6B9D' : '#E63384')
        .attr('stroke-width', 2.5)
        .attr('d', line)

      // Legend for density curve
      const legendX = innerWidth - (props.isExpanded ? 200 : 120)
      const legendY = props.isExpanded ? 50 : 20

      g.append('line')
        .attr('x1', legendX)
        .attr('y1', legendY)
        .attr('x2', legendX + 30)
        .attr('y2', legendY)
        .attr('stroke', props.isDark ? '#FF6B9D' : '#E63384')
        .attr('stroke-width', 2.5)

      g.append('text')
        .attr('x', legendX + 40)
        .attr('y', legendY + 5)
        .attr('font-size', props.isExpanded ? '20px' : '12px')
        .attr('fill', axisColor)
        .text('密度曲线')

      // X axis
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('font-size', props.isExpanded ? '16px' : '10px')
        .attr('fill', axisColor)
        .attr('transform', 'rotate(-45)')
        .attr('text-anchor', 'end')

      // X axis label
      g.append('text')
        .attr('x', innerWidth / 2)
        .attr('y', innerHeight + (props.isExpanded ? 95 : 68))
        .attr('text-anchor', 'middle')
        .attr('font-size', props.isExpanded ? '18px' : '12px')
        .attr('fill', axisColor)
        .text('消费金额(元)')

      g.selectAll('.domain, .tick line').attr('stroke', axisColor)

      // Y axis
      g.append('g')
        .call(d3.axisLeft(yScale).ticks(roundedMax / tickInterval))
        .selectAll('text')
        .attr('fill', axisColor)
        .attr('font-size', props.isExpanded ? '16px' : '10px')

      // Y axis label
      g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -innerHeight / 2)
        .attr('y', props.isExpanded ? -margin.left + 35 : -margin.left + 20)
        .attr('text-anchor', 'middle')
        .attr('font-size', props.isExpanded ? '18px' : '12px')
        .attr('fill', axisColor)
        .text('用户数(人)')

      // Labels on bars
      g.selectAll('.label')
        .data(chartData)
        .enter()
        .append('text')
        .attr('x', d => xScale(d.range) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.count) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', props.isExpanded ? '16px' : '10px')
        .attr('fill', textColor)
        .text(d => d.count)
    }

    onMounted(() => {
      drawChart()
    })

    watch(() => [props.data, props.isDark], () => {
      drawChart()
    }, { deep: true })

    onBeforeUnmount(() => {
      if (svgRef.value) {
        d3.select(svgRef.value).selectAll('*').interrupt()
      }
    })

    return {
      svgRef,
      width,
      height
    }
  }
}
</script>

<style scoped>
.spend-distribution {
  width: 100%;
}

h2 {
  font-size: 16px;
  margin-bottom: 0px;
  color: var(--text-primary, white);
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.6));
  text-align: center;
}

h2:last-of-type {
  font-size: 25px;
}

.expanded-title {
  font-size: 40px !important;
}

svg {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.4));
}
</style>

