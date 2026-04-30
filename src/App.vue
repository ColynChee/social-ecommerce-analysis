<template>
  <div class="app" :class="{ 'light-mode': !isDark }">
    <div class="header">
      <h1>社交电商用户行为分析</h1>
      <button class="theme-toggle" @click="isDark = !isDark" :title="isDark ? '切换浅色模式' : '切换深色模式'">
        {{ isDark ? '☀️' : '🌙' }}
      </button>
    </div>

    <!-- Tab navigation -->
    <div class="tab-nav">
      <button
        :class="['tab-btn', 'tab-overview', { active: activeTab === 'overview' }]"
        @click="activeTab = 'overview'"
      >
        数据总览
      </button>
      <button
        :class="['tab-btn', 'tab-age', { active: activeTab === 'age' }]"
        @click="activeTab = 'age'"
      >
        年龄分群
      </button>
      <button
        :class="['tab-btn', 'tab-behavior', { active: activeTab === 'behavior' }]"
        @click="activeTab = 'behavior'"
      >
        行为洞察
      </button>
    </div>

    <div class="container">
      <!-- Tab 1: Overview -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <!-- Main content -->
        <div class="main-grid">
          <!-- Metrics cards for overview (6 cards) -->
          <MetricsCard
            v-for="metric in getOverviewMetrics()"
            :key="metric.label"
            :metric="metric"
            :isDark="isDark"
          />
        </div>

        <!-- Charts grid -->
        <div class="charts-grid">
          <!-- Gender distribution -->
          <div class="gender-section">
            <GenderPie :data="overviewData" :isDark="isDark" />
          </div>

          <!-- Spend distribution -->
          <div class="spend-section" @click="expandedChart = 'spend'" style="cursor: pointer;">
            <SpendDistribution :data="overviewData" :isDark="isDark" />
          </div>

          <!-- Top categories -->
          <div class="category-section">
            <TopCategoriesCloud :data="overviewData" :isDark="isDark" />
          </div>

          <!-- Social scatter -->
          <div class="social-section" @click="expandedChart = 'social'" style="cursor: pointer;">
            <SocialScatter :data="overviewData" :isDark="isDark" />
          </div>
        </div>
      </div>

      <!-- Tab 2: Age groups -->
      <div v-if="activeTab === 'age'" class="tab-content">
        <!-- Age group selector label -->
        <div class="selector-label">年龄段筛选</div>

        <!-- Age group selector -->
        <div class="age-selector">
          <button
            v-for="age in ageGroups"
            :key="age"
            :class="['age-btn', { active: selectedAge === age }]"
            @click="selectedAge = age"
          >
            {{ age }}
          </button>
        </div>

        <!-- Main content -->
        <div class="main-grid">
          <!-- Metrics cards directly -->
          <MetricsCard
            v-for="metric in getMetrics(currentAgeData)"
            :key="metric.label"
            :metric="metric"
          />
        </div>

        <!-- Charts grid -->
        <div class="charts-grid">
          <!-- Gender distribution -->
          <div class="gender-section">
            <GenderPie :data="currentAgeData" :isDark="isDark" />
          </div>

          <!-- Spend distribution -->
          <div class="spend-section" @click="expandedChart = 'spend'" style="cursor: pointer;">
            <SpendDistribution :data="currentAgeData" :isDark="isDark" />
          </div>

          <!-- Top categories -->
          <div class="category-section">
            <TopCategoriesCloud :data="currentAgeData" :isDark="isDark" />
          </div>

          <!-- Social scatter -->
          <div class="social-section" @click="expandedChart = 'social'" style="cursor: pointer;">
            <SocialScatter :data="currentAgeData" :isDark="isDark" />
          </div>
        </div>
      </div>

      <!-- Tab 3: Behavior insights -->
      <div v-if="activeTab === 'behavior'" class="tab-content">
        <BehaviorFilterPanel :userLevels="userLevels" @filter-change="handleFilterChange" />

        <div class="behavior-charts-grid">
          <div class="behavior-chart-section">
            <SocialPurchaseSankey :data="currentBehaviorData" :isDark="isDark" />
          </div>
          <div class="behavior-chart-section">
            <BehaviorFunnel :data="currentBehaviorData" :isDark="isDark" />
          </div>
        </div>
      </div>
    </div>

    <!-- Expanded chart modal -->
    <div v-if="expandedChart" class="modal-overlay" @click="expandedChart = null">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="expandedChart = null">✕</button>
        <div class="modal-chart">
          <SpendDistribution
            v-if="expandedChart === 'spend' && activeTab === 'overview'"
            :data="overviewData"
            :isDark="isDark"
            :isExpanded="true"
            ageGroup="overview"
          />
          <SpendDistribution
            v-if="expandedChart === 'spend' && activeTab === 'age'"
            :data="currentAgeData"
            :isDark="isDark"
            :isExpanded="true"
            :ageGroup="selectedAge"
          />
          <SocialScatter
            v-if="expandedChart === 'social' && activeTab === 'overview'"
            :data="overviewData"
            :isDark="isDark"
            :isExpanded="true"
            ageGroup="overview"
          />
          <SocialScatter
            v-if="expandedChart === 'social' && activeTab === 'age'"
            :data="currentAgeData"
            :isDark="isDark"
            :isExpanded="true"
            :ageGroup="selectedAge"
          />
        </div>
      </div>
    </div>

    <div class="footer">
      <p>社交电商用户行为分析系统 | 数据驱动的消费洞察</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import MetricsCard from './components/MetricsCard.vue'
import GenderPie from './components/GenderPie.vue'
import SpendDistribution from './components/SpendDistribution.vue'
import TopCategoriesCloud from './components/TopCategoriesCloud.vue'
import SocialScatter from './components/SocialScatter.vue'
import BehaviorFilterPanel from './components/BehaviorFilterPanel.vue'
import SocialPurchaseSankey from './components/SocialPurchaseSankey.vue'
import BehaviorFunnel from './components/BehaviorFunnel.vue'

export default {
  components: {
    MetricsCard,
    GenderPie,
    SpendDistribution,
    TopCategoriesCloud,
    SocialScatter,
    BehaviorFilterPanel,
    SocialPurchaseSankey,
    BehaviorFunnel
  },
  setup() {
    const activeTab = ref('overview')
    const ageGroups = ['18-25', '26-35', '36-45', '46+']
    const selectedAge = ref('18-25')
    const analysisResults = ref(null)
    const currentBehaviorSegment = ref('all')
    const isDark = ref(true)
    const expandedChart = ref(null)

    const overviewData = computed(() => {
      if (!analysisResults.value) return null
      return analysisResults.value.overview
    })

    const currentAgeData = computed(() => {
      if (!analysisResults.value) return null
      return analysisResults.value.age_groups[selectedAge.value]
    })

    const currentBehaviorData = computed(() => {
      if (!analysisResults.value || !analysisResults.value.behavior_insights) return null
      return analysisResults.value.behavior_insights[currentBehaviorSegment.value]
    })

    const userLevels = computed(() => {
      if (!analysisResults.value || !analysisResults.value.user_levels) return []
      return analysisResults.value.user_levels
    })

    const getOverviewMetrics = () => {
      const data = overviewData.value
      if (!data) return []
      return [
        { label: '总用户数', value: data.total_users.toLocaleString(), icon: '👥' },
        { label: '总消费额', value: `¥${(data.total_spend / 10000).toFixed(1)}万`, icon: '💰' },
        { label: '总购买次数', value: `${(data.avg_purchase_freq * data.total_users).toFixed(0)}`, icon: '🛍️' },
        { label: '购买率', value: `${(data.purchase_rate * 100).toFixed(1)}%`, icon: '📊' },
        { label: '平均消费', value: `¥${data.avg_spend.toFixed(0)}`, icon: '💳' }
      ]
    }

    const getMetrics = (data) => {
      if (!data) return []
      return [
        { label: '用户数', value: data.user_count, icon: '👥' },
        { label: '平均消费', value: `¥${data.avg_spend.toFixed(0)}`, icon: '💰' },
        { label: '平均频率', value: `${data.avg_purchase_freq.toFixed(1)}次`, icon: '🛍️' },
        { label: '购买率', value: `${(data.purchase_rate * 100).toFixed(1)}%`, icon: '📊' },
        { label: '平均浏览次数', value: `${data.avg_pv.toFixed(1)}`, icon: '👀' }
      ]
    }

    const handleFilterChange = (segmentKey) => {
      currentBehaviorSegment.value = segmentKey
    }

    onMounted(async () => {
      try {
        const response = await fetch('/data/analysis_results.json')
        analysisResults.value = await response.json()
      } catch (error) {
        console.error('Failed to load data:', error)
      }
    })

    return {
      activeTab,
      ageGroups,
      selectedAge,
      overviewData,
      currentAgeData,
      currentBehaviorData,
      userLevels,
      getOverviewMetrics,
      getMetrics,
      handleFilterChange,
      isDark,
      expandedChart
    }
  }
}
</script>

<style scoped>
.app {
  --bg-primary: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1729 100%);
  --bg-card: rgba(15, 23, 41, 0.8);
  --bg-btn: rgba(10, 14, 39, 0.6);
  --text-primary: white;
  --text-accent: #00d4ff;
  --border-color: rgba(0, 212, 255, 0.3);
  --border-hover: rgba(0, 212, 255, 0.6);
  --shadow-glow: rgba(0, 212, 255, 0.2);
  --d3-text: white;
  --d3-axis: white;

  min-height: 100vh;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.app.light-mode {
  --bg-primary: #f0f4f8;
  --bg-card: white;
  --bg-btn: rgba(255, 255, 255, 0.9);
  --text-primary: #1a1a2e;
  --text-accent: #0099cc;
  --border-color: rgba(0, 153, 204, 0.3);
  --border-hover: rgba(0, 153, 204, 0.6);
  --shadow-glow: rgba(0, 153, 204, 0.15);
  --d3-text: #1a1a2e;
  --d3-axis: #666;
}

.header {
  background: linear-gradient(135deg, #0a0e27 0%, #1a1a4d 50%, #2d1b4e 100%);
  color: var(--text-primary);
  padding: 40px 20px 30px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
  border-bottom: 2px solid var(--border-color);
  box-shadow: 0 10px 40px rgba(0, 212, 255, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    repeating-linear-gradient(
      0deg,
      rgba(0, 212, 255, 0.03) 0px,
      rgba(0, 212, 255, 0.03) 1px,
      transparent 1px,
      transparent 2px
    ),
    repeating-linear-gradient(
      90deg,
      rgba(124, 58, 237, 0.03) 0px,
      rgba(124, 58, 237, 0.03) 1px,
      transparent 1px,
      transparent 2px
    );
  pointer-events: none;
}

.header::after {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.header h1 {
  font-size: 48px;
  margin-bottom: 0;
  font-weight: 800;
  letter-spacing: 3px;
  position: relative;
  z-index: 2;
  background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
  filter: drop-shadow(0 0 20px rgba(124, 58, 237, 0.2));
}

.light-mode .header {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 50%, #f0e8ff 100%);
  border-bottom-color: rgba(0, 212, 255, 0.2);
  box-shadow: 0 10px 40px rgba(0, 212, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.light-mode .header h1 {
  background: linear-gradient(135deg, #0099cc 0%, #6b3fb5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: none;
  filter: drop-shadow(0 0 10px rgba(0, 153, 204, 0.15));
}

.theme-toggle {
  position: absolute;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--bg-btn);
  border: 2px solid var(--border-color);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.theme-toggle:hover {
  border-color: var(--border-hover);
  box-shadow: 0 0 15px var(--shadow-glow);
  transform: translateY(-50%) scale(1.1);
}

.subtitle {
  font-size: 20px;
  opacity: 0.9;
  margin: 0;
  position: relative;
  z-index: 1;
  font-weight: 300;
  text-shadow: 0 0 10px rgba(124, 58, 237, 0.6);
}

.tab-nav {
  display: flex;
  gap: 30px;
  padding: 0 30px 40px 30px;
  justify-content: stretch;
  flex-wrap: nowrap;
}

.tab-btn {
  padding: 14px 32px;
  border: 2px solid var(--border-color);
  background: var(--bg-btn);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-accent);
  box-shadow: 0 0 15px var(--shadow-glow);
  flex: 1;
  min-width: 0;
}

.tab-btn:hover {
  border-color: var(--border-hover);
  background: rgba(0, 212, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 0 25px var(--shadow-glow), inset 0 0 15px var(--shadow-glow);
}

.tab-btn.active {
  background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%);
  color: white;
  border-color: #ff8c00;
  box-shadow: 0 0 30px rgba(255, 140, 0, 0.8), 0 0 60px rgba(255, 107, 0, 0.4);
  transform: translateY(-2px);
}

/* Tab-specific colors */
.tab-btn.tab-overview {
  border-color: rgba(255, 140, 0, 0.5);
  color: #ff8c00;
}

.tab-btn.tab-overview:hover {
  border-color: #ff8c00;
  background: rgba(255, 140, 0, 0.1);
  box-shadow: 0 0 25px rgba(255, 140, 0, 0.5), inset 0 0 15px rgba(255, 140, 0, 0.1);
}

.tab-btn.tab-overview.active {
  background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%);
  border-color: #ff8c00;
  box-shadow: 0 0 30px rgba(255, 140, 0, 0.8), 0 0 60px rgba(255, 107, 0, 0.4);
  color: white;
}

.tab-btn.tab-age {
  border-color: rgba(255, 165, 0, 0.5);
  color: #ffa500;
}

.tab-btn.tab-age:hover {
  border-color: #ffa500;
  background: rgba(255, 165, 0, 0.1);
  box-shadow: 0 0 25px rgba(255, 165, 0, 0.5), inset 0 0 15px rgba(255, 165, 0, 0.1);
}

.tab-btn.tab-age.active {
  background: linear-gradient(135deg, #ffa500 0%, #ff8c00 100%);
  border-color: #ffa500;
  box-shadow: 0 0 30px rgba(255, 165, 0, 0.8), 0 0 60px rgba(255, 140, 0, 0.4);
  color: white;
}

.tab-btn.tab-behavior {
  border-color: rgba(255, 184, 0, 0.5);
  color: #ffb800;
}

.tab-btn.tab-behavior:hover {
  border-color: #ffb800;
  background: rgba(255, 184, 0, 0.1);
  box-shadow: 0 0 25px rgba(255, 184, 0, 0.5), inset 0 0 15px rgba(255, 184, 0, 0.1);
}

.tab-btn.tab-behavior.active {
  background: linear-gradient(135deg, #ffb800 0%, #ffa500 100%);
  border-color: #ffb800;
  box-shadow: 0 0 30px rgba(255, 184, 0, 0.8), 0 0 60px rgba(255, 165, 0, 0.4);
  color: white;
}

.tab-btn.tab-overview.active {
  background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%);
  border-color: #ff8c00;
  box-shadow: 0 0 30px rgba(255, 140, 0, 0.8), 0 0 60px rgba(255, 107, 0, 0.4);
  color: white;
}

.tab-btn.tab-age {
  border-color: rgba(255, 165, 0, 0.5);
  color: #ffa500;
}

.tab-btn.tab-age:hover {
  border-color: #ffa500;
  background: rgba(255, 165, 0, 0.1);
  box-shadow: 0 0 25px rgba(255, 165, 0, 0.5), inset 0 0 15px rgba(255, 165, 0, 0.1);
}

.tab-btn.tab-age.active {
  background: linear-gradient(135deg, #ffa500 0%, #ff8c00 100%);
  border-color: #ffa500;
  box-shadow: 0 0 30px rgba(255, 165, 0, 0.8), 0 0 60px rgba(255, 140, 0, 0.4);
  color: white;
}

.tab-btn.tab-behavior {
  border-color: rgba(255, 184, 0, 0.5);
  color: #ffb800;
}

.tab-btn.tab-behavior:hover {
  border-color: #ffb800;
  background: rgba(255, 184, 0, 0.1);
  box-shadow: 0 0 25px rgba(255, 184, 0, 0.5), inset 0 0 15px rgba(255, 184, 0, 0.1);
}

.tab-btn.tab-behavior.active {
  background: linear-gradient(135deg, #ffb800 0%, #ffa500 100%);
  border-color: #ffb800;
  box-shadow: 0 0 30px rgba(255, 184, 0, 0.8), 0 0 60px rgba(255, 165, 0, 0.4);
  color: white;
}

.container {
  flex: 1;
  padding: 0 30px 0px 30px;
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
}

.tab-content {
  width: 100%;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  color: var(--text-accent);
  font-size: 24px;
  font-weight: 600;
}

.age-selector {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
  justify-content: space-between;
  flex-wrap: wrap;
}

.selector-label {
  font-size: 18px;
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 10px;
  text-shadow: 0 0 10px var(--shadow-glow);
}

.age-btn {
  padding: 14px 32px;
  border: 2px solid var(--border-color);
  background: var(--bg-btn);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-accent);
  box-shadow: 0 0 15px var(--shadow-glow);
  flex: 1;
  min-width: 150px;
}

.age-btn:hover {
  border-color: var(--border-hover);
  background: rgba(0, 212, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 0 25px var(--shadow-glow), inset 0 0 15px var(--shadow-glow);
}

.age-btn.active {
  background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
  color: white;
  border-color: #00d4ff;
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.8), 0 0 60px rgba(124, 58, 237, 0.4);
  transform: translateY(-2px);
}

.main-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 32px;
  margin-bottom: 40px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr 1.4fr 1.3fr;
  gap: 32px;
  margin-bottom: 50px;
  max-width: 2500px;
  margin-left: auto;
  margin-right: auto;
}

.behavior-charts-grid {
  display: grid;
  grid-template-columns: 1.1fr 1.1fr;
  gap: 32px;
  margin-bottom: 50px;
  max-width: 2500px;
  margin-left: auto;
  margin-right: auto;
}

.metrics-section,
.gender-section,
.spend-section,
.category-section,
.social-section,
.behavior-chart-section {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 0 20px var(--shadow-glow), inset 0 0 20px rgba(0, 212, 255, 0.05);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.metrics-section:hover,
.gender-section:hover,
.spend-section:hover,
.category-section:hover,
.social-section:hover,
.behavior-chart-section:hover {
  transform: translateY(-4px);
  box-shadow: 0 0 40px var(--shadow-glow), 0 0 80px rgba(124, 58, 237, 0.2), inset 0 0 20px var(--shadow-glow);
  border-color: var(--border-hover);
}

.footer {
  background: var(--bg-btn);
  backdrop-filter: blur(10px);
  color: var(--text-accent);
  text-align: center;
  padding: 24px;
  font-size: 14px;
  margin-top: auto;
  border-top: 1px solid var(--border-color);
  box-shadow: 0 0 20px var(--shadow-glow);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  padding: 10px;
}

.modal-content {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 20px;
  padding: 70px 20px 20px 20px;
  width: 100%;
  height: 100%;
  max-width: 95vw;
  max-height: 95vh;
  overflow: auto;
  position: relative;
  box-shadow: 0 0 50px rgba(0, 212, 255, 0.3), 0 0 100px rgba(124, 58, 237, 0.2);
  display: flex;
  flex-direction: column;
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(0, 212, 255, 0.2);
  border: 2px solid var(--border-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 1001;
}

.modal-close:hover {
  background: rgba(0, 212, 255, 0.4);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
  transform: scale(1.1);
}

.modal-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  overflow: auto;
}

@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}
</style>
