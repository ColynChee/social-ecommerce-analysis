<template>
  <div class="top-categories">
    <h2>热门品类 Top 5</h2>
    <svg ref="svgRef" :width="width" :height="height"></svg>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

export default {
  props: {
    data: Object
  },
  setup(props) {
    const svgRef = ref(null)
    const width = 300
    const height = 250
    const margin = { top: 20, right: 20, bottom: 40, left: 50 }

    const drawChart = () => {
      if (!svgRef.value || !props.data) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom

      const chartData = Object.entries(props.data.top_categories).map(([cat, data]) => ({
        label: cat,
        value: data.purchase_rate * 100
      }))

      const xScale = d3.scaleBand()
        .domain(chartData.map(d => d.label))
        .range([0, innerWidth])
        .padding(0.3)

      const yScale = d3.scaleLinear()
        .domain([0, 100])
        .range([innerHeight, 0])

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // Bars
      g.selectAll('.bar')
        .data(chartData)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => xScale(d.label))
        .attr('y', d => yScale(d.value))
        .attr('width', xScale.bandwidth())
        .attr('height', d => innerHeight - yScale(d.value))
        .attr('fill', '#667eea')
        .attr('opacity', 0.8)

      // X axis
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('font-size', '11px')

      // Y axis
      g.append('g')
        .call(d3.axisLeft(yScale))

      // Labels
      g.selectAll('.label')
        .data(chartData)
        .enter()
        .append('text')
        .attr('x', d => xScale(d.label) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.value) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '11px')
        .attr('fill', '#333')
        .text(d => `${d.value.toFixed(1)}%`)
    }

    onMounted(() => {
      drawChart()
    })

    watch(() => props.data, () => {
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
.top-categories {
  width: 100%;
}

h2 {
  font-size: 20px;
  margin-bottom: 24px;
  color: #333;
  font-weight: 700;
  letter-spacing: 0.5px;
}

svg {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.08));
}
</style>
