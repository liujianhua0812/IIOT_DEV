<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { fetchUserProfile, updateUserProfile } from '@/services/api'

const router = useRouter()
const { user, isAuthenticated, updateUser } = useAuth()

// 如果未登录，重定向到登录页
if (!isAuthenticated.value) {
  router.push({ name: 'login' })
}

const formData = ref({
  username: '',
  email: '',
})

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

onMounted(async () => {
  loading.value = true
  // 先使用本地存储的用户信息
  if (user.value) {
    formData.value = {
      username: user.value.username || '',
      email: user.value.email || '',
    }
  }
  
  // 尝试从服务器获取最新信息
  try {
    const response = await fetchUserProfile()
    formData.value = {
      username: response.data.username || '',
      email: response.data.email || '',
    }
    // 更新本地用户信息
    updateUser(response.data)
  } catch (error) {
    // 如果获取失败，继续使用本地存储的用户信息
    if (!user.value) {
      errorMessage.value = '获取用户信息失败，请重新登录'
    }
  } finally {
    loading.value = false
  }
})

const handleSave = async () => {
  if (!formData.value.username || !formData.value.email) {
    errorMessage.value = '请填写所有必填项'
    return
  }

  // 简单的邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }

  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await updateUserProfile(formData.value)
    updateUser(response.data)
    successMessage.value = '个人信息更新成功'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = error.response?.data?.message || error.message || '更新失败，请稍后重试'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="profile-view">
    <div class="profile-container">
      <div class="profile-header">
        <h1>编辑个人信息</h1>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <form v-else @submit.prevent="handleSave" class="profile-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="请输入邮箱地址"
            required
          />
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="router.back()">
            取消
          </button>
          <button type="submit" class="save-btn" :disabled="saving">
            <span v-if="saving">保存中...</span>
            <span v-else>保存</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.profile-view {
  min-height: 100%;
  padding: 32px;
  background: #f5f7fa;
}

.profile-container {
  max-width: 600px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 40px;
}

.profile-header {
  margin-bottom: 32px;
}

.profile-header h1 {
  font-size: 24px;
  margin: 0;
  color: #303133;
  font-weight: 600;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.form-group input {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  background: #ffffff;
  color: #606266;
  font-size: 14px;
  transition: all 0.3s ease;
  outline: none;
}

.form-group input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.form-group input::placeholder {
  color: #c0c4cc;
}

.success-message {
  padding: 12px 16px;
  border-radius: 8px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  color: #409eff;
  font-size: 14px;
  text-align: center;
}

.error-message {
  padding: 12px 16px;
  border-radius: 8px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  color: #f56c6c;
  font-size: 14px;
  text-align: center;
}

.form-actions {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.cancel-btn,
.save-btn {
  flex: 1;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  border: 1px solid #dcdfe6;
  background: #ffffff;
  color: #606266;
}

.cancel-btn:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

.save-btn {
  border: none;
  color: #ffffff;
  background: #409eff;
}

.save-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

