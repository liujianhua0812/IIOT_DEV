<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>内生安全体系</h1>
      <p>以内生可信为核心，贯穿数据、模型、任务全生命周期的纵深防护体系。</p>
    </header>

    <section class="grid">
      <!-- 设备可信认证模块 -->
      <div class="module-wrapper">
        <article class="card" @click="navigateToDeviceVerification('hikvision-camera')">
          <h2>设备可信认证</h2>
          <p>融合链路、设备、模型、任务多维指标，实时安全态势感知。</p>
          <div class="chip-group device-chip-group" @click.stop>
            <button class="chip" @click="navigateToDeviceVerification('hikvision-camera')">
              <span>海康工业相机<br>(Ethernet Protocol)</span>
            </button>
            <button class="chip" @click="navigateToDeviceVerification('siemens-motor-driver')">
              <span>西门子电机驱动器<br>(ProfiNet Protocol)</span>
            </button>
            <button class="chip" @click="navigateToDeviceVerification('tsn-switch')">
              <span>TSN交换机<br>(TSN Protocol)</span>
            </button>
            <button class="chip" @click="navigateToDeviceVerification('temperature-sensor')">
              <span>温度传感器<br>(Modbus Protocol)</span>
            </button>
            <button class="chip" @click="navigateToDeviceVerification('ethercat-motor-driver')">
              <span>EtherCat电机驱动器<br>(EtherCat Protocol)</span>
            </button>
          </div>
        </article>
      </div>

      <!-- 细粒度访问控制模块 -->
      <div class="module-wrapper">
        <article class="card" @click="navigateToAccessControl('端侧模型访问控制')">
          <h2>细粒度访问控制</h2>
          <p>安全策略自学习迭代，自动编排边云协同防护链路。</p>
          <div class="chip-group access-chip-group" @click.stop>
            <button class="chip" @click="navigateToAccessControl('端侧模型访问控制')">
              <span>端侧模型访问控制<br>(Device-Side Model)</span>
            </button>
            <button class="chip" @click="navigateToAccessControl('云侧模型访问控制')">
              <span>云侧模型访问控制<br>(Cloud-Side Model)</span>
            </button>
            <button class="chip" @click="navigateToAccessControl('云上数据访问控制')">
              <span>云上数据访问控制<br>(Cloud Data)</span>
            </button>
            <button class="chip" @click="navigateToAccessControl('链上数据访问控制')">
              <span>链上数据访问控制<br>(Chain Data)</span>
            </button>
            <button class="chip" @click="navigateToAccessControl('视频数据访问控制')">
              <span>视频数据访问控制<br>(Video Data)</span>
            </button>
          </div>
        </article>
      </div>

      <!-- DDoS检测模块 -->
      <div class="module-wrapper">
        <article class="card radar" @click="navigateToDDoS">
          <h2>DDoS检测</h2>
          <p>进入检测中枢页面，查看实时威胁、攻击链溯源与自动处置编排。</p>
          <div class="chip-group ddos-chip-group" @click.stop>
            <RouterLink class="chip chip-link" :to="{ name: 'ddos-system-status' }">
              <span>系统状态<br>(System Status)</span>
            </RouterLink>
            <RouterLink class="chip chip-link" :to="{ name: 'ddos-device-monitor' }">
              <span>设备监控<br>(Device Monitor)</span>
            </RouterLink>
            <div class="chip chip-invisible">
              <span>占位符<br>(Placeholder)</span>
            </div>
            <div class="chip chip-invisible">
              <span>占位符<br>(Placeholder)</span>
            </div>
            <div class="chip chip-invisible">
              <span>占位符<br>(Placeholder)</span>
            </div>
          </div>
        </article>
      </div>
    </section>

    <!-- 技术路线全景图 -->
    <section class="tech-roadmap">
      <h2 class="roadmap-title">技术路线关系图谱</h2>
      <div class="roadmap-canvas-wrapper">
        <canvas ref="canvas" class="roadmap-canvas"></canvas>
        <div class="legend">
          <div class="legend-item"><span class="dot device-color"></span>设备可信认证</div>
          <div class="legend-item"><span class="dot access-color"></span>细粒度访问控制</div>
          <div class="legend-item"><span class="dot ddos-color"></span>DDoS检测</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'SecurityView',
  setup() {
    const router = useRouter()
    const canvas = ref(null)
    const hoveredNode = ref(null)
    const infoPosition = ref({ x: 0, y: 0 })
    let animationId = null
    let ctx = null
    let nodes = []
    let links = []
    let childNodes = []  // 悬停时显示的子节点
    let draggedNode = null  // 正在拖动的节点
    let isDragging = false
    
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

    const navigateToDDoS = () => {
      safePush({ name: 'ddos-system-status' })
    }

    // 初始化节点和连接数据
    const initGraph = () => {
      const width = canvas.value.width
      const height = canvas.value.height
      
      // 创建所有节点
      nodes = [
        // 设备可信认证节点 (蓝色系)
        { id: 'device-0', label: '硬件指纹', sublabel: 'TPM/PUF', category: '设备可信认证', x: 0, y: 0, vx: 0, vy: 0, color: '#58b2ff', type: 'device', 
          children: [
            { label: 'TPM', sublabel: 'Trusted Platform Module', tech: '可信平台模块' },
            { label: 'PUF', sublabel: 'Physical Unclonable Function', tech: '物理不可克隆函数' }
          ]
        },
        { id: 'device-1', label: '固件可信', sublabel: 'Secure Boot', category: '设备可信认证', x: 0, y: 0, vx: 0, vy: 0, color: '#58b2ff', type: 'device',
          children: [
            { label: 'UEFI', sublabel: 'Unified Extensible Firmware', tech: '统一可扩展固件' },
            { label: '签名验证', sublabel: 'Digital Signature', tech: '数字签名校验' }
          ]
        },
        { id: 'device-2', label: '协议栈指纹', sublabel: 'Profinet/TSN', category: '设备可信认证', x: 0, y: 0, vx: 0, vy: 0, color: '#58b2ff', type: 'device',
          children: [
            { label: 'Profinet', sublabel: 'Process Field Net', tech: '工业以太网协议' },
            { label: 'TSN', sublabel: 'Time-Sensitive Networking', tech: '时间敏感网络' },
            { label: 'EtherCAT', sublabel: 'Ethernet for Control', tech: '实时工业以太网' }
          ]
        },
        { id: 'device-3', label: '密钥管理', sublabel: 'X.509/SM2', category: '设备可信认证', x: 0, y: 0, vx: 0, vy: 0, color: '#6cc6ff', type: 'device',
          children: [
            { label: 'X.509', sublabel: 'PKI Certificate', tech: '公钥基础设施证书' },
            { label: 'SM2', sublabel: 'State Cryptography', tech: '国密椭圆曲线算法' },
            { label: 'HSM', sublabel: 'Hardware Security Module', tech: '硬件安全模块' }
          ]
        },
        { id: 'device-4', label: '远程证明', sublabel: 'TEE/DICE', category: '设备可信认证', x: 0, y: 0, vx: 0, vy: 0, color: '#6cc6ff', type: 'device',
          children: [
            { label: 'TEE', sublabel: 'Trusted Execution Environment', tech: '可信执行环境' },
            { label: 'DICE', sublabel: 'Device Identifier Composition', tech: '设备标识符组合引擎' },
            { label: 'SGX', sublabel: 'Software Guard Extensions', tech: '软件保护扩展' }
          ]
        },
        { id: 'device-5', label: '链路安全', sublabel: 'TLS1.3', category: '设备可信认证', x: 0, y: 0, vx: 0, vy: 0, color: '#80d6ff', type: 'device',
          children: [
            { label: 'TLS 1.3', sublabel: 'Transport Layer Security', tech: '传输层安全协议' },
            { label: 'DTLS', sublabel: 'Datagram TLS', tech: '数据报传输层安全' },
            { label: 'MACsec', sublabel: 'Media Access Control Security', tech: '媒体访问控制安全' }
          ]
        },
        { id: 'device-6', label: '行为基线', sublabel: '时序/功耗', category: '设备可信认证', x: 0, y: 0, vx: 0, vy: 0, color: '#80d6ff', type: 'device',
          children: [
            { label: '时序分析', sublabel: 'Timing Analysis', tech: '操作时序特征提取' },
            { label: '功耗分析', sublabel: 'Power Analysis', tech: '功耗模式识别' },
            { label: '行为建模', sublabel: 'Behavior Modeling', tech: '正常行为模型' }
          ]
        },
        { id: 'device-7', label: '态势感知', sublabel: '策略联动', category: '设备可信认证', x: 0, y: 0, vx: 0, vy: 0, color: '#94e6ff', type: 'device',
          children: [
            { label: '威胁情报', sublabel: 'Threat Intelligence', tech: '威胁情报聚合' },
            { label: '风险评估', sublabel: 'Risk Assessment', tech: '实时风险评分' },
            { label: '自动响应', sublabel: 'Auto Response', tech: '自动化响应编排' }
          ]
        },
        
        // 访问控制节点 (青色系)
        { id: 'access-0', label: '统一身份', sublabel: 'IAM/OIDC', category: '细粒度访问控制', x: 0, y: 0, vx: 0, vy: 0, color: '#00d4aa', type: 'access',
          children: [
            { label: 'IAM', sublabel: 'Identity Access Management', tech: '身份访问管理' },
            { label: 'OIDC', sublabel: 'OpenID Connect', tech: '开放身份认证' },
            { label: 'SAML', sublabel: 'Security Assertion Markup', tech: '安全断言标记语言' }
          ]
        },
        { id: 'access-1', label: '属性管理', sublabel: '设备/数据', category: '细粒度访问控制', x: 0, y: 0, vx: 0, vy: 0, color: '#00d4aa', type: 'access',
          children: [
            { label: '设备属性', sublabel: 'Device Attributes', tech: '设备元数据管理' },
            { label: '数据属性', sublabel: 'Data Attributes', tech: '数据分类标签' },
            { label: '属性同步', sublabel: 'Attribute Sync', tech: '属性同步机制' }
          ]
        },
        { id: 'access-2', label: '策略模型', sublabel: 'RBAC/PBAC', category: '细粒度访问控制', x: 0, y: 0, vx: 0, vy: 0, color: '#1ae6bb', type: 'access',
          children: [
            { label: 'RBAC', sublabel: 'Role-Based Access Control', tech: '基于角色访问控制' },
            { label: 'ABAC', sublabel: 'Attribute-Based Access', tech: '基于属性访问控制' },
          ]
        },
        { id: 'access-3', label: '加密协议', sublabel: '可搜索加密/属性加密', category: '细粒度访问控制', x: 0, y: 0, vx: 0, vy: 0, color: '#1ae6bb', type: 'access',
          children: [
            { label: '可搜索加密', sublabel: 'Searchable Encryption', tech: '密文搜索技术' },
            { label: '属性加密', sublabel: 'Attribute-Based Encryption', tech: '基于属性加密' },
            { label: '对称加密', sublabel: 'Symmetric Encryption', tech: '对称密钥加密' }
          ]
        },
        { id: 'access-4', label: '上下文感知', sublabel: '态势/时空', category: '细粒度访问控制', x: 0, y: 0, vx: 0, vy: 0, color: '#33f5cc', type: 'access',
          children: [
            { label: '时间因素', sublabel: 'Temporal Context', tech: '时间窗口控制' },
            { label: '位置因素', sublabel: 'Location Context', tech: '地理位置限制' },
            { label: '态势因素', sublabel: 'Situation Context', tech: '安全态势感知' }
          ]
        },
        { id: 'access-5', label: '端侧执行', sublabel: 'TEE/合约授权', category: '细粒度访问控制', x: 0, y: 0, vx: 0, vy: 0, color: '#33f5cc', type: 'access',
          children: [
            { label: '可信执行环境', sublabel: 'Trusted Execution Environment', tech: 'TEE隔离执行' },
            { label: '合约授权', sublabel: 'Contract Authorization', tech: '智能合约授权' },
            { label: 'Baker映射', sublabel: 'Baker Map', tech: 'Baker混沌映射' }
          ]
        },
        { id: 'access-6', label: '云侧执行', sublabel: 'API网关/任务锚点', category: '细粒度访问控制', x: 0, y: 0, vx: 0, vy: 0, color: '#4dffdd', type: 'access',
          children: [
            { label: 'API网关', sublabel: 'API Gateway', tech: 'API鉴权网关' },
            { label: '任务锚点', sublabel: 'Task Anchor', tech: '任务锚点机制' },
            { label: '激活值偏移', sublabel: 'Activation Offset', tech: '激活值偏移保护' }
          ]
        },
        { id: 'access-7', label: '审计合规', sublabel: '回放/认证数据结构', category: '细粒度访问控制', x: 0, y: 0, vx: 0, vy: 0, color: '#4dffdd', type: 'access',
          children: [
            { label: '行为回放', sublabel: 'Behavior Replay', tech: '操作回放分析' },
            { label: '认证数据结构', sublabel: 'Authenticated Data Structure', tech: 'ADS数据结构' },
            { label: '合规检查', sublabel: 'Compliance Check', tech: '合规性验证' }
          ]
        },
        
        // DDoS检测节点 (橙色系)
        { id: 'ddos-0', label: '流量采集', sublabel: 'eBPF/DPDK', category: 'DDoS检测', x: 0, y: 0, vx: 0, vy: 0, color: '#ff9d00', type: 'ddos',
          children: [
            { label: 'eBPF', sublabel: 'Extended BPF', tech: '内核级流量捕获' },
            { label: 'DPDK', sublabel: 'Data Plane Development', tech: '数据平面加速' },
            { label: 'XDP', sublabel: 'eXpress Data Path', tech: '快速数据路径' }
          ]
        },
        { id: 'ddos-1', label: '镜像流', sublabel: 'NetFlow', category: 'DDoS检测', x: 0, y: 0, vx: 0, vy: 0, color: '#ff9d00', type: 'ddos',
          children: [
            { label: 'NetFlow', sublabel: 'Network Flow', tech: '网络流量统计' },
            { label: 'sFlow', sublabel: 'Sampled Flow', tech: '采样流量分析' },
            { label: 'IPFIX', sublabel: 'IP Flow Information', tech: 'IP流信息导出' }
          ]
        },
        { id: 'ddos-2', label: '特征工程', sublabel: '熵/突发', category: 'DDoS检测', x: 0, y: 0, vx: 0, vy: 0, color: '#ffb133', type: 'ddos',
          children: [
            { label: '熵值分析', sublabel: 'Entropy Analysis', tech: '流量熵值计算' },
            { label: '突发检测', sublabel: 'Burst Detection', tech: '流量突发识别' },
            { label: '统计特征', sublabel: 'Statistical Features', tech: '多维统计特征' }
          ]
        },
        { id: 'ddos-3', label: '检测模型', sublabel: 'LSTM', category: 'DDoS检测', x: 0, y: 0, vx: 0, vy: 0, color: '#ffb133', type: 'ddos',
          children: [
            { label: 'LSTM', sublabel: 'Long Short-Term Memory', tech: '长短期记忆网络' },
            { label: 'Transformer', sublabel: 'Attention Mechanism', tech: '注意力机制模型' },
            { label: 'Random Forest', sublabel: 'Ensemble Learning', tech: '随机森林集成' }
          ]
        },
        { id: 'ddos-4', label: '攻击溯源', sublabel: 'IP画像', category: 'DDoS检测', x: 0, y: 0, vx: 0, vy: 0, color: '#ffc466', type: 'ddos',
          children: [
            { label: 'IP画像', sublabel: 'IP Profiling', tech: 'IP行为画像' },
            { label: '路径追踪', sublabel: 'Path Tracing', tech: '攻击路径追踪' },
            { label: '归因分析', sublabel: 'Attribution Analysis', tech: '攻击归因' }
          ]
        },
        { id: 'ddos-5', label: '自动处置', sublabel: 'ACL/清洗', category: 'DDoS检测', x: 0, y: 0, vx: 0, vy: 0, color: '#ffc466', type: 'ddos',
          children: [
            { label: 'ACL', sublabel: 'Access Control List', tech: '访问控制列表' },
            { label: '流量清洗', sublabel: 'Traffic Scrubbing', tech: '恶意流量过滤' },
            { label: '黑洞路由', sublabel: 'Blackhole Routing', tech: '黑洞路由丢弃' }
          ]
        },
        { id: 'ddos-6', label: '可视化', sublabel: '看板/告警', category: 'DDoS检测', x: 0, y: 0, vx: 0, vy: 0, color: '#ffd799', type: 'ddos',
          children: [
            { label: 'Grafana', sublabel: 'Metrics Dashboard', tech: '指标可视化看板' },
            { label: 'ELK', sublabel: 'Elasticsearch Kibana', tech: '日志分析展示' },
            { label: 'AlertManager', sublabel: 'Alert Routing', tech: '告警路由管理' }
          ]
        },
        { id: 'ddos-7', label: '自学习', sublabel: '自适应', category: 'DDoS检测', x: 0, y: 0, vx: 0, vy: 0, color: '#ffd799', type: 'ddos',
          children: [
            { label: '在线学习', sublabel: 'Online Learning', tech: '在线模型更新' },
            { label: '反馈优化', sublabel: 'Feedback Loop', tech: '反馈闭环优化' },
            { label: '自适应阈值', sublabel: 'Adaptive Threshold', tech: '动态阈值调整' }
          ]
        }
      ]
      
      // 随机初始化位置
      nodes.forEach(node => {
        node.x = Math.random() * width
        node.y = Math.random() * height
        node.vx = (Math.random() - 0.5) * 2
        node.vy = (Math.random() - 0.5) * 2
      })
      
      // 定义连接关系
      links = [
        // 设备认证内部连接
        { source: 'device-0', target: 'device-1', strength: 0.8 },
        { source: 'device-0', target: 'device-3', strength: 0.9 },
        { source: 'device-1', target: 'device-2', strength: 0.7 },
        { source: 'device-3', target: 'device-4', strength: 0.8 },
        { source: 'device-4', target: 'device-5', strength: 0.7 },
        { source: 'device-5', target: 'device-7', strength: 0.6 },
        { source: 'device-6', target: 'device-7', strength: 0.8 },
        
        // 访问控制内部连接
        { source: 'access-0', target: 'access-1', strength: 0.9 },
        { source: 'access-1', target: 'access-2', strength: 0.8 },
        { source: 'access-2', target: 'access-3', strength: 0.9 },
        { source: 'access-3', target: 'access-4', strength: 0.7 },
        { source: 'access-4', target: 'access-5', strength: 0.6 },
        { source: 'access-4', target: 'access-6', strength: 0.6 },
        { source: 'access-5', target: 'access-7', strength: 0.5 },
        { source: 'access-6', target: 'access-7', strength: 0.5 },
        
        // DDoS检测内部连接
        { source: 'ddos-0', target: 'ddos-1', strength: 0.8 },
        { source: 'ddos-0', target: 'ddos-2', strength: 0.9 },
        { source: 'ddos-1', target: 'ddos-2', strength: 0.7 },
        { source: 'ddos-2', target: 'ddos-3', strength: 0.9 },
        { source: 'ddos-3', target: 'ddos-4', strength: 0.7 },
        { source: 'ddos-4', target: 'ddos-5', strength: 0.8 },
        { source: 'ddos-5', target: 'ddos-6', strength: 0.6 },
        { source: 'ddos-6', target: 'ddos-7', strength: 0.7 },
        
        // 跨模块连接
        { source: 'device-0', target: 'access-0', strength: 0.8 },
        { source: 'device-3', target: 'access-2', strength: 0.9 },
        { source: 'device-4', target: 'access-4', strength: 0.6 },
        { source: 'device-7', target: 'access-7', strength: 0.7 },
        
        { source: 'access-4', target: 'ddos-2', strength: 0.7 },
        { source: 'access-6', target: 'ddos-5', strength: 0.8 },
        { source: 'access-7', target: 'ddos-6', strength: 0.6 },
        
        { source: 'device-6', target: 'ddos-2', strength: 0.5 },
        { source: 'device-7', target: 'ddos-4', strength: 0.6 },
        { source: 'device-5', target: 'ddos-5', strength: 0.5 }
      ]
    }

    // 力导向布局算法
    const updatePhysics = () => {
      const centerX = canvas.value.width / 2
      const centerY = canvas.value.height / 2
      const damping = 0.8
      
      // 应用力
      nodes.forEach(node => {
        // 如果节点正在被拖动，跳过物理计算
        if (draggedNode && draggedNode.id === node.id) {
          node.vx = 0
          node.vy = 0
          return
        }
        
        // 重力 - 吸引到中心
        const dx = centerX - node.x
        const dy = centerY - node.y
        const distToCenter = Math.sqrt(dx * dx + dy * dy)
        node.vx += (dx / distToCenter) * 0.01
        node.vy += (dy / distToCenter) * 0.01
        
        // 节点间排斥力
        nodes.forEach(other => {
          if (node !== other) {
            const dx = node.x - other.x
            const dy = node.y - other.y
            const dist = Math.sqrt(dx * dx + dy * dy) || 1
            const force = 3000 / (dist * dist)
            node.vx += (dx / dist) * force
            node.vy += (dy / dist) * force
          }
        })
      })
      
      // 连接的吸引力
      links.forEach(link => {
        const source = nodes.find(n => n.id === link.source)
        const target = nodes.find(n => n.id === link.target)
        if (!source || !target) return
        
        // 如果任一节点正在被拖动，跳过
        if ((draggedNode && draggedNode.id === source.id) || (draggedNode && draggedNode.id === target.id)) {
          return
        }
        
        const dx = target.x - source.x
        const dy = target.y - source.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = (dist - 200) * 0.01 * link.strength
        
        source.vx += (dx / dist) * force
        source.vy += (dy / dist) * force
        target.vx -= (dx / dist) * force
        target.vy -= (dy / dist) * force
      })
      
      // 更新位置
      nodes.forEach(node => {
        // 如果节点正在被拖动，跳过位置更新
        if (draggedNode && draggedNode.id === node.id) {
          return
        }
        
        node.vx *= damping
        node.vy *= damping
        node.x += node.vx
        node.y += node.vy
        
        // 边界检查 - 为子节点预留底部空间
        const margin = 60
        const bottomMargin = 200  // 底部预留更多空间给子节点显示
        if (node.x < margin) { node.x = margin; node.vx *= -0.5 }
        if (node.x > canvas.value.width - margin) { node.x = canvas.value.width - margin; node.vx *= -0.5 }
        if (node.y < margin) { node.y = margin; node.vy *= -0.5 }
        if (node.y > canvas.value.height - bottomMargin) { node.y = canvas.value.height - bottomMargin; node.vy *= -0.5 }
      })
    }

    // 绘制图形
    const draw = () => {
      if (!ctx) return
      
      // 清空画布
      ctx.fillStyle = 'rgba(3, 13, 23, 0.3)'
      ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)
      
      // 绘制连接线
      links.forEach(link => {
        const source = nodes.find(n => n.id === link.source)
        const target = nodes.find(n => n.id === link.target)
        if (!source || !target) return
        
        const gradient = ctx.createLinearGradient(source.x, source.y, target.x, target.y)
        gradient.addColorStop(0, source.color + '40')
        gradient.addColorStop(1, target.color + '40')
        
        ctx.strokeStyle = gradient
        ctx.lineWidth = link.strength * 2
        ctx.beginPath()
        ctx.moveTo(source.x, source.y)
        ctx.lineTo(target.x, target.y)
        ctx.stroke()
        
        // 发光效果
        if (hoveredNode.value && (link.source === hoveredNode.value.id || link.target === hoveredNode.value.id)) {
          ctx.shadowBlur = 20
          ctx.shadowColor = source.color
          ctx.strokeStyle = source.color + 'cc'
          ctx.lineWidth = link.strength * 3
          ctx.stroke()
          ctx.shadowBlur = 0
        }
      })
      
      // 绘制子节点连接线
      if (hoveredNode.value && childNodes.length > 0) {
        childNodes.forEach(child => {
          const gradient = ctx.createLinearGradient(hoveredNode.value.x, hoveredNode.value.y, child.x, child.y)
          gradient.addColorStop(0, hoveredNode.value.color + 'aa')
          gradient.addColorStop(1, hoveredNode.value.color + '66')
          
          ctx.strokeStyle = gradient
          ctx.lineWidth = 2
          ctx.setLineDash([5, 5])
          ctx.beginPath()
          ctx.moveTo(hoveredNode.value.x, hoveredNode.value.y)
          ctx.lineTo(child.x, child.y)
          ctx.stroke()
          ctx.setLineDash([])
        })
      }
      
      // 绘制节点
      nodes.forEach(node => {
        const isHovered = hoveredNode.value && hoveredNode.value.id === node.id
        const radius = isHovered ? 28 : 20
        
        // 外发光
        ctx.shadowBlur = isHovered ? 30 : 15
        ctx.shadowColor = node.color
        
        // 节点外圈
        ctx.beginPath()
        ctx.arc(node.x, node.y, radius + 4, 0, Math.PI * 2)
        ctx.fillStyle = node.color + '40'
        ctx.fill()
        
        // 节点主体
        const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, radius)
        gradient.addColorStop(0, node.color)
        gradient.addColorStop(1, node.color + '80')
        
        ctx.beginPath()
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2)
        ctx.fillStyle = gradient
        ctx.fill()
        
        ctx.shadowBlur = 0
        
        // 绘制标签
        ctx.fillStyle = '#d6e8ff'
        ctx.font = isHovered ? 'bold 16px Arial' : '14px Arial'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(node.label, node.x, node.y - radius - 12)
        
        if (isHovered && node.sublabel) {
          ctx.fillStyle = '#80d6ff'
          ctx.font = '12px Consolas'
          ctx.fillText(node.sublabel, node.x, node.y - radius - 26)
        }
      })
      
      // 绘制子节点
      if (hoveredNode.value && childNodes.length > 0) {
        childNodes.forEach((child, index) => {
          const radius = 12
          
          // 外发光
          ctx.shadowBlur = 15
          ctx.shadowColor = hoveredNode.value.color
          
          // 子节点外圈
          ctx.beginPath()
          ctx.arc(child.x, child.y, radius + 2, 0, Math.PI * 2)
          ctx.fillStyle = hoveredNode.value.color + '30'
          ctx.fill()
          
          // 子节点主体
          const gradient = ctx.createRadialGradient(child.x, child.y, 0, child.x, child.y, radius)
          gradient.addColorStop(0, hoveredNode.value.color + 'dd')
          gradient.addColorStop(1, hoveredNode.value.color + '99')
          
          ctx.beginPath()
          ctx.arc(child.x, child.y, radius, 0, Math.PI * 2)
          ctx.fillStyle = gradient
          ctx.fill()
          
          ctx.shadowBlur = 0
          
          // 绘制子节点标签（显示在节点下方）
          ctx.fillStyle = '#ffffff'
          ctx.font = 'bold 12px Arial'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillText(child.label, child.x, child.y + radius + 10)
        })
      }
    }

    // 动画循环
    const animate = () => {
      updatePhysics()
      draw()
      animationId = requestAnimationFrame(animate)
    }

    // 鼠标交互
    const handleMouseMove = (e) => {
      const rect = canvas.value.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      
      // 如果正在拖动，更新拖动节点的位置
      if (isDragging && draggedNode) {
        // 限制拖动范围，底部预留空间给子节点
        const margin = 60
        const bottomMargin = 200
        draggedNode.x = Math.max(margin, Math.min(x, canvas.value.width - margin))
        draggedNode.y = Math.max(margin, Math.min(y, canvas.value.height - bottomMargin))
        
        // 如果拖动的节点有子节点在显示，实时更新子节点位置
        if (hoveredNode.value && hoveredNode.value.id === draggedNode.id && childNodes.length > 0) {
          const childCount = childNodes.length
          const spreadAngle = Math.PI / 3
          const startAngle = Math.PI / 2 - spreadAngle / 2
          
          childNodes.forEach((child, index) => {
            const angle = startAngle + (index * spreadAngle / Math.max(childCount - 1, 1))
            const distance = 120 + (index % 2) * 30 + Math.floor(index / 2) * 15
            
            child.x = draggedNode.x + Math.cos(angle) * distance
            child.y = draggedNode.y + Math.sin(angle) * distance
            // 保持progress为1，表示已完全展开
            child.progress = 1
          })
        }
        return
      }
      
      let found = null
      for (const node of nodes) {
        const dist = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
        if (dist < 30) {
          found = node
          break
        }
      }
      
      // 当悬停节点发生变化时，更新子节点
      if (found !== hoveredNode.value) {
        hoveredNode.value = found
        
        if (found && found.children) {
          // 创建子节点布局 - 下方扇形排列
          const childCount = found.children.length
          const spreadAngle = Math.PI / 3  // 扇形张角（60度）
          const startAngle = Math.PI / 2 - spreadAngle / 2  // 从下方偏左开始
          
          childNodes = found.children.map((child, index) => {
            const angle = startAngle + (index * spreadAngle / Math.max(childCount - 1, 1))
            const distance = 120 + (index % 2) * 30 + Math.floor(index / 2) * 15
            return {
              ...child,
              x: found.x + Math.cos(angle) * distance,
              y: found.y + Math.sin(angle) * distance,
              targetX: found.x + Math.cos(angle) * distance,
              targetY: found.y + Math.sin(angle) * distance,
              currentX: found.x,
              currentY: found.y,
              progress: 0
            }
          })
        } else {
          childNodes = []
        }
      }
      
      // 更新子节点展开动画
      if (childNodes.length > 0 && hoveredNode.value) {
        childNodes.forEach((child, index) => {
          // 计算子节点相对于父节点的位置
          const childCount = childNodes.length
          const spreadAngle = Math.PI / 3
          const startAngle = Math.PI / 2 - spreadAngle / 2
          const angle = startAngle + (index * spreadAngle / Math.max(childCount - 1, 1))
          const distance = 120 + (index % 2) * 30 + Math.floor(index / 2) * 15
          
          const targetX = hoveredNode.value.x + Math.cos(angle) * distance
          const targetY = hoveredNode.value.y + Math.sin(angle) * distance
          
          if (child.progress < 1) {
            child.progress = Math.min(child.progress + 0.15, 1)
          }
          
          // 始终使用相同的目标位置，不使用缓动
          child.x = targetX
          child.y = targetY
        })
      }
      
      canvas.value.style.cursor = found ? 'grab' : 'default'
    }

    const handleMouseDown = (e) => {
      const rect = canvas.value.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      
      for (const node of nodes) {
        const dist = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
        if (dist < 30) {
          isDragging = true
          draggedNode = node
          canvas.value.style.cursor = 'grabbing'
          break
        }
      }
    }

    const handleMouseUp = () => {
      if (isDragging) {
        isDragging = false
        draggedNode = null
        canvas.value.style.cursor = hoveredNode.value ? 'grab' : 'default'
      }
    }

    const handleMouseLeave = () => {
      if (isDragging) {
        isDragging = false
        draggedNode = null
      }
    }

    const getConnections = (nodeId) => {
      return links.filter(link => link.source === nodeId || link.target === nodeId)
    }

    const handleResize = () => {
      if (!canvas.value) return
      canvas.value.width = canvas.value.offsetWidth
      canvas.value.height = canvas.value.offsetHeight
    }

    onMounted(() => {
      nextTick(() => {
        if (!canvas.value) return
        
        canvas.value.width = canvas.value.offsetWidth
        canvas.value.height = canvas.value.offsetHeight
        ctx = canvas.value.getContext('2d')
        
        initGraph()
        animate()
        
        canvas.value.addEventListener('mousemove', handleMouseMove)
        canvas.value.addEventListener('mousedown', handleMouseDown)
        canvas.value.addEventListener('mouseup', handleMouseUp)
        canvas.value.addEventListener('mouseleave', handleMouseLeave)
        window.addEventListener('resize', handleResize)
      })
    })

    onUnmounted(() => {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
      if (canvas.value) {
        canvas.value.removeEventListener('mousemove', handleMouseMove)
        canvas.value.removeEventListener('mousedown', handleMouseDown)
        canvas.value.removeEventListener('mouseup', handleMouseUp)
        canvas.value.removeEventListener('mouseleave', handleMouseLeave)
      }
      window.removeEventListener('resize', handleResize)
    })

    return {
      navigateToEdgeModel,
      navigateToAccessControl,
      navigateToDeviceVerification,
      navigateToDDoS,
      canvas,
      hoveredNode,
      infoPosition,
      getConnections
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

.module-wrapper {
  display: grid;
  grid-template-rows: auto auto auto;
  gap: 12px;
  align-content: start;
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
.access-chip-group,
.ddos-chip-group {
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
  text-align: center;
  line-height: 1.4;
}

.chip span {
  display: inline-block;
}

.chip:hover {
  background: rgba(128, 214, 255, 0.2);
  border-color: rgba(128, 214, 255, 0.35);
}

.chip-invisible {
  visibility: hidden;
  pointer-events: none;
}
.clickable {
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 28px 56px rgba(0, 0, 0, 0.42);
}
.link-reset {
  text-decoration: none;
  color: inherit;
  display: block;
}
.link-reset:focus-visible {
  outline: 2px solid rgba(73, 197, 255, 0.6);
  outline-offset: 4px;
}
.chip-link {
  text-decoration: none;
  color: inherit;
  display: inline-block;
}
.chip-link:hover {
  background: rgba(128, 214, 255, 0.18);
}

.device-chip-group .chip {
  padding: 8px 12px;
}

/* 技术路线关系图样式 */
.tech-roadmap {
  margin-top: 48px;
  padding: 32px;
  background: linear-gradient(160deg, rgba(4, 21, 38, 0.8), rgba(3, 13, 23, 0.7));
  border-radius: 24px;
  border: 1px solid rgba(88, 178, 255, 0.25);
  box-shadow: 0 0 50px rgba(88, 178, 255, 0.15), inset 0 0 80px rgba(88, 178, 255, 0.05);
  position: relative;
  overflow: hidden;
}

.tech-roadmap::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(88, 178, 255, 0.8), transparent);
}

.roadmap-title {
  font-size: 28px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #d6e8ff, rgba(128, 214, 255, 0.9));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 3px;
  text-shadow: 0 0 30px rgba(88, 178, 255, 0.5);
}

.roadmap-canvas-wrapper {
  position: relative;
  width: 100%;
  height: 700px;
  background: radial-gradient(circle at center, rgba(4, 21, 38, 0.3), rgba(3, 13, 23, 0.5));
  border-radius: 16px;
  border: 1px solid rgba(88, 178, 255, 0.15);
  overflow: hidden;
}

.roadmap-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.legend {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(4, 21, 38, 0.9);
  border: 1px solid rgba(88, 178, 255, 0.3);
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 12px 0;
  font-size: 15px;
  color: #d6e8ff;
  font-weight: 500;
}

.legend .dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  box-shadow: 0 0 12px currentColor;
}

.device-color {
  background: #58b2ff;
  color: #58b2ff;
}

.access-color {
  background: #00d4aa;
  color: #00d4aa;
}

.ddos-color {
  background: #ff9d00;
  color: #ff9d00;
}

.node-info {
  position: fixed;
  background: linear-gradient(135deg, rgba(9, 32, 56, 0.98), rgba(4, 19, 34, 0.98));
  border: 1px solid rgba(88, 178, 255, 0.4);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 0 30px rgba(88, 178, 255, 0.3), inset 0 0 20px rgba(88, 178, 255, 0.05);
  backdrop-filter: blur(15px);
  pointer-events: none;
  z-index: 1000;
  min-width: 220px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.info-title {
  font-size: 16px;
  font-weight: 600;
  color: #d6e8ff;
  margin-bottom: 8px;
  text-shadow: 0 0 10px rgba(88, 178, 255, 0.5);
}

.info-category {
  font-size: 12px;
  color: rgba(128, 214, 255, 0.8);
  margin-bottom: 6px;
  padding: 4px 8px;
  background: rgba(88, 178, 255, 0.1);
  border-radius: 6px;
  display: inline-block;
}

.info-tech {
  font-size: 11px;
  color: rgba(160, 230, 255, 0.9);
  font-family: 'Consolas', 'Monaco', monospace;
  margin-bottom: 8px;
  padding: 4px 8px;
  background: rgba(88, 178, 255, 0.05);
  border-radius: 4px;
}

.info-connections {
  font-size: 11px;
  color: rgba(128, 214, 255, 0.7);
  padding-top: 8px;
  border-top: 1px solid rgba(88, 178, 255, 0.2);
}

.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.18s ease; }
</style>

