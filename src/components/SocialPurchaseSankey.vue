<template>
  <div class="social-purchase-sankey">
    <h2>社交互动与购买关系</h2>
    <svg ref="svgRef" :width="width" :height="height"></svg>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as d3 from 'd3'

export default {
  props: {
    isDark: { type: Boolean, default: true },
    data: Object
  },
  setup(props) {
    const svgRef = ref(null)
    const width = 1100
    const height = 700
    const margin = { top: 30, right: 220, bottom: 30, left: 100 }

    const drawChart = () => {
      if (!svgRef.value || !props.data || !props.data.sankey) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const textColor = props.isDark ? 'white' : '#1a1a2e'

      const { nodes, links } = props.data.sankey
      if (!nodes || !links || nodes.length === 0) return

      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom

      // Calculate node positions and heights
      const leftNodes = nodes.slice(0, 6)
      const rightNodes = nodes.slice(6, 8)

      // Calculate total value for each node
      const nodeValues = nodes.map((_, i) => {
        return links
          .filter(l => l.source === i || l.target === i)
          .reduce((sum, l) => sum + l.value, 0)
      })

      const maxValue = Math.max(...nodeValues)
      const nodeHeightScale = d3.scaleLinear()
        .domain([0, maxValue])
        .range([10, 60])

      // Position left nodes (6 nodes, evenly spaced)
      const leftNodePositions = leftNodes.map((_, i) => ({
        x: 0,
        y: (innerHeight / 6) * i + (innerHeight / 12),
        height: nodeHeightScale(nodeValues[i])
      }))

      // Position right nodes (2 nodes, centered)
      const rightNodePositions = rightNodes.map((_, i) => ({
        x: innerWidth,
        y: (innerHeight / 2) * i + (innerHeight / 4),
        height: nodeHeightScale(nodeValues[6 + i])
      }))

      const allPositions = [...leftNodePositions, ...rightNodePositions]

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // Draw links first (so they appear behind nodes)
      const maxLinkValue = Math.max(...links.map(l => l.value))
      const linkWidthScale = d3.scaleLinear()
        .domain([0, maxLinkValue])
        .range([2, 40])

      const linkGroup = g.append('g').attr('class', 'links')

      links.forEach(link => {
        const source = allPositions[link.source]
        const target = allPositions[link.target]

        const isHasInteraction = link.source < 6 && link.source % 2 === 0
        const color = isHasInteraction ? '#00d4ff' : '#7c3aed'

        // Create path data for curved link
        const x0 = source.x + 15
        const x1 = target.x - 15
        const xi = d3.interpolate(x0, x1)
        const x2 = xi(0.5)

        const pathData = `M${x0},${source.y + source.height / 2}C${x2},${source.y + source.height / 2} ${x2},${target.y + target.height / 2} ${x1},${target.y + target.height / 2}`

        linkGroup.append('path')
          .attr('d', pathData)
          .attr('fill', 'none')
          .attr('stroke', color)
          .attr('stroke-width', linkWidthScale(link.value))
          .attr('opacity', 0.6)
          .attr('class', 'link')
          .on('mouseover', function() {
            d3.select(this)
              .attr('opacity', 1)
              .attr('filter', 'drop-shadow(0 0 8px rgba(0, 212, 255, 0.8))')
          })
          .on('mouseout', function() {
            d3.select(this)
              .attr('opacity', 0.6)
              .attr('filter', 'none')
          })
      })

      // Add invisible hover areas for tooltips
      links.forEach(link => {
        const source = allPositions[link.source]
        const target = allPositions[link.target]

        const x0 = source.x + 15
        const x1 = target.x - 15
        const xi = d3.interpolate(x0, x1)
        const x2 = xi(0.5)

        const pathData = `M${x0},${source.y + source.height / 2}C${x2},${source.y + source.height / 2} ${x2},${target.y + target.height / 2} ${x1},${target.y + target.height / 2}`

        linkGroup.append('path')
          .attr('d', pathData)
          .attr('fill', 'none')
          .attr('stroke', 'transparent')
          .attr('stroke-width', Math.max(linkWidthScale(link.value), 12))
          .attr('opacity', 0)
          .on('mouseover', function() {
            const midX = (source.x + target.x) / 2
            const midY = (source.y + target.y) / 2

            const tooltip = svg.append('g')
              .attr('class', 'tooltip')
              .attr('transform', `translate(${margin.left + midX},${margin.top + midY - 30})`)

            tooltip.append('rect')
              .attr('x', -50)
              .attr('y', -20)
              .attr('width', 100)
              .attr('height', 40)
              .attr('fill', 'rgba(10, 14, 39, 0.95)')
              .attr('stroke', '#00d4ff')
              .attr('stroke-width', 1)
              .attr('rx', 4)

            tooltip.append('text')
              .attr('text-anchor', 'middle')
              .attr('y', -5)
              .attr('fill', 'white')
              .attr('font-size', '12px')
              .text(`人数: ${link.value.toLocaleString()}`)

            tooltip.append('text')
              .attr('text-anchor', 'middle')
              .attr('y', 10)
              .attr('fill', '#00d4ff')
              .attr('font-size', '11px')
              .text(`占比: ${((link.value / maxLinkValue) * 100).toFixed(1)}%`)
          })
          .on('mouseout', function() {
            svg.selectAll('.tooltip').remove()
          })
      })

      // Draw nodes
      const nodeGroup = g.append('g').attr('class', 'nodes')

      allPositions.forEach((pos, i) => {
        const isLeftNode = i < 6
        const isHasInteraction = i < 6 && i % 2 === 0
        const isPurchased = i === 6

        let nodeColor = '#7c3aed'
        if (isLeftNode && isHasInteraction) nodeColor = '#00d4ff'
        if (isPurchased) nodeColor = '#00d4ff'
        if (i === 7) nodeColor = 'rgba(255, 255, 255, 0.2)'

        nodeGroup.append('rect')
          .attr('x', pos.x - (isLeftNode ? 15 : -15))
          .attr('y', pos.y - pos.height / 2)
          .attr('width', 30)
          .attr('height', pos.height)
          .attr('fill', nodeColor)
          .attr('opacity', 0.8)
          .attr('rx', 4)
          .on('mouseover', function() {
            d3.select(this)
              .attr('opacity', 1)
              .attr('filter', 'drop-shadow(0 0 10px rgba(0, 212, 255, 0.8))')
          })
          .on('mouseout', function() {
            d3.select(this)
              .attr('opacity', 0.8)
              .attr('filter', 'none')
          })

        // Node label
        nodeGroup.append('text')
          .attr('x', pos.x + (isLeftNode ? -25 : 25))
          .attr('y', pos.y)
          .attr('text-anchor', isLeftNode ? 'end' : 'start')
          .attr('dominant-baseline', 'middle')
          .attr('fill', textColor)
          .attr('font-size', '12px')
          .attr('font-weight', '600')
          .text(nodes[i].name)

        // Node value
        nodeGroup.append('text')
          .attr('x', pos.x + (isLeftNode ? -25 : 25))
          .attr('y', pos.y + 12)
          .attr('text-anchor', isLeftNode ? 'end' : 'start')
          .attr('dominant-baseline', 'middle')
          .attr('fill', props.isDark ? '#00d4ff' : '#0099cc')
          .attr('font-size', '11px')
          .text(`${nodeValues[i].toLocaleString()}`)
      })
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
.social-purchase-sankey {
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
