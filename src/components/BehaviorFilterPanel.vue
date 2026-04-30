<template>
  <div class="filter-panel">
    <!-- Age group filter -->
    <div class="filter-group">
      <div class="filter-label">年龄段</div>
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: activeFilter === 'all' && filterType === 'age' }]"
          @click="selectFilter('age', 'all')"
        >
          全部
        </button>
        <button
          v-for="age in ageGroups"
          :key="age"
          :class="['filter-btn', { active: activeFilter === `age_${age}` }]"
          @click="selectFilter('age', `age_${age}`)"
        >
          {{ age }}
        </button>
      </div>
    </div>

    <!-- Gender filter -->
    <div class="filter-group">
      <div class="filter-label">性别</div>
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: activeFilter === 'all' && filterType === 'gender' }]"
          @click="selectFilter('gender', 'all')"
        >
          全部
        </button>
        <button
          :class="['filter-btn', { active: activeFilter === 'gender_male' }]"
          @click="selectFilter('gender', 'gender_male')"
        >
          男性
        </button>
        <button
          :class="['filter-btn', { active: activeFilter === 'gender_female' }]"
          @click="selectFilter('gender', 'gender_female')"
        >
          女性
        </button>
      </div>
    </div>

    <!-- User level filter -->
    <div class="filter-group">
      <div class="filter-label">用户等级</div>
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: activeFilter === 'all' && filterType === 'level' }]"
          @click="selectFilter('level', 'all')"
        >
          全部
        </button>
        <button
          v-for="level in userLevels"
          :key="level"
          :class="['filter-btn', { active: activeFilter === `level_${level}` }]"
          @click="selectFilter('level', `level_${level}`)"
        >
          {{ level }}级
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  props: {
    userLevels: {
      type: Array,
      default: () => []
    }
  },
  emits: ['filter-change'],
  setup(props, { emit }) {
    const ageGroups = ['18-25', '26-35', '36-45', '46+']

    const filterType = ref('age')
    const activeFilter = ref('all')

    const selectFilter = (type, filter) => {
      filterType.value = type
      activeFilter.value = filter

      const segmentKey = filter === 'all' ? 'all' : filter
      emit('filter-change', segmentKey)
    }

    return {
      ageGroups,
      filterType,
      activeFilter,
      selectFilter
    }
  }
}
</script>

<style scoped>
.filter-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
  width: 100%;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: nowrap;
}

.filter-label {
  font-size: 16px;
  color: var(--text-primary, white);
  font-weight: 600;
  min-width: 100px;
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.6));
  white-space: nowrap;
}

.filter-buttons {
  display: flex;
  gap: 12px;
  flex: 1;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 12px 24px;
  border: 2px solid var(--border-color, rgba(0, 212, 255, 0.5));
  background: var(--bg-btn, rgba(10, 14, 39, 0.6));
  backdrop-filter: blur(10px);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-accent, #00d4ff);
  box-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.2));
  white-space: nowrap;
  flex: 1;
  min-width: 80px;
}

.filter-btn:hover {
  border-color: var(--border-hover, #00d4ff);
  background: rgba(0, 212, 255, 0.1);
  transform: translateY(-1px);
  box-shadow: 0 0 15px var(--shadow-glow, rgba(0, 212, 255, 0.4)), inset 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.1));
}

.filter-btn.active {
  background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
  color: white;
  border-color: #00d4ff;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.6), 0 0 40px rgba(124, 58, 237, 0.3);
  transform: translateY(-1px);
}
</style>
