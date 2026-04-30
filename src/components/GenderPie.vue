<template>
  <div class="gender-pie">
    <h2>性别分布</h2>
    <div class="chart-container">
      <svg ref="svgRef" :width="width" :height="height"></svg>
      <div class="legend">
        <div class="legend-item male">
          <span class="dot"></span>
          <span class="text">男性 ({{ (data?.gender_distribution.male_ratio * 100).toFixed(1) }}%)</span>
        </div>
        <div class="legend-item female">
          <span class="dot"></span>
          <span class="text">女性 ({{ (data?.gender_distribution.female_ratio * 100).toFixed(1) }}%)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

export default {
  props: {
    data: Object,
    isDark: { type: Boolean, default: true }
  },
  setup(props) {
    const svgRef = ref(null)
    const width = 330
    const height = 330
    const hoveredIndex = ref(null)

    const drawChart = () => {
      if (!svgRef.value || !props.data) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const textColor = props.isDark ? 'white' : '#1a1a2e'
      const axisColor = props.isDark ? 'white' : '#666'

      const genderData = [
        { label: '男性', value: props.data.gender_distribution.male_ratio * 100, count: props.data.gender_distribution.male, color: '#4A90E2' },
        { label: '女性', value: props.data.gender_distribution.female_ratio * 100, count: props.data.gender_distribution.female, color: '#FF6B9D' }
      ]

      const radius = Math.min(width, height) / 2 - 30

      // Add defs for gradients and filters
      const defs = svg.append('defs')

      // Gradient for male
      defs.append('linearGradient')
        .attr('id', 'gradient-male')
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '100%')
        .attr('y2', '100%')
        .selectAll('stop')
        .data([
          { offset: '0%', color: '#4A90E2' },
          { offset: '100%', color: '#357ABD' }
        ])
        .enter()
        .append('stop')
        .attr('offset', d => d.offset)
        .attr('stop-color', d => d.color)

      // Gradient for female
      defs.append('linearGradient')
        .attr('id', 'gradient-female')
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '100%')
        .attr('y2', '100%')
        .selectAll('stop')
        .data([
          { offset: '0%', color: '#FF6B9D' },
          { offset: '100%', color: '#FF8FB3' }
        ])
        .enter()
        .append('stop')
        .attr('offset', d => d.offset)
        .attr('stop-color', d => d.color)

      // Shadow filter
      const filter = defs.append('filter')
        .attr('id', 'shadow')
        .attr('x', '-50%')
        .attr('y', '-50%')
        .attr('width', '200%')
        .attr('height', '200%')

      filter.append('feDropShadow')
        .attr('dx', 0)
        .attr('dy', 4)
        .attr('stdDeviation', 6)
        .attr('flood-opacity', 0.3)

      const g = svg.append('g')
        .attr('transform', `translate(${width / 2},${height / 2})`)

      const pie = d3.pie().value(d => d.value)
      const arc = d3.arc().innerRadius(0).outerRadius(radius)
      const arcHover = d3.arc().innerRadius(0).outerRadius(radius + 10)

      const arcs = g.selectAll('.arc')
        .data(pie(genderData))
        .enter()
        .append('g')
        .attr('class', 'arc')
        .attr('filter', 'url(#shadow)')

      // Add 3D effect with shadow
      arcs.append('path')
        .attr('d', arc)
        .attr('fill', (d, i) => i === 0 ? 'url(#gradient-male)' : 'url(#gradient-female)')
        .attr('opacity', 0.9)
        .attr('stroke', textColor)
        .attr('stroke-width', 3)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d, i) {
          hoveredIndex.value = d.index
          d3.select(this)
            .transition()
            .duration(200)
            .attr('d', arcHover)
            .attr('opacity', 1)
        })
        .on('mouseout', function(event, d) {
          hoveredIndex.value = null
          d3.select(this)
            .transition()
            .duration(200)
            .attr('d', arc)
            .attr('opacity', 0.9)
        })

      // Add labels with animation
      arcs.append('text')
        .attr('class', 'label-text')
        .attr('transform', d => `translate(${arc.centroid(d)})`)
        .attr('text-anchor', 'middle')
        .attr('font-size', '14px')
        .attr('fill', textColor)
        .attr('font-weight', 'bold')
        .attr('opacity', 0)
        .text(d => `${d.data.value.toFixed(1)}%`)
        .transition()
        .delay(300)
        .duration(500)
        .attr('opacity', 1)

      // Update labels on hover
      svg.on('mousemove', function() {
        arcs.selectAll('.label-text').text((d, i) => {
          if (hoveredIndex.value === d.index) {
            return `${d.data.count} 人`
          }
          return `${d.data.value.toFixed(1)}%`
        })
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
.gender-pie {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

h2 {
  font-size: 20px;
  margin-bottom: 16px;
  color: var(--text-primary, white);
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.6));
}

.chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
}

svg {
  width: 100%;
  height: auto;
  max-width: 500px;
  filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.4));
  cursor: pointer;
  transition: filter 0.3s ease;
  overflow: visible;
}

svg:hover {
  filter: drop-shadow(0 0 25px rgba(0, 212, 255, 0.6));
}

.legend {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, white);
}

.legend-item.male .dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.8);
}

.legend-item.female .dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
  box-shadow: 0 0 10px rgba(236, 72, 153, 0.8);
}

.text {
  font-weight: 600;
  text-shadow: 0 0 5px rgba(0, 212, 255, 0.4);
}
</style>
