<template>
  <div class="behavior-funnel">
    <h2>行为转化漏斗</h2>
    <svg ref="svgRef" :width="width" :height="height"></svg>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

export default {
  props: {
    isDark: { type: Boolean, default: true },
    data: Object
  },
  setup(props) {
    const svgRef = ref(null)
    const width = 950
    const height = 650
    const margin = { top: 20, right: 180, bottom: 20, left: 300 }

    const drawChart = () => {
      if (!svgRef.value || !props.data || !props.data.funnel) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const textColor = props.isDark ? 'white' : '#1a1a2e'

      const funnelData = props.data.funnel
      if (funnelData.length === 0) return

      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom
      const stepHeight = innerHeight / funnelData.length

      const maxCount = Math.max(...funnelData.map(d => d.count))
      const widthScale = d3.scaleLinear()
        .domain([0, maxCount])
        .range([50, innerWidth - 50])

      const colorScale = d3.scaleLinear()
        .domain([0, funnelData.length - 1])
        .range(['#00d4ff', '#7c3aed'])
        .interpolate(d3.interpolateRgb)

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // Draw trapezoids
      funnelData.forEach((d, i) => {
        const nextCount = i < funnelData.length - 1 ? funnelData[i + 1].count : d.count
        const currentWidth = widthScale(d.count)
        const nextWidth = widthScale(nextCount)
        const y = i * stepHeight

        // Trapezoid path
        const x1 = (innerWidth - currentWidth) / 2
        const x2 = x1 + currentWidth
        const x3 = (innerWidth - nextWidth) / 2
        const x4 = x3 + nextWidth

        const pathData = `M ${x1} ${y} L ${x2} ${y} L ${x4} ${y + stepHeight} L ${x3} ${y + stepHeight} Z`

        g.append('path')
          .attr('d', pathData)
          .attr('fill', colorScale(i))
          .attr('opacity', 0.7)
          .attr('stroke', 'rgba(255, 255, 255, 0.3)')
          .attr('stroke-width', 1)
          .on('mouseover', function() {
            d3.select(this)
              .attr('opacity', 1)
              .attr('filter', 'drop-shadow(0 0 10px rgba(0, 212, 255, 0.8))')
          })
          .on('mouseout', function() {
            d3.select(this)
              .attr('opacity', 0.7)
              .attr('filter', 'none')
          })

        // Step label (left side)
        g.append('text')
          .attr('x', -10)
          .attr('y', y + stepHeight / 2)
          .attr('text-anchor', 'end')
          .attr('dominant-baseline', 'middle')
          .attr('fill', textColor)
          .attr('font-size', '14px')
          .attr('font-weight', '600')
          .text(d.step)

        // Count and conversion rate (right side)
        const conversionRate = i === 0 ? '100%' : `${((d.count / funnelData[i - 1].count) * 100).toFixed(1)}%`

        g.append('text')
          .attr('x', innerWidth + 10)
          .attr('y', y + stepHeight / 2 - 5)
          .attr('text-anchor', 'start')
          .attr('fill', props.isDark ? '#00d4ff' : '#0099cc')
          .attr('font-size', '13px')
          .attr('font-weight', '600')
          .text(`${d.count.toLocaleString()}`)

        g.append('text')
          .attr('x', innerWidth + 10)
          .attr('y', y + stepHeight / 2 + 10)
          .attr('text-anchor', 'start')
          .attr('fill', props.isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(26, 26, 46, 0.7)')
          .attr('font-size', '11px')
          .text(`转化: ${conversionRate}`)
      })
    }

    onMounted(() => {
      drawChart()
    })

    watch(() => [props.data, props.isDark], () => {
      drawChart()
    }, { deep: true })

    return {
      svgRef,
      width,
      height
    }
  }
}
</script>

<style scoped>
.behavior-funnel {
  width: 100%;
}

h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: var(--text-primary, white);
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.6));
}

svg {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.4));
}
</style>
