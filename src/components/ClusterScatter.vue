<template>
  <div class="cluster-scatter">
    <h2>用户分群分布</h2>
    <p class="description">X轴：消费金额 | Y轴：购买频率 | 气泡大小：社交活跃度</p>
    <svg ref="svgRef" :width="width" :height="height"></svg>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

export default {
  props: {
    data: Array,
    selectedCluster: Number
  },
  emits: ['cluster-selected'],
  setup(props, { emit }) {
    const svgRef = ref(null)
    const width = 500
    const height = 400
    const margin = { top: 20, right: 20, bottom: 40, left: 50 }

    const clusterColors = {
      0: '#FF6B6B',
      1: '#4ECDC4',
      2: '#45B7D1',
      3: '#FFA07A'
    }

    const clusterNames = {
      0: '高频购买者',
      1: '普通用户',
      2: '社交达人',
      3: 'VIP用户'
    }

    const drawChart = () => {
      if (!svgRef.value || !props.data || props.data.length === 0) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom

      // 创建比例尺
      const xScale = d3.scaleLinear()
        .domain([0, d3.max(props.data, d => d.total_spend)])
        .range([0, innerWidth])

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(props.data, d => d.purchase_freq)])
        .range([innerHeight, 0])

      const radiusScale = d3.scaleSqrt()
        .domain([0, d3.max(props.data, d => d.social_activity)])
        .range([3, 15])

      // 创建主组
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // 添加网格线
      g.append('g')
        .attr('class', 'grid')
        .attr('opacity', 0.1)
        .call(d3.axisLeft(yScale)
          .tickSize(-innerWidth)
          .tickFormat('')
        )

      // X轴
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale))
        .append('text')
        .attr('x', innerWidth / 2)
        .attr('y', 35)
        .attr('fill', '#333')
        .attr('text-anchor', 'middle')
        .text('消费金额 (¥)')

      // Y轴
      g.append('g')
        .call(d3.axisLeft(yScale))
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -innerHeight / 2)
        .attr('y', -35)
        .attr('fill', '#333')
        .attr('text-anchor', 'middle')
        .text('购买频率 (次)')

      // 绘制散点
      g.selectAll('.dot')
        .data(props.data)
        .enter()
        .append('circle')
        .attr('class', 'dot')
        .attr('cx', d => xScale(d.total_spend))
        .attr('cy', d => yScale(d.purchase_freq))
        .attr('r', d => radiusScale(d.social_activity))
        .attr('fill', d => clusterColors[d.cluster])
        .attr('opacity', d => d.cluster === props.selectedCluster ? 0.8 : 0.4)
        .attr('stroke', d => d.cluster === props.selectedCluster ? '#333' : 'none')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')
        .on('click', (event, d) => {
          emit('cluster-selected', d.cluster)
        })
        .on('mouseover', function(event, d) {
          d3.select(this)
            .attr('opacity', 0.9)
            .attr('stroke', '#333')
            .attr('stroke-width', 2)

          // 显示tooltip
          const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(0,0,0,0.8)')
            .style('color', 'white')
            .style('padding', '8px 12px')
            .style('border-radius', '4px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .html(`群体: ${clusterNames[d.cluster]}<br/>消费: ¥${d.total_spend.toFixed(0)}<br/>频率: ${d.purchase_freq}次`)

          setTimeout(() => tooltip.remove(), 3000)
        })

      // 添加图例
      const legend = svg.append('g')
        .attr('transform', `translate(${width - 150}, 20)`)

      Object.entries(clusterNames).forEach(([clusterId, name], i) => {
        const legendRow = legend.append('g')
          .attr('transform', `translate(0, ${i * 25})`)

        legendRow.append('circle')
          .attr('r', 6)
          .attr('fill', clusterColors[clusterId])

        legendRow.append('text')
          .attr('x', 15)
          .attr('y', 5)
          .attr('font-size', '12px')
          .text(name)
      })
    }

    onMounted(() => {
      drawChart()
    })

    watch(() => [props.data, props.selectedCluster], () => {
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
.cluster-scatter {
  width: 100%;
}

h2 {
  font-size: 18px;
  margin-bottom: 8px;
  color: #333;
}

.description {
  font-size: 12px;
  color: #999;
  margin-bottom: 15px;
}

svg {
  width: 100%;
  height: auto;
}

:deep(.grid) {
  stroke: #ddd;
}

:deep(.dot) {
  transition: all 0.2s ease;
}
</style>
