<template>
  <div class="top-categories-cloud">
    <h2>热门品类</h2>
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
    const width = 630
    const height = 610

    const drawChart = () => {
      if (!svgRef.value || !props.data || !props.data.top_categories) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const textColor = props.isDark ? 'white' : '#1a1a2e'

      const categories = Object.entries(props.data.top_categories).map(([name, data]) => ({
        name,
        rate: data.purchase_rate
      }))

      if (categories.length === 0) return

      const maxRate = d3.max(categories, d => d.rate)
      const minRate = d3.min(categories, d => d.rate)

      const sizeScale = d3.scaleLinear()
        .domain([minRate, maxRate])
        .range([20, 70])

      const colorScale = d3.scaleLinear()
        .domain([minRate, maxRate])
        .range(['#ffffff', '#ffffff'])

      // Force simulation with improved parameters
      const simulation = d3.forceSimulation(categories)
        .force('x', d3.forceX(width / 2).strength(0.05))
        .force('y', d3.forceY(height / 2).strength(0.05))
        .force('collide', d3.forceCollide(d => sizeScale(d.rate) + 50).strength(1.5))
        .force('charge', d3.forceManyBody().strength(-300))
        .stop()

      for (let i = 0; i < 400; i++) {
        simulation.tick()
      }

      const g = svg.append('g')

      // Words with better boundary constraints
      g.selectAll('.word')
        .data(categories)
        .enter()
        .append('text')
        .attr('class', 'word')
        .attr('x', d => {
          const padding = sizeScale(d.rate) + 20
          return Math.max(padding, Math.min(width - padding, d.x))
        })
        .attr('y', d => {
          const padding = sizeScale(d.rate) + 20
          return Math.max(padding, Math.min(height - padding, d.y))
        })
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', d => sizeScale(d.rate))
        .attr('font-weight', 700)
        .attr('fill', textColor)
        .attr('opacity', 1)
        .text(d => d.name)
        .on('mouseover', function(event, d) {
          d3.select(this)
            .attr('opacity', 1)
            .attr('font-size', sizeScale(d.rate) * 1.1)
        })
        .on('mouseout', function(event, d) {
          d3.select(this)
            .attr('opacity', 1)
            .attr('font-size', sizeScale(d.rate))
        })

      // Rate labels
      g.selectAll('.rate-label')
        .data(categories)
        .enter()
        .append('text')
        .attr('class', 'rate-label')
        .attr('x', d => {
          const padding = sizeScale(d.rate) + 20
          return Math.max(padding, Math.min(width - padding, d.x))
        })
        .attr('y', d => {
          const padding = sizeScale(d.rate) + 20
          return Math.max(padding, Math.min(height - padding, d.y)) + sizeScale(d.rate) / 2 + 18
        })
        .attr('text-anchor', 'middle')
        .attr('font-size', '15px')
        .attr('fill', textColor)
        .attr('opacity', 1)
        .text(d => (d.rate * 100).toFixed(1) + '%')
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
.top-categories-cloud {
  width: 100%;
  padding: 0;
}

h2 {
  font-size: 20px;
  margin-bottom: 2px;
  color: var(--text-primary, white);
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.6));
}

svg {
  width: 100%;
  height: auto;
  margin-top: -60px;
  display: block;
  filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.4));
}
</style>
