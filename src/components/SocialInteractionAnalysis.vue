<template>
  <div class="analysis-card">
    <div class="section-header">
      <div>
        <h2>社交互动与购买关系</h2>
        <p>分析点赞、评论、分享和互动率是否会提升加购、用券和购买行为。</p>
      </div>

      <select v-model="selectedMetric" class="metric-select">
        <option value="like_groups">点赞数</option>
        <option value="comment_groups">评论数</option>
        <option value="share_groups">分享数</option>
        <option value="interaction_rate_groups">互动率</option>
        <option value="purchase_intent_groups">购买意向</option>
      </select>
    </div>

    <div v-if="!data" class="empty">数据加载中...</div>

    <template v-else>
      <div class="chart-block">
        <h3>{{ metricTitle }} 分组购买率</h3>

        <div class="bar-chart">
          <div
            v-for="item in currentGroups"
            :key="String(item.group)"
            class="bar-row"
          >
            <div class="bar-label">{{ formatGroup(item.group) }}</div>

            <div class="bar-track">
              <div
                class="bar-fill purchase"
                :style="{ width: `${Math.max(Number(item.purchase_rate || 0) * 100, 1)}%` }"
              ></div>
            </div>

            <div class="bar-value">
              {{ formatPercent(item.purchase_rate) }}
            </div>

            <div class="bar-count">
              n={{ formatNumber(item.count) }}
            </div>
          </div>
        </div>
      </div>

      <div class="chart-block">
        <h3>互动行为相关性矩阵</h3>
        <p class="hint">
          数值越接近 1，说明两个指标之间的正相关越强；数值越接近 -1，说明负相关越强。
          重点观察点赞、评论、分享、加购、用券和购买之间的关系。
        </p>

        <div v-if="correlationRows.length" class="heatmap">
          <div
            class="heatmap-grid"
            :style="{ gridTemplateColumns: `110px repeat(${correlationColumns.length}, 64px)` }"
          >
            <div class="heatmap-corner"></div>

            <div
              v-for="col in correlationColumns"
              :key="col"
              class="heatmap-label top"
            >
              {{ shortName(col) }}
            </div>

            <template v-for="row in correlationRows" :key="row.name">
              <div class="heatmap-label left">{{ shortName(row.name) }}</div>

              <div
                v-for="cell in row.values"
                :key="row.name + '-' + cell.name"
                class="heatmap-cell"
                :style="cellStyle(cell.value)"
                :title="`${shortName(row.name)} 与 ${shortName(cell.name)}：${Number(cell.value || 0).toFixed(3)}`"
              >
                {{ Number(cell.value || 0).toFixed(2) }}
              </div>
            </template>
          </div>
        </div>

        <div v-else class="matrix-empty">
          暂时没有读取到相关性矩阵数据。当前分组购买率图仍可用于分析社交互动与购买率的关系。
        </div>
      </div>

      <div class="insight-box">
        <h3>这个模块回答的问题</h3>
        <p>
          该模块用于判断社交电商中的“种草行为”是否真的与购买转化有关。
          如果高点赞、高评论、高分享或高互动率组的购买率更高，说明社交互动可能对购买行为有促进作用。
        </p>
      </div>
    </template>
  </div>
</template>

<script>
import { computed, ref } from 'vue'

export default {
  name: 'SocialInteractionAnalysis',
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
    const selectedMetric = ref('like_groups')

    const metricTitles = {
      like_groups: '点赞数',
      comment_groups: '评论数',
      share_groups: '分享数',
      interaction_rate_groups: '互动率',
      purchase_intent_groups: '购买意向'
    }

    const metricTitle = computed(() => {
      return metricTitles[selectedMetric.value] || '互动指标'
    })

    const currentGroups = computed(() => {
      if (!props.data || !props.data[selectedMetric.value]) return []
      return props.data[selectedMetric.value]
    })

    const normalizedCorrelationMatrix = computed(() => {
      if (!props.data || !props.data.correlation_matrix) return {}

      const raw = props.data.correlation_matrix

      // 兼容当前 generate_analysis.py 输出格式：
      // {
      //   columns: [...],
      //   matrix: [[...]],
      //   items: [...]
      // }
      if (
        Array.isArray(raw.columns) &&
        Array.isArray(raw.matrix) &&
        Array.isArray(raw.items)
      ) {
        const matrix = {}

        raw.items.forEach((rowName, rowIndex) => {
          matrix[rowName] = {}

          raw.columns.forEach((colName, colIndex) => {
            matrix[rowName][colName] = Number(raw.matrix[rowIndex]?.[colIndex] ?? 0)
          })
        })

        return matrix
      }

      // 兼容 pandas split / tight 风格：
      // {
      //   columns: [...],
      //   index: [...],
      //   data: [[...]]
      // }
      if (
        Array.isArray(raw.columns) &&
        Array.isArray(raw.index) &&
        Array.isArray(raw.data)
      ) {
        const matrix = {}

        raw.index.forEach((rowName, rowIndex) => {
          matrix[rowName] = {}

          raw.columns.forEach((colName, colIndex) => {
            matrix[rowName][colName] = Number(raw.data[rowIndex]?.[colIndex] ?? 0)
          })
        })

        return matrix
      }

      // 兼容普通 dict-of-dict 格式：
      // {
      //   "pv_count": {"pv_count": 1, "like_num": 0.2},
      //   "like_num": {"pv_count": 0.2, "like_num": 1}
      // }
      const rawKeys = Object.keys(raw)
      const looksLikeDictOfDict =
        rawKeys.length > 0 &&
        rawKeys.every(key => {
          return raw[key] && typeof raw[key] === 'object' && !Array.isArray(raw[key])
        }) &&
        !raw.columns &&
        !raw.index &&
        !raw.data &&
        !raw.items &&
        !raw.matrix

      if (looksLikeDictOfDict) {
        return raw
      }

      return {}
    })

    const allMatrixColumns = computed(() => {
      const matrix = normalizedCorrelationMatrix.value
      const rowNames = Object.keys(matrix)
      const colSet = new Set(rowNames)

      rowNames.forEach(rowName => {
        Object.keys(matrix[rowName] || {}).forEach(colName => {
          colSet.add(colName)
        })
      })

      const preferredOrder = [
        'pv_count',
        'like_num',
        'comment_num',
        'share_num',
        'collect_num',
        'add2cart',
        'coupon_used',
        'interaction_rate',
        'purchase_intent',
        'label'
      ]

      return preferredOrder.filter(col => colSet.has(col))
    })

    const correlationColumns = computed(() => {
      return allMatrixColumns.value
    })

    const correlationRows = computed(() => {
      const matrix = normalizedCorrelationMatrix.value
      const cols = allMatrixColumns.value

      if (!cols.length) return []

      return cols.map(rowName => ({
        name: rowName,
        values: cols.map(colName => ({
          name: colName,
          value: Number(matrix[rowName]?.[colName] ?? 0)
        }))
      }))
    })

    const shortName = (name) => {
      const map = {
        pv_count: '浏览',
        like_num: '点赞',
        comment_num: '评论',
        share_num: '分享',
        collect_num: '收藏',
        add2cart: '加购',
        coupon_used: '用券',
        interaction_rate: '互动率',
        purchase_intent: '购买意向',
        label: '购买'
      }

      return map[name] || name
    }

    const formatPercent = (value) => {
      const num = Number(value || 0)
      return `${(num * 100).toFixed(1)}%`
    }

    const formatNumber = (value) => {
      return Number(value || 0).toLocaleString()
    }

    const formatGroup = (group) => {
      return String(group)
        .replace('(-0.001,', '0 -')
        .replace('[', '')
        .replace(']', '')
        .replace('(', '')
        .replace(')', '')
    }

    const cellStyle = (value) => {
      const num = Number(value || 0)
      const intensity = Math.min(Math.abs(num), 1)
      const opacity = 0.12 + intensity * 0.78

      if (num < 0) {
        return {
          background: `rgba(124, 58, 237, ${opacity})`,
          color: intensity > 0.45 ? '#ffffff' : 'var(--text-primary)'
        }
      }

      return {
        background: `rgba(0, 212, 255, ${opacity})`,
        color: intensity > 0.45 ? '#001018' : 'var(--text-primary)'
      }
    }

    return {
      selectedMetric,
      metricTitle,
      currentGroups,
      correlationColumns,
      correlationRows,
      shortName,
      formatPercent,
      formatNumber,
      formatGroup,
      cellStyle
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
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
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

.metric-select {
  background: var(--bg-btn);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 10px 14px;
  outline: none;
}

.chart-block {
  margin-top: 22px;
}

.chart-block h3 {
  margin-bottom: 12px;
  color: var(--text-primary);
}

.hint {
  font-size: 13px;
  opacity: 0.75;
  margin-bottom: 14px;
  line-height: 1.6;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-row {
  display: grid;
  grid-template-columns: 120px 1fr 70px 90px;
  gap: 12px;
  align-items: center;
}

.bar-label {
  font-size: 14px;
  opacity: 0.9;
}

.bar-track {
  height: 16px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
}

.bar-fill.purchase {
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
}

.bar-value {
  font-weight: 700;
  color: var(--text-accent);
}

.bar-count {
  font-size: 12px;
  opacity: 0.7;
}

.heatmap {
  overflow-x: auto;
  padding-bottom: 8px;
  margin-top: 12px;
}

.heatmap-grid {
  display: grid;
  gap: 4px;
  align-items: center;
  width: max-content;
  min-width: 100%;
}

.heatmap-label {
  font-size: 12px;
  opacity: 0.85;
}

.heatmap-label.top {
  text-align: center;
  transform: rotate(-25deg);
  transform-origin: center;
  min-height: 42px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.heatmap-label.left {
  text-align: right;
  padding-right: 8px;
  white-space: nowrap;
}

.heatmap-cell {
  width: 64px;
  height: 38px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.matrix-empty {
  padding: 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  opacity: 0.8;
  line-height: 1.6;
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

@media (max-width: 900px) {
  .section-header {
    flex-direction: column;
  }

  .bar-row {
    grid-template-columns: 90px 1fr 60px;
  }

  .bar-count {
    display: none;
  }
}
</style>