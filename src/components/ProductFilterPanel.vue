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

    <!-- 当前筛选条件摘要 -->
    <div v-if="hasActiveFilter" class="filter-summary">
      <span class="summary-label">当前筛选：</span>
      <span v-if="activeAge !== 'all'" class="summary-tag">{{ activeAge }}岁</span>
      <span v-if="activeGender !== 'all'" class="summary-tag">{{ activeGender === 'male' ? '男性' : '女性' }}</span>
      <span v-if="activeLevel !== 'all'" class="summary-tag">Lv.{{ activeLevel }}</span>
      <button class="reset-btn" @click="resetAll">重置</button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ProductFilterPanel',
  props: {
    userLevels: {
      type: Array,
      default: () => []
    }
  },
  emits: ['filter-change'],
  setup(props, { emit }) {
    const ageGroups = ['18-25', '26-35', '36-45', '46+']

    // 三个维度独立的状态
    const activeAge = ref('all')
    const activeGender = ref('all')
    const activeLevel = ref('all')

    // 是否有任意维度被激活
    const hasActiveFilter = computed(() => {
      return activeAge.value !== 'all' ||
             activeGender.value !== 'all' ||
             activeLevel.value !== 'all'
    })

    // 统一的 emit 函数：将三个维度打包为对象
    const emitFilter = () => {
      emit('filter-change', {
        age: activeAge.value,
        gender: activeGender.value,
        level: activeLevel.value
      })
    }

    const selectAge = (value) => {
      activeAge.value = value
      emitFilter()
    }

    const selectGender = (value) => {
      activeGender.value = value
      emitFilter()
    }

    const selectLevel = (value) => {
      activeLevel.value = value
      emitFilter()
    }

    const resetAll = () => {
      activeAge.value = 'all'
      activeGender.value = 'all'
      activeLevel.value = 'all'
      emitFilter()
    }

    return {
      ageGroups,
      activeAge,
      activeGender,
      activeLevel,
      hasActiveFilter,
      selectAge,
      selectGender,
      selectLevel,
      resetAll
    }
  }
}
</script>

<style scoped>
.filter-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  gap: 10px;
  flex: 1;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 10px 20px;
  border: 2px solid var(--border-color, rgba(0, 212, 255, 0.5));
  background: var(--bg-btn, rgba(10, 14, 39, 0.6));
  backdrop-filter: blur(10px);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-accent, #00d4ff);
  box-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.2));
  white-space: nowrap;
  flex: 1;
  min-width: 70px;
}

.filter-btn:hover {
  border-color: var(--border-hover, #00d4ff);
  background: rgba(0, 212, 255, 0.1);
  transform: translateY(-1px);
  box-shadow: 0 0 15px var(--shadow-glow, rgba(0, 212, 255, 0.4)),
              inset 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.1));
}

.filter-btn.active {
  background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
  color: white;
  border-color: #00d4ff;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.6), 0 0 40px rgba(124, 58, 237, 0.3);
  transform: translateY(-1px);
}

/* 筛选摘要 */
.filter-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  flex-wrap: wrap;
}

.summary-label {
  font-size: 13px;
  color: var(--text-primary, white);
  opacity: 0.7;
}

.summary-tag {
  padding: 3px 10px;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  font-size: 12px;
  color: #00d4ff;
  font-weight: 500;
}

.reset-btn {
  padding: 4px 12px;
  background: rgba(255, 100, 100, 0.15);
  border: 1px solid rgba(255, 100, 100, 0.3);
  border-radius: 8px;
  color: #ff6b6b;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: auto;
}

.reset-btn:hover {
  background: rgba(255, 100, 100, 0.25);
  border-color: rgba(255, 100, 100, 0.5);
}
</style>
