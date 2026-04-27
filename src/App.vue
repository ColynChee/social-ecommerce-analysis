<template>
  <div class="app">
    <header class="header">
      <h1>社交电商用户行为分析</h1>
      <p class="subtitle">用户分群与商品内容特征探索</p>
    </header>

    <div class="container">
      <div class="main-content">
        <div class="scatter-section">
          <ClusterScatter
            :data="clusterData"
            :selected-cluster="selectedCluster"
            @cluster-selected="handleClusterSelected"
          />
        </div>

        <div class="detail-section">
          <ClusterDetail
            :cluster-data="clusterData"
            :selected-cluster="selectedCluster"
            :analysis-results="analysisResults"
          />
        </div>
      </div>

      <div class="feature-section">
        <ContentFeature
          :selected-cluster="selectedCluster"
          :analysis-results="analysisResults"
        />
      </div>
    </div>

    <footer class="footer">
      <p>数据来源：社交电商平台用户行为数据 | 基于100K条记录分析</p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import ClusterScatter from './components/ClusterScatter.vue'
import ClusterDetail from './components/ClusterDetail.vue'
import ContentFeature from './components/ContentFeature.vue'

export default {
  components: {
    ClusterScatter,
    ClusterDetail,
    ContentFeature
  },
  setup() {
    const clusterData = ref([])
    const analysisResults = ref(null)
    const selectedCluster = ref(null)

    onMounted(async () => {
      try {
        // 加载用户分群数据
        const csvResponse = await fetch('./data/user_clusters.csv')
        const csvText = await csvResponse.text()
        clusterData.value = parseCSV(csvText)

        // 加载分析结果
        const jsonResponse = await fetch('./data/analysis_results.json')
        analysisResults.value = await jsonResponse.json()

        // 默认选择第一个群体
        selectedCluster.value = 0
      } catch (error) {
        console.error('数据加载失败:', error)
      }
    })

    const parseCSV = (csv) => {
      const lines = csv.trim().split('\n')
      const headers = lines[0].split(',')
      return lines.slice(1).map(line => {
        const values = line.split(',')
        const obj = {}
        headers.forEach((header, i) => {
          obj[header] = isNaN(values[i]) ? values[i] : parseFloat(values[i])
        })
        return obj
      })
    }

    const handleClusterSelected = (clusterId) => {
      selectedCluster.value = clusterId
    }

    return {
      clusterData,
      analysisResults,
      selectedCluster,
      handleClusterSelected
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header h1 {
  font-size: 32px;
  margin-bottom: 8px;
  font-weight: 600;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.container {
  flex: 1;
  padding: 30px 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.scatter-section,
.detail-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.feature-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.footer {
  background: #333;
  color: #999;
  text-align: center;
  padding: 20px;
  font-size: 14px;
  margin-top: auto;
}

@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>
