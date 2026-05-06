<template>
  <div class="social-scatter">
    <h2 v-if="!isExpanded">社交活跃度与消费关系</h2>
    <h2 v-else class="expanded-title">社交活跃度与消费关系（{{ ageGroup === 'overview' ? '数据总览' : ageGroup }}）</h2>
    <svg
      ref="svgRef"
      :viewBox="`0 0 ${width} ${height}`"
      preserveAspectRatio="xMidYMid meet"
    ></svg>
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
    const width = props.isExpanded ? window.innerWidth * 0.9 : 550
    const height = props.isExpanded ? window.innerHeight * 0.7 : 600
    const margin = props.isExpanded
      ? { top: 40, right: 50, bottom: 50, left: 120 }
      : { top: 20, right: 10, bottom: 60, left:90 }

    const drawChart = () => {
      if (!svgRef.value || !props.data || !props.data.social_scatter) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const textColor = props.isDark ? 'white' : '#1a1a2e'
      const axisColor = props.isDark ? 'white' : '#666'

      const data = props.data.social_scatter
      if (data.length === 0) return

      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom

      const xScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.social_activity)])
        .range([0, innerWidth])

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.total_spend)])
        .range([innerHeight, 0])

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // X axis
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('fill', axisColor)
        .attr('font-size', props.isExpanded ? '16px' : '10px')

      // X axis label
      g.append('text')
        .attr('x', innerWidth / 2)
        .attr('y', innerHeight + (props.isExpanded ? 60 : 45))
        .attr('text-anchor', 'middle')
        .attr('font-size', props.isExpanded ? '18px' : '14px')
        .attr('fill', axisColor)
        .text('社交活跃度')

      g.selectAll('.domain, .tick line').attr('stroke', axisColor)

      // Y axis
      const maxY = d3.max(data, d => d.total_spend)
      const tickValues = d3.range(0, maxY + 1500, 1500)
      g.append('g')
        .call(d3.axisLeft(yScale).tickValues(tickValues))
        .selectAll('text')
        .attr('fill', axisColor)
        .attr('font-size', props.isExpanded ? '16px' : '12px')

      // Y axis label
      g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -innerHeight / 2)
        .attr('y', -margin.left + 30)
        .attr('text-anchor', 'middle')
        .attr('font-size', props.isExpanded ? '18px' : '14px')
        .attr('fill', axisColor)
        .text('消费金额 (¥)')

      g.selectAll('.domain, .tick line').attr('stroke', axisColor)

      // Scatter points
      g.selectAll('.dot')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'dot')
        .attr('cx', d => xScale(d.social_activity))
        .attr('cy', d => yScale(d.total_spend))
        .attr('r', 3)
        .attr('fill', props.isDark ? '#00d4ff' : '#0099cc')
        .attr('opacity', 0.7)
        .on('mouseover', function(event, d) {
          d3.select(this)
            .attr('r', 5)
            .attr('opacity', 1)

          const tooltip = g.selectAll('.tooltip').data([d])
          tooltip.exit().remove()

          const tooltipEnter = tooltip.enter().append('g')
            .attr('class', 'tooltip')

          // Determine vertical position: show below if point is in upper half
          const showBelow = yScale(d.total_spend) < innerHeight / 2
          const rectY = showBelow ? yScale(d.total_spend) + 10 : Math.max(0, yScale(d.total_spend) - 85)

          // Check horizontal position
          const tooltipXRight = xScale(d.social_activity) + 10
          const showLeft = tooltipXRight + 200 > innerWidth
          const rectX = showLeft ? xScale(d.social_activity) - 210 : tooltipXRight

          tooltipEnter.append('rect')
            .attr('x', rectX)
            .attr('y', rectY)
            .attr('width', 200)
            .attr('height', 65)
            .attr('fill', props.isDark ? 'rgba(0, 20, 40, 0.9)' : 'rgba(255, 255, 255, 0.9)')
            .attr('stroke', props.isDark ? '#00d4ff' : '#0099cc')
            .attr('stroke-width', 2)
            .attr('rx', 5)

          const textX = showLeft ? xScale(d.social_activity) - 190 : xScale(d.social_activity) + 20

          tooltipEnter.append('text')
            .attr('x', textX)
            .attr('y', rectY + 20)
            .attr('font-size', '18px')
            .attr('fill', props.isDark ? '#00d4ff' : '#0099cc')
            .text(`粉丝数: ${d.fans_num}`)

          tooltipEnter.append('text')
            .attr('x', textX)
            .attr('y', rectY + 40)
            .attr('font-size', '18px')
            .attr('fill', props.isDark ? '#00d4ff' : '#0099cc')
            .text(`关注数: ${d.follow_num}`)

          tooltipEnter.append('text')
            .attr('x', textX)
            .attr('y', rectY + 60)
            .attr('font-size', '18px')
            .attr('fill', props.isDark ? '#00d4ff' : '#0099cc')
            .text(`消费金额: ¥${d.total_spend}`)
        })
        .on('mouseout', function() {
          d3.select(this)
            .attr('r', 3)
            .attr('opacity', 0.7)

          g.selectAll('.tooltip').remove()
        })

      // Trend line
      const regression = calculateRegression(data)
      if (regression) {
        const line = d3.line()
          .x(d => xScale(d.x))
          .y(d => yScale(d.y))

        const trendData = [
          { x: 0, y: regression.intercept },
          { x: d3.max(data, d => d.social_activity), y: regression.intercept + regression.slope * d3.max(data, d => d.social_activity) }
        ]

        g.append('path')
          .datum(trendData)
          .attr('fill', 'none')
          .attr('stroke', props.isDark ? '#764ba2' : '#9370DB')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', '5,5')
          .attr('opacity', 1)
          .attr('d', line)
      }

      // Formula annotation in top-right corner
      const annotationY1 = props.isExpanded ? -15 : 15
      const annotationY2 = props.isExpanded ? 10 : 40
      const annotationY3 = props.isExpanded ? 35 : 65

      g.append('text')
        .attr('x', innerWidth - 10)
        .attr('y', annotationY1)
        .attr('text-anchor', 'end')
        .attr('font-size', props.isExpanded ? '20px' : '16px')
        .attr('fill', axisColor)
        .attr('opacity', 0.8)
        .text(`节点数: ${data.length}`)

      g.append('text')
        .attr('x', innerWidth - 10)
        .attr('y', annotationY2)
        .attr('text-anchor', 'end')
        .attr('font-size', props.isExpanded ? '20px' : '16px')
        .attr('fill', axisColor)
        .attr('opacity', 0.8)
        .text('虚线：趋势线')

      g.append('text')
        .attr('x', innerWidth - 10)
        .attr('y', annotationY3)
        .attr('text-anchor', 'end')
        .attr('font-size', props.isExpanded ? '20px' : '16px')
        .attr('fill', axisColor)
        .attr('opacity', 0.8)
        .text('社交活跃度 = 粉丝数 + 关注数')
    }

    const calculateRegression = (data) => {
      if (data.length < 2) return null

      const n = data.length
      const sumX = data.reduce((sum, d) => sum + d.social_activity, 0)
      const sumY = data.reduce((sum, d) => sum + d.total_spend, 0)
      const sumXY = data.reduce((sum, d) => sum + d.social_activity * d.total_spend, 0)
      const sumX2 = data.reduce((sum, d) => sum + d.social_activity * d.social_activity, 0)

      const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
      const intercept = (sumY - slope * sumX) / n

      return { slope, intercept }
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
.social-scatter {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

h2 {
  font-size: 20px;
  margin: 0 0 8px 0;
  color: var(--text-primary, white);
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.6));
  text-align: center;
  flex-shrink: 0;
}
h2:last-of-type {
  font-size: 25px;
}

.expanded-title {
  font-size: 40px !important;
}

svg {
  width: 100%;
  flex: 1;
  min-height: 0;
  display: block;
  filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.4));
  overflow: hidden;
}
</style>
