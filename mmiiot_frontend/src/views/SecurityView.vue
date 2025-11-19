<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>内生安全体系</h1>
      <p>以内生可信为核心，贯穿数据、模型、任务全生命周期的纵深防护体系。</p>
    </header>

    <section class="grid">
      <article class="card" @click="navigateToDeviceVerification('hikvision-camera')">
        <h2>设备可信认证</h2>
        <p>融合链路、设备、模型、任务多维指标，实时安全态势感知。</p>
        <div class="chip-group device-chip-group" @click.stop>
          <button class="chip" @click="navigateToDeviceVerification('hikvision-camera')">海康工业相机（Ethernet Protocol）</button>
          <button class="chip" @click="navigateToDeviceVerification('siemens-motor-driver')">西门子电机驱动器（ProfiNet Protocol）</button>
          <button class="chip" @click="navigateToDeviceVerification('tsn-switch')">TSN交换机（TSN Protocol）</button>
          <button class="chip" @click="navigateToDeviceVerification('temperature-sensor')">温度传感器（Modbus Protocol）</button>
          <button class="chip" @click="navigateToDeviceVerification('ethercat-motor-driver')">EtherCat电机驱动器（EtherCat Protocol）</button>
        </div>
      </article>
      <article class="card" @click="navigateToAccessControl('端侧模型访问控制')">
        <h2>细粒度访问控制</h2>
        <p>安全策略自学习迭代，自动编排边云协同防护链路。</p>
        <div class="chip-group access-chip-group" @click.stop>
          <button class="chip" @click="navigateToAccessControl('端侧模型访问控制')">端侧模型访问控制（Device-Side Model）</button>
          <button class="chip" @click="navigateToAccessControl('云侧模型访问控制')">云侧模型访问控制（Cloud-Side Model）</button>
          <button class="chip" @click="navigateToAccessControl('云上数据访问控制')">云上数据访问控制（Cloud Data）</button>
          <button class="chip" @click="navigateToAccessControl('链上数据访问控制')">链上数据访问控制（Chain Data）</button>
          <button class="chip" @click="navigateToAccessControl('视频数据访问控制')">视频数据访问控制（Video Data）</button>
        </div>
      </article>
    </section>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'SecurityView',
  setup() {
    const router = useRouter()
    
    // 包装push，避免重复导航等错误导致未捕获异常
    const safePush = (to) => {
      return router.push(to).catch(err => {
        // 忽略导航重复等可预期的错误
        if (err.name !== 'NavigationDuplicated') {
          console.warn('导航错误:', err)
        }
      })
    }

    const navigateToEdgeModel = () => {
      safePush({ name: 'edge-model-access-control' })
    }

    const navigateToAccessControl = (type) => {
      const routeMap = {
        '端侧模型访问控制': 'edge-model-access-control',
        '云侧模型访问控制': 'cloud-model-access-control',
        '云上数据访问控制': 'cloud-data-access-control',
        '链上数据访问控制': 'chain-data-access-control',
        '视频数据访问控制': 'video-data-access-control'
      }
      const routeName = routeMap[type]
      if (routeName) {
        safePush({ name: routeName })
      }
    }

    const navigateToDeviceVerification = (deviceType) => {
      // 使用英文设备类型作为路由参数
      return router.push(`/security/device-verification/${deviceType}`).catch(err => {
        // 忽略导航重复等可预期的错误
        if (err.name !== 'NavigationDuplicated') {
          console.warn('导航错误:', err)
        }
      })
    }

    return {
      navigateToEdgeModel,
      navigateToAccessControl,
      navigateToDeviceVerification
    }
  }
}
</script>

<style scoped>
.page-shell {
  padding: 32px 64px 64px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(4, 21, 38, 0.96), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
}

.page-header h1 {
  font-size: 34px;
  margin-bottom: 12px;
  letter-spacing: 1.4px;
}

.page-header p {
  max-width: 640px;
  color: rgba(214, 232, 255, 0.74);
  line-height: 1.8;
}

.grid {
  margin-top: 32px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.card {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  cursor: pointer;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 28px 48px rgba(0, 0, 0, 0.4);
  border-color: rgba(88, 178, 255, 0.2);
}

.card h2 {
  font-size: 22px;
  margin-bottom: 14px;
}

.card p {
  color: rgba(214, 232, 255, 0.75);
  line-height: 1.7;
}

.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

.device-chip-group,
.access-chip-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.chip {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid rgba(128, 214, 255, 0.2);
  background: rgba(128, 214, 255, 0.12);
  font-size: 13px;
  letter-spacing: 0.8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: inherit;
  font-family: inherit;
}

.chip:hover {
  background: rgba(128, 214, 255, 0.2);
  border-color: rgba(128, 214, 255, 0.35);
}

.device-chip-group .chip {
  padding: 8px 12px;
}

</style>

