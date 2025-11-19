<template>
  <div class="page-shell">
    <div class="container">
      <aside class="sidebar">
        <div class="system-header">
          <div class="system-title">细粒度访问控制系统</div>
        </div>

        <div 
          v-for="item in accessControlItems" 
          :key="item.name"
          class="device-category"
          :class="{ active: currentAccessControlType === item.name }"
          @click="navigateToAccessControl(item.name)"
        >
          <span class="category-icon">{{ item.icon }}</span> {{ item.name }}
        </div>
      </aside>

      <main class="main-content">
        <div class="header">
          <h1>柔性制造产线数据安全查询平台</h1>
        </div>

        <!-- 状态栏 -->
        <div class="status-bar">
          <div class="status-card">
            <span class="status-label">🕒 当前时间：</span>
            <span class="status-value">{{ currentTime }}</span>
          </div>
          <div class="status-card">
            <span class="status-label">📊 索引状态：</span>
            <span class="status-value">{{ indexStatus }}</span>
          </div>
          <div class="status-card">
            <span class="status-label">🏢 部门（可多选）：</span>
            <span class="status-value">{{ selectedDepartmentsDisplay }}</span>
          </div>
        </div>

        <!-- 搜索区域 -->
        <div class="search-section selection-panel">
          <h2 class="section-title">🔍 搜索</h2>
          <div v-if="statusMsg" class="status-banner" :class="statusType">{{ statusMsg }}</div>

          <div class="search-form">
            <!-- 关键词输入 -->
            <div class="form-group card-box">
              <label>关键词（按回车添加）</label>
              <input
                v-model.trim="keywordInput"
                @keydown.enter.prevent="addKeyword"
                placeholder="输入关键词并回车"
              />
              <div class="keyword-tags">
                <div class="keyword-tag" v-for="(kw, idx) in keywords" :key="kw + idx">
                  <span>{{ kw }}</span>
                  <span class="remove" @click="removeKeyword(idx)">×</span>
                </div>
              </div>
            </div>

            <!-- 部门与产线并排卡片 -->
            <div class="form-row">
              <div class="form-group card-box">
                <label>可选部门（多选）</label>
                <div id="departmentOptions" class="option-chips">
                  <span
                    v-for="dept in departments"
                    :key="dept"
                    class="chip"
                    :class="{ active: isDeptSelected(dept) }"
                    @click="toggleDepartment(dept)"
                  >{{ dept }}</span>
                  <span v-if="!departments || departments.length === 0" class="chip disabled">暂无部门</span>
                </div>
              </div>
              <div class="form-group card-box">
                <label>可选产线（按部门显示，多选）</label>
                <div id="levelOptionsContainer" class="level-groups">
                  <template v-if="selectedDepartmentsArr.length === 0">
                    <div class="no-levels">请先选择部门</div>
                  </template>
                  <template v-else>
                    <div class="level-group" v-for="dept in selectedDepartmentsArr" :key="dept">
                      <div class="level-dept-title">{{ dept }}</div>
                      <div class="option-chips">
                        <template v-if="levels[dept] && levels[dept].length > 0">
                          <span
                            v-for="lv in levels[dept]"
                            :key="dept + '-' + lv"
                            class="chip level"
                            :class="{ active: isLevelSelected(dept, lv) }"
                            @click="toggleLevel(dept, lv)"
                            :title="levelDisplayNames[lv] || lv"
                          >{{ levelDisplayNames[lv] || lv }}</span>
                        </template>
                        <span v-else class="chip disabled">该部门暂无产线</span>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="form-actions">
              <button id="searchBtn" class="btn btn-primary" :disabled="searching" @click="performSearch">
                {{ searching ? '搜索中...' : '搜索' }}
              </button>
              <button class="btn btn-danger" @click="clearSearch">清空</button>
            </div>
          </div>
        </div>

        <!-- 查询陷门信息 -->
        <div class="trapdoor-section">
          <h2 class="section-title">🔐 查询陷门信息</h2>
          <div class="trapdoor-box" v-html="trapdoorHtml"></div>
        </div>

        <!-- 结果区域 -->
        <div class="result-section selection-panel">
          <h2 class="section-title">📊 搜索结果</h2>
          <div v-if="resultsCountText" class="result-count">{{ resultsCountText }}</div>
          <div v-if="loadingResults" class="loading">
            <div class="spinner"></div>
            <p>正在搜索...</p>
          </div>
          <div v-else class="result-scroll-container">
            <div v-if="results.length === 0" class="no-results">未找到匹配的文档，请尝试其他关键词或属性</div>
            <div v-else class="result-list">
              <div class="result-item" v-for="(item, idx) in results" :key="(item.file || item.id || idx) + '-' + idx">
                <div class="result-header">
                  <h3><span class="file-icon">{{ getFileIcon(item.file || item.id) }}</span>{{ item.file || item.id || '未知文件名' }}</h3>
                  <span class="rank-badge">排名 #{{ idx + 1 }}</span>
                </div>
                <div class="meta-row">
                  <strong>内积结果</strong>
                  <span class="meta-pill score">{{ formatScore(item) }}</span>
                </div>
                <div class="meta-row" v-if="item.inner_product !== undefined">
                  <strong>内积</strong>
                  <span class="meta-pill">{{ typeof item.inner_product === 'number' ? item.inner_product.toFixed(4) : item.inner_product }}</span>
                </div>
                <div class="meta-row" v-if="item.accuracy !== undefined">
                  <strong>精确度</strong>
                  <span class="meta-pill accuracy">{{ typeof item.accuracy === 'number' ? (item.accuracy * 100).toFixed(2) + '%' : item.accuracy }}</span>
                </div>
                <div class="meta-row" v-if="Array.isArray(item.keywords) && item.keywords.length">
                  <strong>关键词</strong>
                  <span class="kw" v-for="k in item.keywords" :key="k">{{ k }}</span>
                </div>
                <div class="meta-row" v-if="item.attributes">
                  <strong>属性</strong>
                  <span class="attr" v-for="(v, k) in item.attributes" :key="k">{{ k }}: {{ k === 'level' ? (levelDisplayNames[v] || v) : v }}</span>
                </div>
                <div class="meta-row" v-if="item.meta">
                  <strong>元信息</strong>
                  <span class="meta-pill" v-for="(v, k) in item.meta" :key="k">{{ k }}: {{ v }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'CloudDataAccessControlView',
  setup() {
    const router = useRouter()
    const route = useRoute()

    // 左侧导航
    const accessControlItems = [
      { name: '端侧模型访问控制', route: 'edge-model-access-control', icon: '⚙️' },
      { name: '云侧模型访问控制', route: 'cloud-model-access-control', icon: '☁️' },
      { name: '云上数据访问控制', route: 'cloud-data-access-control', icon: '💾' },
      { name: '链上数据访问控制', route: 'chain-data-access-control', icon: '⛓️' },
      { name: '视频数据访问控制', route: 'video-data-access-control', icon: '🎥' }
    ]
    const currentAccessControlType = ref('云上数据访问控制')
    const navigateToAccessControl = (name) => {
      currentAccessControlType.value = name
      const item = accessControlItems.find(item => item.name === name)
      if (item && route.name !== item.route) {
        router.push({ name: item.route })
      }
    }

    // 云上数据访问控制状态
    const API_BASE_URL = 'http://210.45.71.131:5000'
    const currentTime = ref('--')
    const indexStatus = ref('初始化中...')
    const statusMsg = ref('')
    const statusType = ref('success') // success | error | warning

    // 关键词
    const keywordInput = ref('')
    const keywords = ref([])
    const addKeyword = () => {
      const v = (keywordInput.value || '').trim()
      if (v && !keywords.value.includes(v)) {
        keywords.value.push(v)
      }
      keywordInput.value = ''
    }
    const removeKeyword = (idx) => {
      keywords.value.splice(idx, 1)
    }

    // 部门与级别
    // 先提供默认选项，避免初次点击出现无产线
    const departments = ref(['Safety', 'Technical'])
    const levels = reactive({
      Safety: ['cc', 'dd'],
      Technical: ['aa', 'bb']
    }) // { dept: [levelKey, ...] }
    const levelDisplayNames = {
      aa: '生产线1',
      bb: '生产线2',
      cc: '生产线3',
      dd: '生产线4'
    }

    const selectedDepartments = reactive(new Set())
    const selectedLevelsByDept = reactive({}) // { dept: Set(level) }

    const isDeptSelected = (dept) => selectedDepartments.has(dept)
    const toggleDepartment = (dept) => {
      // 自动确认输入框中的关键词
      if (keywordInput.value && keywordInput.value.trim()) {
        addKeyword()
      }
      if (selectedDepartments.has(dept)) {
        selectedDepartments.delete(dept)
      } else {
        selectedDepartments.add(dept)
      }
      // 同步级别选择容器
      if (!selectedLevelsByDept[dept]) {
        selectedLevelsByDept[dept] = new Set()
      }
    }
    const selectedDepartmentsArr = computed(() => Array.from(selectedDepartments))
    const selectedDepartmentsDisplay = computed(() => selectedDepartmentsArr.value.join(', ') || '未选择')

    const isLevelSelected = (dept, lv) => (selectedLevelsByDept[dept] || new Set()).has(lv)
    const toggleLevel = (dept, lv) => {
      if (!selectedLevelsByDept[dept]) selectedLevelsByDept[dept] = new Set()
      const set = selectedLevelsByDept[dept]
      if (set.has(lv)) set.delete(lv)
      else set.add(lv)
    }

    // 结果与陷门信息
    const searching = ref(false)
    const loadingResults = ref(false)
    const results = ref([])
    const resultsCountText = ref('')
    const trapdoorHtml = ref('执行搜索后将显示查询陷门信息...')

    const showStatus = (message, type = 'success') => {
      statusMsg.value = message
      statusType.value = type
      // 自动淡出提示，仅更新文本，不强制隐藏区域
      setTimeout(() => {
        statusMsg.value = ''
      }, 5000)
    }

    const updateCurrentTime = () => {
      const now = new Date()
      const pad = num => num.toString().padStart(2, '0')
      currentTime.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
    }

    const loadSystemInfo = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/info`)
        const data = await res.json()
        const apiDepts = Array.isArray(data.departments) ? data.departments : []
        if (apiDepts.length) {
          departments.value = apiDepts
        }

        // 清理并重建 levels，使其与后端保持一致
        const resetLevels = () => {
          Object.keys(levels).forEach(k => { delete levels[k] })
        }

        const assignLevelsForAllDepts = (levelsList) => {
          departments.value.forEach(d => { levels[d] = [...levelsList] })
        }

        const assignLevelsFromObjectMap = (objMap) => {
          resetLevels()
          departments.value.forEach(d => {
            if (Array.isArray(objMap[d])) {
              levels[d] = [...objMap[d]]
            } else {
              // 若后端无该部门映射，设为空数组
              levels[d] = []
            }
          })
        }

        // 多种后端返回兼容：
        // 1) data.levels 为对象: { dept: [levels] }
        // 2) data.levels 为数组: ['aa','bb'] -> 所有部门共用
        // 3) data.levels 为数组对象: [{department:'X',levels:[...]}, ...]
        // 4) 其他常见键名: data.levels_by_department / data.department_levels
        if (data.levels && typeof data.levels === 'object' && !Array.isArray(data.levels)) {
          assignLevelsFromObjectMap(data.levels)
        } else if (Array.isArray(data.levels) && data.levels.length) {
          if (typeof data.levels[0] === 'string') {
            // 扁平字符串数组：优先按默认规则为不同部门分配不同产线
            const list = data.levels
            const defaultMap = {
              Safety: ['cc', 'dd'],
              Technical: ['aa', 'bb']
            }
            const hasKnownDepts = departments.value.some(d => Object.prototype.hasOwnProperty.call(defaultMap, d))
            const listIncludesAllKnown = ['aa','bb','cc','dd'].every(x => list.includes(x))
            resetLevels()
            if (hasKnownDepts && listIncludesAllKnown) {
              departments.value.forEach(d => {
                if (defaultMap[d]) {
                  levels[d] = defaultMap[d].filter(x => list.includes(x))
                } else {
                  // 未知部门：回退为完整列表，避免完全无产线
                  levels[d] = [...list]
                }
              })
            } else {
              // 无法判定具体分配规则，则所有部门共用
              assignLevelsForAllDepts(list)
            }
          } else if (typeof data.levels[0] === 'object') {
            // 数组对象格式
            const objMap = {}
            data.levels.forEach(item => {
              const deptKey = item.department || item.dept || item.name
              const lv = item.levels || item.level || []
              if (deptKey) objMap[deptKey] = Array.isArray(lv) ? lv : []
            })
            assignLevelsFromObjectMap(objMap)
          }
        } else if (data.levels_by_department && typeof data.levels_by_department === 'object') {
          assignLevelsFromObjectMap(data.levels_by_department)
        } else if (data.department_levels && typeof data.department_levels === 'object') {
          assignLevelsFromObjectMap(data.department_levels)
        } else {
          // 后端未返回映射，若 departments 与默认不符，则为其填充空数组以提示后端未配置
          if (!(departments.value.includes('Safety') && departments.value.includes('Technical') && departments.value.length === 2)) {
            resetLevels()
            departments.value.forEach(d => { levels[d] = [] })
          }
        }
        indexStatus.value = '已构建完成'
        showStatus('服务已就绪，可以开始搜索', 'success')
      } catch (e) {
        console.error('加载系统信息失败:', e)
        indexStatus.value = '未知（后端未响应）'
        showStatus('搜索服务暂不可用，请检查后端服务', 'error')
      }
    }

    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/health`)
        const data = await res.json()
        if (data.status === 'healthy') {
          showStatus('健康检查通过', 'success')
        }
      } catch (e) {
        console.error('健康检查失败:', e)
      }
    }

    // 构造与 demo_index.html 完全一致的 query_attributesList
    const buildQueryAttributes = () => {
      const depts = selectedDepartmentsArr.value
      const result = []
      if (depts.length > 0) {
        depts.forEach(dept => {
          const lvSet = selectedLevelsByDept[dept]
          const lvArr = lvSet ? Array.from(lvSet) : []
          if (lvArr.length > 0) {
            lvArr.forEach(level => {
              result.push({ department: dept, level })
            })
          } else {
            result.push({ department: dept })
          }
        })
      } else {
        // demo_index.html 兜底逻辑：若无部门但有级别
        Object.keys(selectedLevelsByDept).forEach(dept => {
          const lvArr = Array.from(selectedLevelsByDept[dept] || [])
          if (lvArr.length > 0) {
            lvArr.forEach(level => {
              result.push({ department: dept, level })
            })
          }
        })
      }
      return result
    }

    const formatScore = (item) => {
      const s = typeof item.score === 'number' ? item.score : (typeof item.similarity === 'number' ? item.similarity : 0)
      return s.toFixed(4)
    }

    const getFileIcon = (filename) => {
      if (!filename) return '📄'
      const ext = filename.split('.').pop()?.toLowerCase()
      const iconMap = {
        'pdf': '📕',
        'doc': '📘', 'docx': '📘',
        'xls': '📗', 'xlsx': '📗', 'csv': '📗',
        'ppt': '📙', 'pptx': '📙',
        'txt': '📝',
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️',
        'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'mkv': '🎬',
        'mp3': '🎵', 'wav': '🎵', 'flac': '🎵',
        'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦',
        'json': '📋', 'xml': '📋', 'yaml': '📋', 'yml': '📋',
        'js': '📜', 'ts': '📜', 'py': '📜', 'java': '📜', 'cpp': '📜', 'c': '📜',
        'html': '🌐', 'css': '🎨', 'md': '📰'
      }
      return iconMap[ext] || '📄'
    }

    const fetchEncryptionLogs = async (payload) => {
      try {
        const res = await fetch(`${API_BASE_URL}/blockchain/encryption_logs`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
        })
        if (!res.ok) return null
        return await res.json()
      } catch (e) {
        console.log('获取加密日志失败:', e)
        return null
      }
    }

    const fetchQueryVectorLogs = async (payload) => {
      try {
        const res = await fetch(`${API_BASE_URL}/blockchain/query_vector_logs`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
        })
        if (!res.ok) return null
        return await res.json()
      } catch (e) {
        console.log('获取查询向量日志失败:', e)
        return null
      }
    }

    // 陷门信息展示逻辑与 demo_index.html 保持一致，department 保持英文原值，level 显示中文
    const renderTrapdoorHtml = (info) => {
      try {
        if (!info || typeof info !== 'object') return '<div class="no-real-data">暂无陷门信息</div>'
        const safe = info
        const parts = []
        if (Array.isArray(safe.keywords) && safe.keywords.length) {
          parts.push(`<div class="trap-row"><strong>关键词</strong><span class="trap-value">${safe.keywords.join(', ')}</span></div>`)
        } else if (Array.isArray(safe.query_keywords) && safe.query_keywords.length) {
          parts.push(`<div class="trap-row"><strong>关键词</strong><span class="trap-value">${safe.query_keywords.join(', ')}</span></div>`)
        }
        const levelDisplayNames = {
          aa: '生产线1',
          bb: '生产线2',
          cc: '生产线3',
          dd: '生产线4'
        }
        const addAttrs = (attrs) => {
          if (!attrs) return
          if (Array.isArray(attrs)) {
            attrs.forEach(a => {
              if (a && typeof a === 'object' && a.department) {
                parts.push(`<div class="trap-row"><strong>属性</strong><span class="trap-value">${a.department}${a.level ? ' - ' + (levelDisplayNames[a.level] || a.level) : ''}</span></div>`)
              } else {
                Object.entries(a).forEach(([k, v]) => {
                  parts.push(`<div class="trap-row"><strong>${k}</strong><span class="trap-value">${Array.isArray(v) ? v.join(', ') : v}</span></div>`)
                })
              }
            })
          } else if (typeof attrs === 'object') {
            Object.entries(attrs).forEach(([k, v]) => {
              parts.push(`<div class="trap-row"><strong>${k}</strong><span class="trap-value">${Array.isArray(v) ? v.map(lv => k==='level' ? (levelDisplayNames[lv]||lv) : lv).join(', ') : (k==='level' ? (levelDisplayNames[v]||v) : v)}</span></div>`)
            })
          }
        }
        if (safe.attributes) addAttrs(safe.attributes)
        else if (safe.query_attributes) addAttrs(safe.query_attributes)

        if (safe.timestamp) {
          parts.push(`<div class="trap-row"><strong>时间戳</strong><span class="trap-value">${safe.timestamp}</span></div>`)
        }

        if (safe.trapdoor_vector && Array.isArray(safe.trapdoor_vector)) {
          let dim = ''
          if (Array.isArray(safe.vector_shape) && safe.vector_shape.length > 0) {
            dim = safe.vector_shape.join(' × ')
          } else {
            dim = safe.trapdoor_vector.length
          }
          const preview = safe.trapdoor_vector.slice(0, 502).map(v => {
            if (typeof v === 'number') return v.toFixed(4)
            if (!isNaN(Number(v))) return Number(v).toFixed(4)
            return v
          }).join(', ')
          parts.push(`<div class="trap-row"><strong>向量维度</strong><span class="trap-value">${dim}</span></div><div class="trap-row vector-row"><strong>加密向量</strong><div class="vector-scroll">[${preview}]</div></div>`)
        } else if (safe.encrypted_trapdoor) {
          const text = typeof safe.encrypted_trapdoor === 'string' ? safe.encrypted_trapdoor : JSON.stringify(safe.encrypted_trapdoor)
          parts.push(`<div class="trap-row"><strong>加密陷门</strong><span class="vector-box">${text}</span></div>`)
        }

        return `<div class="trapdoor-content">${parts.join('')}</div>`
      } catch (e) {
        return `<div class=\"no-real-data\">显示查询陷门信息时出错: ${e.message}</div>`
      }
    }

    const performSearch = async () => {
      if (keywords.value.length === 0) {
        showStatus('请输入至少一个关键词', 'error')
        return
      }

      const requestBody = {
        keywords: keywords.value,
        query_attributes: buildQueryAttributes()
      }

      searching.value = true
      loadingResults.value = true
      results.value = []
      resultsCountText.value = ''
      trapdoorHtml.value = '正在生成查询陷门...'

      try {
        const res = await fetch(`${API_BASE_URL}/search`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestBody)
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()

        const enc = await fetchEncryptionLogs(requestBody)
        const qv = await fetchQueryVectorLogs(requestBody)

        if (data.success) {
          const resultData = {
            success: true,
            results: Array.isArray(data.results) ? data.results : [],
            count: typeof data.count === 'number' ? data.count : (Array.isArray(data.results) ? data.results.length : 0),
            total_count: data.total_count,
            trapdoor_info: data.trapdoor_info,
            access_info: data.access_info
          }

          results.value = resultData.results
          resultsCountText.value = `找到 ${resultData.count}${resultData.total_count !== undefined && resultData.total_count !== resultData.count ? ` / ${resultData.total_count}` : ''} 个匹配结果`

          // 优先使用查询向量日志
          if (qv && qv.success && qv.trapdoor_info) {
            trapdoorHtml.value = renderTrapdoorHtml(qv.trapdoor_info)
          } else if (enc && enc.trapdoor_info) {
            trapdoorHtml.value = renderTrapdoorHtml(enc.trapdoor_info)
          } else if (resultData.trapdoor_info) {
            trapdoorHtml.value = renderTrapdoorHtml(resultData.trapdoor_info)
          } else {
            trapdoorHtml.value = '<div class="no-real-data">暂无陷门信息</div>'
          }

          const statusMessage = resultData.total_count !== undefined && resultData.count !== resultData.total_count
            ? `搜索完成，显示 ${resultData.count} / ${resultData.total_count} 个结果`
            : `搜索完成，找到 ${resultData.count} 个结果`
          showStatus(statusMessage, 'success')
        } else {
          showStatus(`搜索失败: ${data.error || data.message || '未知错误'}`, 'error')
          results.value = []
          resultsCountText.value = ''
          trapdoorHtml.value = '<div class="no-real-data">搜索失败</div>'
        }
      } catch (e) {
        console.error('搜索错误:', e)
        showStatus(`请求失败: ${e.message}`, 'error')
        results.value = []
        resultsCountText.value = ''
        trapdoorHtml.value = '<div class="no-real-data">网络错误，请检查后端服务是否运行</div>'
      } finally {
        searching.value = false
        loadingResults.value = false
      }
    }

    const clearSearch = () => {
      keywords.value = []
      keywordInput.value = ''
      Object.keys(selectedLevelsByDept).forEach(k => selectedLevelsByDept[k]?.clear?.())
      selectedDepartments.clear()
      results.value = []
      resultsCountText.value = ''
      trapdoorHtml.value = '执行搜索后将显示查询陷门信息...'
      statusMsg.value = ''
    }

    onMounted(async () => {
      updateCurrentTime()
      setInterval(updateCurrentTime, 1000)
      await loadSystemInfo()
      checkHealth()
    })

    return {
      // 导航
      accessControlItems,
      currentAccessControlType,
      navigateToAccessControl,
      // 状态
      currentTime,
      indexStatus,
      statusMsg,
      statusType,
      // 搜索输入
      keywordInput,
      keywords,
      addKeyword,
      removeKeyword,
      // 部门与级别
      departments,
      levels,
      levelDisplayNames,
      selectedDepartmentsArr,
      selectedDepartmentsDisplay,
      isDeptSelected,
      toggleDepartment,
      isLevelSelected,
      toggleLevel,
      // 结果
      searching,
      loadingResults,
      results,
      resultsCountText,
      trapdoorHtml,
      performSearch,
      clearSearch,
      formatScore,
      getFileIcon,
      levelDisplayNames
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

.container {
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 200px);
}

.sidebar {
  width: 360px;
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.system-header {
  text-align: center;
  margin-bottom: 12px;
}

.system-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.3;
  margin-bottom: 6px;
}

.device-category {
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  border-bottom: 1px solid rgba(88, 178, 255, 0.12);
  font-size: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  font-size: 18px;
  line-height: 1;
}

.device-category:hover {
  background: rgba(128, 214, 255, 0.1);
}

.device-category.active {
  background: rgba(88, 178, 255, 0.2);
  border-color: rgba(88, 178, 255, 0.35);
  font-weight: 700;
}

.main-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.header {
  margin-bottom: 30px;
}
.header h1 {
  color: #e6f1ff;
  font-size: 24px;
  margin-bottom: 10px;
  letter-spacing: 1.4px;
  font-weight: normal;
}

.status-bar {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.status-card {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  color: #e6f1ff;
  padding: 12px 16px;
  border-radius: 10px;
  flex: 1;
  min-width: 220px;
  height: 50px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-label { font-size: 14px; opacity: 0.9; color: rgba(214, 232, 255, 0.8); white-space: nowrap; }
.status-value { font-size: 16px; font-weight: bold; color: #e6f1ff; flex: 1; }

.selection-panel {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 2px 24px 12px 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  margin-bottom: 24px;
}
.section-title { 
  color: #e6f1ff; 
  font-size: 20px; 
  margin-bottom: 16px; 
  border-bottom: 2px solid rgba(88, 178, 255, 0.3);
  padding-bottom: 10px;
}
.status-banner { padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; font-weight: 600; }
.status-banner.success { background: rgba(39, 174, 96, 0.15); border: 1px solid rgba(39, 174, 96, 0.4); color: rgba(39, 174, 96, 1); }
.status-banner.error { background: rgba(231, 76, 60, 0.15); border: 1px solid rgba(231, 76, 60, 0.4); color: #e74c3c; }
.status-banner.warning { background: rgba(255, 193, 7, 0.15); border: 1px solid rgba(255, 193, 7, 0.4); color: rgba(255, 193, 7, 1); }

.search-form { display: grid; grid-template-columns: 1fr; gap: 16px; }
.form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 8px;
}
.card-box {
  background: rgba(9, 32, 56, 0.18);
  border: 1px solid rgba(88, 178, 255, 0.13);
  border-radius: 14px;
  padding: 18px 18px 10px 18px;
  flex: 1 1 0;
  min-width: 220px;
  box-shadow: 0 2px 8px rgba(88, 178, 255, 0.07);
}
@media (max-width: 900px) {
  .form-row { flex-direction: column; gap: 12px; }
  .card-box { min-width: 0; }
}
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #e6f1ff; }
.form-group input { width: 100%; padding: 12px; border: 1px solid rgba(88, 178, 255, 0.2); border-radius: 8px; background: rgba(4, 19, 34, 0.6); color: #e6f1ff; }
.form-group input::placeholder { color: rgba(214, 232, 255, 0.5); }

.keyword-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.keyword-tag { background: rgba(88, 178, 255, 0.15); color: #e6f1ff; padding: 6px 12px; border-radius: 16px; display: inline-flex; align-items: center; gap: 8px; border: 1px solid rgba(88, 178, 255, 0.3); }
.keyword-tag .remove { background: rgba(88, 178, 255, 0.5); color: white; width: 18px; height: 18px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; font-size: 12px; }

.option-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { background: rgba(88, 178, 255, 0.12); color: #e6f1ff; padding: 6px 14px; border-radius: 18px; cursor: pointer; border: 1px solid rgba(88, 178, 255, 0.25); transition: all 0.2s; font-size: 14px; }
.chip:hover { background: rgba(88, 178, 255, 0.2); }
.chip.active { background: rgba(88, 178, 255, 0.3); border-color: rgba(88, 178, 255, 0.6); box-shadow: 0 2px 8px rgba(88, 178, 255, 0.25); }
.chip.disabled { opacity: 0.5; cursor: not-allowed; }
.chip.level { background: rgba(39, 174, 96, 0.12); border-color: rgba(39, 174, 96, 0.25); }
.chip.level.active { background: rgba(39, 174, 96, 0.25); border-color: rgba(39, 174, 96, 0.6); }

.level-groups { display: flex; flex-direction: column; gap: 12px; }
.level-group { background: rgba(4, 19, 34, 0.5); border: 1px solid rgba(88, 178, 255, 0.12); border-radius: 10px; padding: 12px; }
.level-dept-title { font-weight: 700; color: #e6f1ff; margin-bottom: 8px; }
.no-levels { color: rgba(214, 232, 255, 0.7); font-style: italic; padding: 8px; }

.form-actions { display: flex; gap: 12px; margin-top: 4px; }
.btn { padding: 12px 24px; border: 1px solid rgba(88, 178, 255, 0.3); border-radius: 8px; font-size: 14px; cursor: pointer; transition: all 0.3s; color: #e6f1ff; background: linear-gradient(135deg, rgba(88, 178, 255, 0.25), rgba(73, 197, 255, 0.25)); }
.btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(88, 178, 255, 0.3); }
.btn-primary { background: linear-gradient(135deg, rgba(88, 178, 255, 0.4), rgba(73, 197, 255, 0.4)); border-color: rgba(88, 178, 255, 0.6); font-weight: 600; }
.btn-danger { background: linear-gradient(135deg, rgba(231, 76, 60, 0.25), rgba(231, 76, 60, 0.25)); border-color: rgba(231, 76, 60, 0.4); }

.result-section { margin-top: 10px; margin-bottom: 24px; }
.result-count { background: rgba(88, 178, 255, 0.15); border: 1px solid rgba(88, 178, 255, 0.3); color: #e6f1ff; padding: 10px 14px; border-radius: 8px; margin-bottom: 14px; font-weight: 700; display: inline-block; }
.result-scroll-container {
  max-height: 500px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
}
.result-scroll-container::-webkit-scrollbar {
  width: 8px;
}
.result-scroll-container::-webkit-scrollbar-track {
  background: rgba(4, 19, 34, 0.5);
  border-radius: 4px;
}
.result-scroll-container::-webkit-scrollbar-thumb {
  background: rgba(88, 178, 255, 0.4);
  border-radius: 4px;
}
.result-scroll-container::-webkit-scrollbar-thumb:hover {
  background: rgba(88, 178, 255, 0.6);
}
.result-list { display: flex; flex-direction: column; gap: 12px; }
.result-item { background: rgba(9, 32, 56, 0.6); border-radius: 10px; padding: 16px; border: 1px solid rgba(88, 178, 255, 0.12); color: #e6f1ff; }
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.result-item h3 { color: #e6f1ff; margin-bottom: 0; font-size: 18px; display: flex; align-items: center; gap: 8px; flex: 1; }
.rank-badge { background: linear-gradient(135deg, rgba(255, 167, 38, 0.25), rgba(255, 138, 0, 0.25)); border: 1px solid rgba(255, 167, 38, 0.5); color: #ffa726; padding: 4px 12px; border-radius: 14px; font-size: 13px; font-weight: 700; white-space: nowrap; }
.file-icon { font-size: 22px; line-height: 1; }
.meta-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 6px 0; }
.meta-row strong { color: rgba(214, 232, 255, 0.9); min-width: 56px; font-size: 13px; }
.kw { background: rgba(255, 193, 7, 0.2); color: #ffd54f; padding: 4px 10px; border-radius: 12px; font-size: 13px; border: 1px solid rgba(255, 193, 7, 0.4); font-weight: 600; }
.attr { background: rgba(156, 39, 176, 0.15); color: #ce93d8; padding: 4px 10px; border-radius: 12px; font-size: 13px; border: 1px solid rgba(156, 39, 176, 0.4); font-weight: 600; }
.meta-pill { background: rgba(224, 247, 250, 0.1); color: #e6f1ff; padding: 4px 10px; border-radius: 12px; font-size: 13px; border: 1px solid rgba(0, 96, 100, 0.35); }
.meta-pill.score { background: rgba(76, 175, 80, 0.15); color: #81c784; border-color: rgba(76, 175, 80, 0.4); font-weight: 700; }
.meta-pill.accuracy { background: rgba(33, 150, 243, 0.15); color: #64b5f6; border-color: rgba(33, 150, 243, 0.4); font-weight: 700; }
.no-results { text-align: center; padding: 24px; color: rgba(214, 232, 255, 0.7); }

.trapdoor-section { background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9)); border-radius: 20px; padding: 24px; border: 1px solid rgba(88, 178, 255, 0.12); box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36); }
.trapdoor-box { border: 1px solid rgba(88, 178, 255, 0.2); border-radius: 8px; padding: 16px; background: rgba(4, 19, 34, 0.6); color: #e6f1ff; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

/* 陷门信息样式优化 - 使用深度选择器应用到v-html内容 */
.trapdoor-box :deep(.trapdoor-content) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.trapdoor-box :deep(.trap-row) {
  display: flex !important;
  align-items: center !important;
  gap: 10px;
  margin-bottom: 0;
  font-size: 14px;
  flex-wrap: nowrap !important;
}
.trapdoor-box :deep(.trap-row strong) {
  color: #e6f1ff !important;
  min-width: 90px;
  font-weight: 600;
  font-size: 16px;
}
.trapdoor-box :deep(.trap-row .trap-value) {
  font-weight: bold !important;
  color: #ffa726 !important;
  font-size: 17px;
  background: rgba(255,167,38,0.12) !important;
  border-radius: 6px;
  padding: 4px 12px;
  margin-left: 4px;
}
.trapdoor-box :deep(.trap-row .vector-box) {
  font-size: 13px;
  color: #e6f1ff;
  background: rgba(9,32,56,0.3);
  border-radius: 4px;
  padding: 4px 8px;
  margin-left: 6px;
}
.trapdoor-box :deep(.trap-row.vector-row) {
  display: flex !important;
  align-items: center !important;
  gap: 10px;
  flex-wrap: nowrap !important;
}
.trapdoor-box :deep(.trap-row.vector-row strong) {
  flex-shrink: 0;
  white-space: nowrap;
}
.trapdoor-box :deep(.vector-scroll) {
  flex: 0 1 auto;
  min-width: 300px;
  max-width: 800px;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  background: transparent;
  border: 1px solid rgba(88, 178, 255, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 15px;
  color: #ffa726;
  font-weight: bold;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; }
.chip.tiny { padding: 3px 8px; font-size: 12px; border-radius: 12px; }
.chip.tiny.attr { background: rgba(243, 229, 245, 0.1); border: 1px solid rgba(106, 27, 154, 0.35); }

.loading { text-align: center; padding: 24px; }
.spinner { width: 40px; height: 40px; border: 4px solid rgba(243, 243, 243, 0.2); border-top: 4px solid rgba(88, 178, 255, 1); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1100px) {
  .main-content {
    padding: 20px 15px;
  }
  .sidebar {
    width: 100%;
  }
}
</style>

<style>
/* 非作用域样式用于滚动条自定义 */
.vector-scroll::-webkit-scrollbar {
  height: 10px;
}
.vector-scroll::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 6px;
}
.vector-scroll::-webkit-scrollbar-thumb {
  background: rgba(88, 178, 255, 0.4);
  border-radius: 6px;
}
.vector-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(88, 178, 255, 0.6);
}
</style>

