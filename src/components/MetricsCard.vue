<template>
  <div class="metric-card">
    <div class="icon">{{ metric.icon }}</div>
    <div class="label">{{ metric.label }}</div>
    <div class="value">{{ metric.value }}</div>
  </div>
</template>

<script>
export default {
  props: {
    metric: Object
  }
}
</script>

<style scoped>
.metric-card {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
  color: var(--text-accent, #00d4ff);
  padding: 24px;
  border-radius: 14px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 20px var(--shadow-glow, rgba(0, 212, 255, 0.3)), inset 0 0 20px rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.4);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  filter: blur(40px);
}

.metric-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 0 40px rgba(0, 212, 255, 0.6), 0 0 80px rgba(124, 58, 237, 0.3), inset 0 0 20px rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.8);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%);
}

.icon {
  font-size: 32px;
  margin-bottom: 12px;
  display: block;
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.6));
}

.label {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 10px;
  font-weight: 500;
  letter-spacing: 0.5px;
  position: relative;
  z-index: 1;
  color: var(--text-primary, white);
}

.value {
  font-size: 36px;
  font-weight: 700;
  position: relative;
  z-index: 1;
  letter-spacing: -0.5px;
  color: var(--text-primary, white);
  text-shadow: 0 0 10px var(--shadow-glow, rgba(0, 212, 255, 0.8));
}
</style>
