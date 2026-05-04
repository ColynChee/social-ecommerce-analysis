<template>
  <div class="analysis-card">
    <div class="section-header">
      <div>
        <h2>用户行为路径分析</h2>
        <p>将浏览、社交互动、加购、领券、用券和购买串联起来，观察用户从兴趣到购买的转化路径。</p>
      </div>
    </div>

    <div v-if="!data" class="empty">数据加载中...</div>

    <template v-else>
      <div class="summary-grid">
        <div
          v-for="item in funnelData"
          :key="item.stage || item.step"
          class="summary-card"
        >
          <div class="summary-label">{{ item.stage || item.step }}</div>
          <div class="summary-value">{{ formatNumber(item.value ?? item.count) }}</div>
        </div>
      </div>

      <div class="chart-block">
        <h3>浏览到购买的行为流向</h3>
        <p class="hint">线条越宽，代表经过该路径的用户记录越多。</p>

        <svg
          class="path-svg"
          :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <linearGradient id="pathGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#00d4ff" />
              <stop offset="100%" stop-color="#7c3aed" />
            </linearGradient>
          </defs>

          <path
            v-for="(link, index) in visualLinks"
            :key="index"
            :d="link.path"
            fill="none"
            stroke="url(#pathGradient)"
            :stroke-width="link.width"
            stroke-opacity="0.45"
            stroke-linecap="round"
          />

          <g
            v-for="node in visualNodes"
            :key="node.name"
          >
            <rect
              :x="node.x - 56"
              :y="node.y - 20"
              width="112"
              height="40"
              rx="12"
              class="node-box"
            />
            <text
              :x="node.x"
              :y="node.y + 5"
              text-anchor="middle"
              class="node-text"
            >
              {{ node.name }}
            </text>
          </g>
        </svg>
      </div>

      <div class="chart-block">
        <h3>典型路径排行榜</h3>

        <div class="ranking-table">
          <div class="ranking-header">
            <span>路径</span>
            <span>记录数</span>
            <span>购买率</span>
          </div>

          <div
            v-for="item in topPaths"
            :key="item.path"
            class="ranking-row"
          >
            <span class="path-name">{{ item.path }}</span>
            <span>{{ formatNumber(item.count) }}</span>
            <span :class="{ positive: item.purchase_rate > 0 }">
              {{ formatPercent(item.purchase_rate) }}
            </span>
          </div>
        </div>
      </div>

      <div class="insight-box">
        <h3>这个模块回答的问题</h3>
        <p>
          该模块用于识别用户从浏览到购买的典型行为路径。
          如果“互动 → 加购 → 用券 → 购买”的路径转化率更高，说明社交互动和优惠行为可能共同推动购买转化。
        </p>
      </div>
    </template>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'BehaviorPathAnalysis',
  props: {
    data: {
      type: Object,
      default: null
    },
    isDark: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    const svgWidth = 920
    const svgHeight = 420

    const funnelData = computed(() => {
      if (!props.data || !props.data.funnel) return []
      return props.data.funnel
    })

    const rawLinks = computed(() => {
      if (!props.data) return []

      if (Array.isArray(props.data.sankey_links)) {
        return props.data.sankey_links
      }

      if (props.data.sankey && Array.isArray(props.data.sankey.links)) {
        return props.data.sankey.links
      }

      return []
    })

    const topPaths = computed(() => {
      if (!props.data || !Array.isArray(props.data.path_ranking)) return []
      return props.data.path_ranking.slice(0, 8)
    })

    const nodeOrder = [
      '浏览',
      '社交互动',
      '未互动',
      '加购物车',
      '未加购',
      '领券',
      '未领券',
      '用券',
      '未用券',
      '购买',
      '未购买'
    ]

    const visualNodes = computed(() => {
      const usedNames = new Set()
      rawLinks.value.forEach(link => {
        usedNames.add(link.source)
        usedNames.add(link.target)
      })

      const names = nodeOrder.filter(name => usedNames.has(name))
      const columns = {
        '浏览': 0,
        '社交互动': 1,
        '未互动': 1,
        '加购物车': 2,
        '未加购': 2,
        '领券': 3,
        '未领券': 3,
        '用券': 4,
        '未用券': 4,
        '购买': 5,
        '未购买': 5
      }

      const grouped = {}

      names.forEach(name => {
        const col = columns[name] ?? 0
        if (!grouped[col]) grouped[col] = []
        grouped[col].push(name)
      })

      const nodes = []

      Object.keys(grouped).forEach(colKey => {
        const col = Number(colKey)
        const list = grouped[col]
        const x = 90 + col * 150
        const gap = svgHeight / (list.length + 1)

        list.forEach((name, index) => {
          nodes.push({
            name,
            x,
            y: gap * (index + 1)
          })
        })
      })

      return nodes
    })

    const nodeMap = computed(() => {
      const map = {}
      visualNodes.value.forEach(node => {
        map[node.name] = node
      })
      return map
    })

    const visualLinks = computed(() => {
      const links = rawLinks.value
      if (!links.length) return []

      const maxValue = Math.max(...links.map(link => Number(link.value || 0)), 1)

      return links
        .filter(link => nodeMap.value[link.source] && nodeMap.value[link.target])
        .map(link => {
          const source = nodeMap.value[link.source]
          const target = nodeMap.value[link.target]
          const midX = (source.x + target.x) / 2
          const path = `M ${source.x + 56} ${source.y} C ${midX} ${source.y}, ${midX} ${target.y}, ${target.x - 56} ${target.y}`

          return {
            path,
            width: Math.max(2, (Number(link.value || 0) / maxValue) * 28)
          }
        })
    })

    const formatNumber = (value) => {
      return Number(value || 0).toLocaleString()
    }

    const formatPercent = (value) => {
      return `${(Number(value || 0) * 100).toFixed(1)}%`
    }

    return {
      svgWidth,
      svgHeight,
      funnelData,
      visualNodes,
      visualLinks,
      topPaths,
      formatNumber,
      formatPercent
    }
  }
}
</script>

<style scoped>
.analysis-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  padding: 24px;
  color: var(--text-primary);
  box-shadow: 0 0 24px var(--shadow-glow);
}

.section-header {
  margin-bottom: 22px;
}

.section-header h2 {
  margin: 0 0 8px 0;
  color: var(--text-accent);
  font-size: 24px;
}

.section-header p {
  margin: 0;
  opacity: 0.8;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.summary-card {
  padding: 16px;
  border-radius: 14px;
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid var(--border-color);
}

.summary-label {
  opacity: 0.75;
  font-size: 14px;
}

.summary-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 800;
  color: var(--text-accent);
}

.chart-block {
  margin-top: 22px;
}

.chart-block h3 {
  margin-bottom: 8px;
}

.hint {
  font-size: 13px;
  opacity: 0.75;
  margin-bottom: 14px;
}

.path-svg {
  width: 100%;
  min-height: 360px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.node-box {
  fill: rgba(15, 23, 41, 0.92);
  stroke: var(--border-color);
  stroke-width: 1.5;
}

.node-text {
  fill: var(--text-primary);
  font-size: 14px;
  font-weight: 700;
}

.ranking-table {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ranking-header,
.ranking-row {
  display: grid;
  grid-template-columns: 1fr 110px 90px;
  gap: 12px;
  align-items: center;
}

.ranking-header {
  font-weight: 700;
  opacity: 0.8;
  padding: 10px 12px;
}

.ranking-row {
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
}

.path-name {
  line-height: 1.5;
}

.positive {
  color: var(--text-accent);
  font-weight: 700;
}

.insight-box {
  margin-top: 24px;
  padding: 16px;
  border-radius: 14px;
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid var(--border-color);
}

.insight-box h3 {
  margin: 0 0 8px 0;
  color: var(--text-accent);
}

.insight-box p {
  margin: 0;
  line-height: 1.7;
}

.empty {
  padding: 30px;
  text-align: center;
  opacity: 0.7;
}
</style>