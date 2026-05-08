<template>
  <div class="filter-panel">
    <!-- 年龄段筛选 -->
    <div class="filter-group">
      <div class="filter-label">年龄段</div>
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: activeAge === 'all' }]"
          @click="selectAge('all')"
        >
          全部
        </button>
        <button
          v-for="age in ageGroups"
          :key="age"
          :class="['filter-btn', { active: activeAge === age }]"
          @click="selectAge(age)"
        >
          {{ age }}
        </button>
      </div>
    </div>

    <!-- 性别筛选 -->
    <div class="filter-group">
      <div class="filter-label">性别</div>
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: activeGender === 'all' }]"
          @click="selectGender('all')"
        >
          全部
        </button>
        <button
          :class="['filter-btn', { active: activeGender === 'male' }]"
          @click="selectGender('male')"
        >
          男性
        </button>
        <button
          :class="['filter-btn', { active: activeGender === 'female' }]"
          @click="selectGender('female')"
        >
          女性
        </button>
      </div>
    </div>

    <!-- 用户等级筛选 -->
    <div class="filter-group">
      <div class="filter-label">用户等级</div>
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: activeLevel === 'all' }]"
          @click="selectLevel('all')"
        >
          全部
        </button>
        <button
          v-for="level in userLevels"
          :key="level"
          :class="['filter-btn', { active: activeLevel === String(level) }]"
          @click="selectLevel(String(level))"
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

    // 三个维度独立的视觉状态
    const activeAge = ref('all')
    const activeGender = ref('all')
    const activeLevel = ref('all')

    const selectAge = (value) => {
      activeAge.value = value
      // 重置其他维度为 'all'，保持与原有单选行为一致
      activeGender.value = 'all'
      activeLevel.value = 'all'
      const segmentKey = value === 'all' ? 'all' : `age_${value}`
      emit('filter-change', segmentKey)
    }

    const selectGender = (value) => {
      activeGender.value = value
      activeAge.value = 'all'
      activeLevel.value = 'all'
      const segmentKey = value === 'all' ? 'all' : `gender_${value}`
      emit('filter-change', segmentKey)
    }

    const selectLevel = (value) => {
      activeLevel.value = value
      activeAge.value = 'all'
      activeGender.value = 'all'
      const segmentKey = value === 'all' ? 'all' : `level_${value}`
      emit('filter-change', segmentKey)
    }

    return {
      ageGroups,
      activeAge,
      activeGender,
      activeLevel,
      selectAge,
      selectGender,
      selectLevel
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
