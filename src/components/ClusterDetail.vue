<template>
  <div class="cluster-detail">
    <h2>群体特征对比</h2>
    <svg ref="svgRef" :width="width" :height="height"></svg>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

export default {
  props: {
    clusterData: Array,
    selectedCluster: Number,
    analysisResults: Object
  },
  setup(props) {
    const svgRef = ref(null)
    const width = 500
    const height = 400

    const clusterNames = {
      0: '高频购买者',
      1: '普通用户',
      2: '社交达人',
      3: 'VIP用户'
    }

    const clusterColors = {
      0: '#FF6B6B',
      1: '#4ECDC4',
      2: '#45B7D1',
      3: '#FFA07A'
    }

    const drawRadar = () => {
      if (!svgRef.value || !props.analysisResults || props.selectedCluster === null) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const data = props.analysisResults.clusters[`cluster_${props.selectedCluster}`]
      if (!data) return

      // 标准化数据用于雷达图
      const radarData = [
        { axis: '消费金额', value: Math.min(data.avg_spend / 10651, 1) },
        { axis: '购买频率', value: Math.min(data.avg_purchase_freq / 30.79, 1) },
        { axis: '社交活跃度', value: Math.min(data.avg_social_activity / 95.85, 1) },
        { axis: '购买率', value: data.purchase_rate }
      ]

      const radius = 120
      const centerX = width / 2
      const centerY = height / 2
      const levels = 5

      const g = svg.append('g')
        .attr('transform', `translate(${centerX},${centerY})`)

      // 绘制网格
      for (let i = 1; i <= levels; i++) {
        const r = (radius / levels) * i
        g.append('circle')
          .attr('r', r)
          .attr('fill', 'none')
          .attr('stroke', '#ddd')
          .attr('stroke-width', 1)
      }

      // 绘制轴线和标签
      radarData.forEach((d, i) => {
        const angle = (Math.PI * 2 * i) / radarData.length - Math.PI / 2
        const x = radius * Math.cos(angle)
        const y = radius * Math.sin(angle)

        g.append('line')
          .attr('x1', 0)
          .attr('y1', 0)
          .attr('x2', x)
          .attr('y2', y)
          .attr('stroke', '#ddd')
          .attr('stroke-width', 1)

        const labelX = (radius + 30) * Math.cos(angle)
        const labelY = (radius + 30) * Math.sin(angle)

        g.append('text')
          .attr('x', labelX)
          .attr('y', labelY)
          .attr('text-anchor', 'middle')
          .attr('font-size', '12px')
          .attr('fill', '#666')
          .text(d.axis)
      })

      // 绘制数据多边形
      const points = radarData.map((d, i) => {
        const angle = (Math.PI * 2 * i) / radarData.length - Math.PI / 2
        const r = (radius / levels) * levels * d.value
        return [r * Math.cos(angle), r * Math.sin(angle)]
      })

      const line = d3.line()
      const pathData = line(points) + 'Z'

      g.append('path')
        .attr('d', pathData)
        .attr('fill', clusterColors[props.selectedCluster])
        .attr('fill-opacity', 0.3)
        .attr('stroke', clusterColors[props.selectedCluster])
        .attr('stroke-width', 2)

      // 添加数据点
      points.forEach((point, i) => {
        g.append('circle')
          .attr('cx', point[0])
          .attr('cy', point[1])
          .attr('r', 4)
          .attr('fill', clusterColors[props.selectedCluster])
      })

      // 添加标题
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', 20)
        .attr('text-anchor', 'middle')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .attr('fill', '#333')
        .text(`${clusterNames[props.selectedCluster]} (${data.user_count.toLocaleString()}人)`)

      // 添加统计信息
      const stats = [
        `平均消费: ¥${data.avg_spend.toFixed(0)}`,
        `购买频率: ${data.avg_purchase_freq.toFixed(1)}次`,
        `社交活跃度: ${data.avg_social_activity.toFixed(1)}`,
        `购买率: ${(data.purchase_rate * 100).toFixed(1)}%`
      ]

      stats.forEach((stat, i) => {
        svg.append('text')
          .attr('x', 10)
          .attr('y', height - 10 - (stats.length - i - 1) * 18)
          .attr('font-size', '12px')
          .attr('fill', '#666')
          .text(stat)
      })
    }

    onMounted(() => {
      drawRadar()
    })

    watch(() => [props.selectedCluster, props.analysisResults], () => {
      drawRadar()
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
.cluster-detail {
  width: 100%;
}

h2 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
}

svg {
  width: 100%;
  height: auto;
}
</style>
