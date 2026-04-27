<template>
  <div class="content-feature">
    <h2>商品内容特征分析</h2>
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="['tab', { active: activeTab === tab }]"
        @click="activeTab = tab"
      >
        {{ tabLabels[tab] }}
      </button>
    </div>
    <svg ref="svgRef" :width="width" :height="height"></svg>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

export default {
  props: {
    selectedCluster: Number,
    analysisResults: Object
  },
  setup(props) {
    const svgRef = ref(null)
    const width = 1000
    const height = 300
    const activeTab = ref('discount')
    const tabs = ['discount', 'image']
    const tabLabels = {
      discount: '折扣率与购买率',
      image: '图片数量与互动率'
    }
    const margin = { top: 20, right: 20, bottom: 40, left: 50 }

    const drawChart = () => {
      if (!svgRef.value || !props.analysisResults) return

      const svg = d3.select(svgRef.value)
      svg.selectAll('*').remove()

      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom

      let chartData = []
      let yLabel = ''
      let yMax = 1

      if (activeTab.value === 'discount') {
        const discountData = props.analysisResults.content_features.discount
        chartData = [
          { label: '无折扣', value: discountData.label.none },
          { label: '0-10%', value: discountData.label['0-10%'] },
          { label: '10-20%', value: discountData.label['10-20%'] },
          { label: '20%+', value: discountData.label['20%+'] }
        ]
        yLabel = '购买率'
        yMax = 0.55
      } else {
        const imageData = props.analysisResults.content_features.image_count
        chartData = [
          { label: '1-2张', value: imageData.interaction_rate['1-2'] },
          { label: '3-4张', value: imageData.interaction_rate['3-4'] },
          { label: '5-6张', value: imageData.interaction_rate['5-6'] },
          { label: '7+张', value: imageData.interaction_rate['7+'] }
        ]
        yLabel = '互动率'
        yMax = 20
      }

      const xScale = d3.scaleBand()
        .domain(chartData.map(d => d.label))
        .range([0, innerWidth])
        .padding(0.3)

      const yScale = d3.scaleLinear()
        .domain([0, yMax])
        .range([innerHeight, 0])

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // 网格线
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
        .text(activeTab.value === 'discount' ? '折扣率分组' : '图片数量分组')

      // Y轴
      g.append('g')
        .call(d3.axisLeft(yScale))
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -innerHeight / 2)
        .attr('y', -35)
        .attr('fill', '#333')
        .attr('text-anchor', 'middle')
        .text(yLabel)

      // 绘制柱子
      g.selectAll('.bar')
        .data(chartData)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => xScale(d.label))
        .attr('y', d => yScale(d.value))
        .attr('width', xScale.bandwidth())
        .attr('height', d => innerHeight - yScale(d.value))
        .attr('fill', (d, i) => {
          if (activeTab.value === 'discount' && i === 2) return '#FF6B6B' // 10-20%最高
          return '#667eea'
        })
        .attr('opacity', 0.8)
        .on('mouseover', function(event, d) {
          d3.select(this).attr('opacity', 1)

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
            .html(`${d.label}<br/>${yLabel}: ${(d.value * 100).toFixed(1)}%`)

          setTimeout(() => tooltip.remove(), 3000)
        })
        .on('mouseout', function() {
          d3.select(this).attr('opacity', 0.8)
        })

      // 添加数值标签
      g.selectAll('.label')
        .data(chartData)
        .enter()
        .append('text')
        .attr('class', 'label')
        .attr('x', d => xScale(d.label) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.value) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px')
        .attr('fill', '#333')
        .text(d => (d.value * 100).toFixed(1) + '%')

      // 添加关键洞见
      if (activeTab.value === 'discount') {
        svg.append('text')
          .attr('x', 10)
          .attr('y', height - 10)
          .attr('font-size', '12px')
          .attr('fill', '#FF6B6B')
          .attr('font-weight', 'bold')
          .text('💡 关键发现：10-20%折扣购买率最高（51.7%），比无折扣提升21%')
      }
    }

    onMounted(() => {
      drawChart()
    })

    watch(() => [activeTab.value, props.analysisResults], () => {
      drawChart()
    }, { deep: true })

    return {
      svgRef,
      width,
      height,
      activeTab,
      tabs,
      tabLabels
    }
  }
}
</script>

<style scoped>
.content-feature {
  width: 100%;
}

h2 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.tab {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.tab:hover {
  border-color: #667eea;
  color: #667eea;
}

.tab.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

svg {
  width: 100%;
  height: auto;
}

:deep(.grid) {
  stroke: #ddd;
}

:deep(.bar) {
  transition: opacity 0.2s ease;
}
</style>
