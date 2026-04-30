<template>
  <div class="social-purchase-bar">
    <h2>社交互动与购买关系</h2>
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
    const width = 600
    const height = 350
    const margin = { top: 20, right: 20, bottom: 50, left: 60 }

    const drawChart = () => {
      if (!svgRef.value || !props.data || !props.data.social_purchase) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const chartData = props.data.social_purchase
      if (chartData.length === 0) return

      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom

      // Group data by interaction type
      const interactions = ['点赞', '评论', '分享']
      const groupedData = interactions.map(interaction => ({
        interaction,
        data: chartData.filter(d => d.interaction === interaction)
      }))

      const xScale = d3.scaleBand()
        .domain(interactions)
        .range([0, innerWidth])
        .padding(0.3)

      const innerBandScale = d3.scaleBand()
        .domain(['有互动', '无互动'])
        .range([0, xScale.bandwidth()])
        .padding(0.1)

      const yScale = d3.scaleLinear()
        .domain([0, 1])
        .range([innerHeight, 0])

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // Draw bars
      g.selectAll('.interaction-group')
        .data(groupedData)
        .enter()
        .append('g')
        .attr('class', 'interaction-group')
        .attr('transform', d => `translate(${xScale(d.interaction)},0)`)
        .selectAll('.bar')
        .data(d => d.data)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => innerBandScale(d.group))
        .attr('y', d => yScale(d.purchase_rate))
        .attr('width', innerBandScale.bandwidth())
        .attr('height', d => innerHeight - yScale(d.purchase_rate))
        .attr('fill', d => d.group === '有互动' ? '#00d4ff' : '#7c3aed')
        .attr('opacity', 0.8)
        .on('mouseover', function(event, d) {
          d3.select(this)
            .attr('opacity', 1)
            .attr('filter', 'drop-shadow(0 0 8px rgba(0, 212, 255, 0.8))')

          // Show tooltip
          const tooltip = svg.append('g')
            .attr('class', 'tooltip')
            .attr('transform', `translate(${margin.left + xScale(d.interaction) + innerBandScale(d.group) + innerBandScale.bandwidth() / 2},${margin.top + yScale(d.purchase_rate) - 10})`)

          tooltip.append('rect')
            .attr('x', -50)
            .attr('y', -25)
            .attr('width', 100)
            .attr('height', 50)
            .attr('fill', 'rgba(10, 14, 39, 0.95)')
            .attr('stroke', '#00d4ff')
            .attr('stroke-width', 1)
            .attr('rx', 4)

          tooltip.append('text')
            .attr('text-anchor', 'middle')
            .attr('y', -10)
            .attr('fill', 'white')
            .attr('font-size', '12px')
            .text(`购买率: ${(d.purchase_rate * 100).toFixed(1)}%`)

          tooltip.append('text')
            .attr('text-anchor', 'middle')
            .attr('y', 5)
            .attr('fill', '#00d4ff')
            .attr('font-size', '11px')
            .text(`样本: ${d.count}`)
        })
        .on('mouseout', function() {
          d3.select(this)
            .attr('opacity', 0.8)
            .attr('filter', 'none')

          svg.selectAll('.tooltip').remove()
        })

      // X axis
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('fill', 'white')
        .attr('font-size', '12px')

      g.selectAll('.domain, .tick line').attr('stroke', 'white')

      // Y axis
      g.append('g')
        .call(d3.axisLeft(yScale).ticks(5).tickFormat(d => `${(d * 100).toFixed(0)}%`))
        .selectAll('text')
        .attr('fill', 'white')
        .attr('font-size', '12px')

      g.selectAll('.domain, .tick line').attr('stroke', 'white')

      // Legend
      const legend = g.append('g')
        .attr('transform', `translate(${innerWidth - 150}, -15)`)

      legend.append('rect')
        .attr('width', 8)
        .attr('height', 8)
        .attr('fill', '#00d4ff')

      legend.append('text')
        .attr('x', 12)
        .attr('y', 8)
        .attr('fill', 'white')
        .attr('font-size', '12px')
        .text('有互动')

      legend.append('rect')
        .attr('x', 70)
        .attr('width', 8)
        .attr('height', 8)
        .attr('fill', '#7c3aed')

      legend.append('text')
        .attr('x', 82)
        .attr('y', 8)
        .attr('fill', 'white')
        .attr('font-size', '12px')
        .text('无互动')
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
.social-purchase-bar {
  width: 100%;
}

h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: white;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.6);
}

svg {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.4));
}
</style>
