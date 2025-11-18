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
          <h1>视频脱敏与访问控制管理平台</h1>
        </div>

        <!-- 状态栏 -->
        <div class="status-bar">
          <div class="status-card">
            <span class="status-label">🕒 当前时间：</span>
            <span class="status-value">{{ currentTime }}</span>
          </div>
          <div class="status-card">
            <span class="status-label">🏢 级别选择:</span>
            <select v-model="selectedDepartmentId" class="department-select">
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }} ({{ dept.level }})
              </option>
            </select>
          </div>
          <div class="status-card">
            <span class="status-label">⚙️ 运行设备:</span>
            <select v-model="taskForm.device" class="department-select">
              <option value="cpu">CPU</option>
              <option value="cuda">CUDA (Auto)</option>
              <option value="cuda:0">CUDA:0</option>
              <option value="cuda:1">CUDA:1</option>
            </select>
          </div>
        </div>

        <!-- 级别可见对象 -->
        <div class="permission-section selection-panel">
          <h2 class="section-title">👁️ 级别可见对象</h2>
          <div class="panel-subtitle-text">蓝色为可见对象，灰色为系统自动脱敏对象。</div>
          <div class="object-inline">
            <div
              v-for="item in permissionCards"
              :key="item.key"
              class="object-pill"
              :class="{ allowed: item.allowed }"
            >
              <span class="pill-checkbox" :class="{ checked: item.allowed }"></span>
              <span class="pill-label">{{ item.label }}</span>
            </div>
          </div>
        </div>

        <!-- 素材库与上传 -->
        <div class="video-section selection-panel">
          <div class="panel-header-with-actions">
            <h2 class="section-title">📹 素材库与上传</h2>
            <div class="actions">
              <label class="upload-btn btn btn-info" :class="{ disabled: isUploading }">
                选择本地视频
                <input type="file" accept="video/*" @change="handleFileChange" :disabled="isUploading" />
              </label>
            </div>
          </div>

          <div class="selection-info" v-if="uploadFileName || selectedLibraryId">
            <span v-if="uploadFileName">已选择本地文件：{{ uploadFileName }}</span>
            <span v-else-if="selectedLibraryId">
              已选择素材库视频：{{ currentLibraryVideo?.display_name || currentLibraryVideo?.filename }}
            </span>
            <button class="btn btn-link" @click="clearSelections">清空选择</button>
          </div>

          <div class="library-grid">
            <div
              v-for="item in libraryItems"
              :key="item.id"
              class="video-card"
              :class="{ active: selectedLibraryId === item.id }"
              @click="selectLibraryVideo(item.id)"
            >
              <div class="video-cover">
                <img v-if="item.cover_url" :src="buildAssetUrl(item.cover_url)" :alt="item.display_name" />
                <div v-else class="cover-placeholder">预览生成中</div>
              </div>
              <div class="video-meta">
                <div class="video-name">{{ item.display_name }}</div>
                <div class="video-tags">
                  <span>{{ item.duration_human }}</span>
                  <span>{{ item.size_human }}</span>
                </div>
              </div>
            </div>
            <div v-if="!libraryItems.length && !libraryLoading" class="empty-tip">
              暂无素材，请上传视频后刷新。
            </div>
          </div>
        </div>

        <!-- 视频脱敏与展示 -->
        <div class="processing-section selection-panel">
          <h2 class="section-title">🎬 视频脱敏与展示</h2>
          <div class="panel-subtitle-text">支持素材库选择或本地上传，处理完成后可直接播放与下载。</div>
          <div class="processing-body">
            <div class="processing-actions">
              <button
                class="btn btn-primary"
                @click="startProcessing"
                :disabled="isSubmitting || isUploading || !selectedDepartmentId || (!uploadFile && !selectedLibraryId)"
              >
                {{ isSubmitting ? '处理中...' : '处理视频' }}
              </button>
              <div class="status-message" :class="currentJob?.status">
                {{ statusMessage || '请选择部门和视频后开始处理' }}
              </div>
            </div>

            <div v-if="currentJob" class="job-status">
              <div class="job-header">
                <div>
                  <strong>任务编号:</strong> {{ currentJob.job_id }}
                </div>
                <div class="job-state" :class="currentJob.status">
                  {{ jobStatusText }}
                </div>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${jobProgress}%` }"></div>
              </div>
              <p class="job-message">{{ currentJob.message }}</p>
            </div>

            <div v-if="processedVideoUrl" class="video-preview">
              <video :src="processedVideoUrl" controls playsinline></video>
              <div class="video-actions">
                <a class="btn btn-info" :href="processedVideoUrl" download>下载脱敏视频</a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'VideoAccessControlView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const API_BASE = 'http://210.45.71.131:5005'

    const accessControlItems = [
      { name: '端侧模型访问控制', route: 'edge-model-access-control', icon: '⚙️' },
      { name: '云侧模型访问控制', route: 'cloud-model-access-control', icon: '☁️' },
      { name: '云上数据访问控制', route: 'cloud-data-access-control', icon: '💾' },
      { name: '链上数据访问控制', route: 'chain-data-access-control', icon: '⛓️' },
      { name: '视频数据访问控制', route: 'video-data-access-control', icon: '🎥' }
    ]

    const currentTime = ref('--')
    const currentAccessControlType = ref('视频数据访问控制')
    const departments = ref([])
    const objectCatalog = ref([])
    const libraryItems = ref([])
    const selectedDepartmentId = ref('')
    const selectedLibraryId = ref('')
    const uploadFile = ref(null)
    const uploadFileName = ref('')
    const libraryLoading = ref(false)
    const statusMessage = ref('')
    const currentJob = ref(null)
    const isSubmitting = ref(false)
    const isUploading = ref(false)
    const pollingTimer = ref(null)

    const taskForm = ref({
      device: 'cuda'
    })

    const activeDepartment = computed(() => {
      if (!departments.value.length) return null
      return departments.value.find(item => item.id === selectedDepartmentId.value) || departments.value[0]
    })

    const permissionCards = computed(() => {
      const visibleSet = new Set(activeDepartment.value?.visible_objects || [])
      return objectCatalog.value.map(item => ({
        ...item,
        allowed: visibleSet.has(item.key)
      }))
    })

    const currentLibraryVideo = computed(() =>
      libraryItems.value.find(item => item.id === selectedLibraryId.value) || null
    )

    const jobProgress = computed(() => Math.round((currentJob.value?.progress || 0) * 100))

    const processedVideoUrl = computed(() => {
      const path = currentJob.value?.video_url
      if (!path) return ''
      return path.startsWith('http') ? path : `${API_BASE}${path}`
    })

    const jobStatusText = computed(() => {
      const status = currentJob.value?.status
      if (status === 'completed') return '处理完成'
      if (status === 'failed') return '处理失败'
      if (status === 'processing') return '处理中'
      return '排队中'
    })

    const buildAssetUrl = path => {
      if (!path) return ''
      return path.startsWith('http') ? path : `${API_BASE}${path}`
    }

    const fetchJSON = async (path, options = {}) => {
      const response = await fetch(`${API_BASE}${path}`, options)
      let payload = {}
      try {
        payload = await response.json()
      } catch (err) {
        // ignore parse error
      }
      if (!response.ok) {
        const detail = payload?.detail || payload?.message || response.statusText
        throw new Error(detail)
      }
      return payload
    }

    const fetchDepartments = async () => {
      const data = await fetchJSON('/api/departments')
      departments.value = data.data || []
      if (!selectedDepartmentId.value && departments.value.length) {
        // 默认选择级刳1 (L2)
        const defaultDept = departments.value.find(dept => dept.level === 'L2')
        selectedDepartmentId.value = defaultDept ? defaultDept.id : departments.value[0].id
      }
    }

    const fetchObjects = async () => {
      const data = await fetchJSON('/api/objects')
      objectCatalog.value = data.data || []
    }

    const fetchLibrary = async refresh => {
      libraryLoading.value = true
      try {
        const query = refresh ? '?refresh=true' : ''
        const data = await fetchJSON(`/api/videos/library${query}`)
        libraryItems.value = data.data || []
      } finally {
        libraryLoading.value = false
      }
    }

    const refreshLibrary = () => fetchLibrary(true)

    const selectLibraryVideo = id => {
      selectedLibraryId.value = id
      uploadFile.value = null
      uploadFileName.value = ''
    }

    const clearSelections = () => {
      selectedLibraryId.value = ''
      uploadFile.value = null
      uploadFileName.value = ''
    }

    const handleFileChange = async event => {
      const [file] = event.target.files || []
      if (!file) return
      statusMessage.value = '正在上传本地视频...'
      uploadFile.value = null
      isUploading.value = true
      try {
        const formData = new FormData()
        formData.append('file', file)
        const { data } = await fetchJSON('/api/videos/library/upload', {
          method: 'POST',
          body: formData
        })
        const payload = data
        libraryItems.value = [payload, ...libraryItems.value.filter(item => item.id !== payload.id)]
        selectedLibraryId.value = payload.id
        uploadFileName.value = payload.display_name || payload.filename
        statusMessage.value = '上传成功，已添加到素材库'
      } catch (err) {
        statusMessage.value = err.message || '上传失败，请重试或直接点击处理视频'
        uploadFile.value = file
        uploadFileName.value = file.name
      } finally {
        isUploading.value = false
        if (fileInputRef.value) {
          fileInputRef.value.value = ''
        }
      }
    }

    const startProcessing = async () => {
      if (!selectedDepartmentId.value) {
        statusMessage.value = '请先选择部门'
        return
      }
      if (!selectedLibraryId.value && !uploadFile.value) {
        statusMessage.value = '请选择素材库视频或上传本地文件'
        return
      }

      isSubmitting.value = true
      statusMessage.value = '正在创建脱敏任务...'
      try {
        const formData = new FormData()
        formData.append('department_id', selectedDepartmentId.value)
        formData.append('device', taskForm.value.device || 'cpu')
        if (selectedLibraryId.value && !uploadFile.value) {
          formData.append('source', 'library')
          formData.append('library_id', selectedLibraryId.value)
        } else if (uploadFile.value) {
          formData.append('source', 'upload')
          formData.append('file', uploadFile.value, uploadFile.value.name)
        } else if (selectedLibraryId.value) {
          formData.append('source', 'library')
          formData.append('library_id', selectedLibraryId.value)
        }
        const { data } = await fetchJSON('/api/videos/process', {
          method: 'POST',
          body: formData
        })
        currentJob.value = data
        statusMessage.value = '任务已提交，等待处理完成...'
        startPollingJob(data.job_id)
        if (!selectedLibraryId.value) {
          await fetchLibrary(true)
        }
      } catch (err) {
        statusMessage.value = err.message || '任务提交失败'
      } finally {
        isSubmitting.value = false
      }
    }

    const startPollingJob = jobId => {
      stopPolling()
      if (!jobId) return
      pollingTimer.value = window.setInterval(async () => {
        try {
          const { data } = await fetchJSON(`/api/videos/jobs/${jobId}`)
          currentJob.value = data
          if (data.status === 'completed') {
            statusMessage.value = '脱敏完成，可播放与下载。'
            stopPolling()
          } else if (data.status === 'failed') {
            statusMessage.value = data.message || '任务失败'
            stopPolling()
          }
        } catch (err) {
          statusMessage.value = err.message
          stopPolling()
        }
      }, 2000)
    }

    const stopPolling = () => {
      if (pollingTimer.value) {
        clearInterval(pollingTimer.value)
        pollingTimer.value = null
      }
    }

    const updateClock = () => {
      const now = new Date()
      const pad = num => num.toString().padStart(2, '0')
      currentTime.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(
        now.getHours()
      )}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
    }

    let clockTimer = null

    const navigateToAccessControl = name => {
      currentAccessControlType.value = name
      const target = accessControlItems.find(item => item.name === name)
      if (target && target.route && target.route !== route.name) {
        router.push({ name: target.route })
      }
    }

    const syncAccessType = () => {
      const matched = accessControlItems.find(item => item.route === route.name)
      if (matched) {
        currentAccessControlType.value = matched.name
      }
    }

    watch(
      () => route.name,
      () => syncAccessType(),
      { immediate: true }
    )

    onMounted(async () => {
      updateClock()
      clockTimer = window.setInterval(updateClock, 1000)
      try {
        await Promise.all([fetchDepartments(), fetchObjects()])
        await fetchLibrary(false)
      } catch (err) {
        statusMessage.value = err.message
      }
    })

    onUnmounted(() => {
      stopPolling()
      if (clockTimer) {
        clearInterval(clockTimer)
        clockTimer = null
      }
    })

    return {
      accessControlItems,
      currentAccessControlType,
      currentTime,
      departments,
      objectCatalog,
      libraryItems,
      libraryLoading,
      selectedDepartmentId,
      selectedLibraryId,
      uploadFileName,
      taskForm,
      permissionCards,
      currentLibraryVideo,
      statusMessage,
      startProcessing,
      refreshLibrary,
      selectLibraryVideo,
      handleFileChange,
      clearSelections,
      isSubmitting,
      isUploading,
      currentJob,
      jobProgress,
      jobStatusText,
      processedVideoUrl,
      buildAssetUrl,
      navigateToAccessControl
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
  margin-bottom: 24px;
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

.status-label {
  font-size: 14px;
  opacity: 0.9;
  color: rgba(214, 232, 255, 0.8);
  white-space: nowrap;
}

.status-value {
  font-size: 16px;
  font-weight: bold;
  color: #e6f1ff;
  flex: 1;
}

.department-select {
  border: 1px solid rgba(88, 178, 255, 0.3);
  border-radius: 8px;
  padding: 8px 12px;
  background: rgba(4, 19, 34, 0.6);
  color: #e6f1ff;
  outline: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.department-select:hover {
  border-color: rgba(88, 178, 255, 0.5);
  background: rgba(4, 19, 34, 0.8);
}

.selection-panel {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 2px 24px 12px 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  margin-bottom: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  color: #e6f1ff;
  font-size: 20px;
  margin-bottom: 20px;
  font-weight: 600;
  border-bottom: 2px solid rgba(88, 178, 255, 0.3);
  padding-bottom: 10px;
}

.panel-subtitle-text {
  color: rgba(214, 232, 255, 0.7);
  font-size: 13px;
  margin-bottom: 16px;
}

.panel-header-with-actions {
  display: block;
  margin-bottom: 16px;
}

.panel-header-with-actions .section-title {
  margin-bottom: 12px;
}

.panel-subtitle {
  color: rgba(214, 232, 255, 0.7);
  font-size: 13px;
}

.object-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.object-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(88, 178, 255, 0.1);
  border: 1px solid rgba(88, 178, 255, 0.25);
  font-size: 14px;
  color: rgba(214, 232, 255, 0.7);
  transition: all 0.2s ease;
}

.object-pill.allowed {
  background: rgba(88, 178, 255, 0.2);
  border-color: rgba(88, 178, 255, 0.5);
  color: #e6f1ff;
}

.pill-checkbox {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid rgba(214, 232, 255, 0.4);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(4, 19, 34, 0.6);
}

.pill-checkbox.checked {
  background: rgba(88, 178, 255, 0.8);
  border-color: rgba(88, 178, 255, 1);
  position: relative;
}

.pill-checkbox.checked::after {
  content: '';
  width: 6px;
  height: 3px;
  border-left: 2px solid #fff;
  border-bottom: 2px solid #fff;
  transform: rotate(-45deg);
  display: inline-block;
}

.pill-label {
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  color: #e6f1ff;
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.25), rgba(73, 197, 255, 0.25));
  font-weight: 600;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(88, 178, 255, 0.3);
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.4), rgba(73, 197, 255, 0.4));
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.4), rgba(73, 197, 255, 0.4));
  border-color: rgba(88, 178, 255, 0.6);
}

.btn-info {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.3), rgba(73, 197, 255, 0.3));
  border-color: rgba(88, 178, 255, 0.3);
}

.upload-btn input {
  display: none;
}

.upload-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.selection-info {
  margin-top: 12px;
  margin-bottom: 12px;
  padding: 10px 14px;
  background: rgba(88, 178, 255, 0.1);
  border: 1px solid rgba(88, 178, 255, 0.2);
  border-radius: 8px;
  color: #e6f1ff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 14px;
}

.btn-link {
  background: none;
  border: none;
  color: rgba(88, 178, 255, 1);
  padding: 4px 8px;
  font-size: 13px;
  text-decoration: underline;
}

.btn-link:hover {
  color: rgba(73, 197, 255, 1);
  transform: none;
  box-shadow: none;
}

.library-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.video-card {
  background: rgba(9, 32, 56, 0.6);
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
}

.video-card:hover {
  border-color: rgba(88, 178, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.video-card.active {
  border-color: rgba(88, 178, 255, 0.8);
  box-shadow: 0 0 20px rgba(88, 178, 255, 0.3);
}

.video-cover {
  width: 100%;
  height: 140px;
  overflow: hidden;
  background: rgba(4, 19, 34, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  color: rgba(214, 232, 255, 0.5);
  font-size: 13px;
}

.video-meta {
  padding: 12px;
}

.video-name {
  font-weight: 600;
  margin-bottom: 8px;
  color: #e6f1ff;
  font-size: 14px;
}

.video-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.video-tags span {
  display: inline-block;
  background: rgba(88, 178, 255, 0.15);
  border: 1px solid rgba(88, 178, 255, 0.25);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: rgba(214, 232, 255, 0.8);
}

.empty-tip {
  grid-column: 1 / -1;
  text-align: center;
  padding: 30px 0;
  color: rgba(214, 232, 255, 0.6);
  font-size: 14px;
}

.processing-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.processing-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.status-message {
  font-size: 14px;
  color: rgba(214, 232, 255, 0.8);
}

.status-message.completed {
  color: rgba(39, 174, 96, 1);
}

.status-message.failed {
  color: rgba(231, 76, 60, 1);
}

.status-message.processing {
  color: rgba(255, 193, 7, 1);
}

.job-status {
  margin-top: 16px;
  background: rgba(9, 32, 56, 0.6);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(88, 178, 255, 0.12);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #e6f1ff;
}

.job-state {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  text-transform: capitalize;
  font-weight: 600;
}

.job-state.completed {
  background: rgba(39, 174, 96, 0.2);
  border: 1px solid rgba(39, 174, 96, 0.4);
  color: rgba(39, 174, 96, 1);
}

.job-state.processing {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.4);
  color: rgba(255, 193, 7, 1);
}

.job-state.failed {
  background: rgba(231, 76, 60, 0.2);
  border: 1px solid rgba(231, 76, 60, 0.4);
  color: rgba(231, 76, 60, 1);
}

.progress-bar {
  height: 10px;
  border-radius: 8px;
  background: rgba(4, 19, 34, 0.8);
  overflow: hidden;
  border: 1px solid rgba(88, 178, 255, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(88, 178, 255, 0.6), rgba(73, 197, 255, 0.6));
  transition: width 0.3s ease;
}

.job-message {
  margin-top: 10px;
  color: rgba(214, 232, 255, 0.8);
  font-size: 13px;
}

.video-preview {
  margin-top: 16px;
}

.video-preview video {
  width: 100%;
  max-height: 500px;
  border-radius: 12px;
  border: 1px solid rgba(88, 178, 255, 0.2);
  background: #000;
}

.video-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 1100px) {
  .container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
    padding: 16px;
  }

  .device-category {
    flex: 1;
    justify-content: center;
    white-space: nowrap;
  }

  .main-content {
    padding: 20px 15px;
  }
}

@media (max-width: 768px) {
  .page-shell {
    padding: 16px;
  }

  .status-bar {
    flex-direction: column;
  }

  .status-card {
    min-width: 100%;
  }

  .library-grid {
    grid-template-columns: 1fr;
  }
}
</style>
