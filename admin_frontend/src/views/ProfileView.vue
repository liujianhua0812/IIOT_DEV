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
        <button class="back-btn" @click="router.back()">
          <span>←</span> 返回
        </button>
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
  min-height: calc(100vh - 80px);
  padding: 32px;
  background: radial-gradient(circle at top, rgba(4, 17, 30, 0.98), rgba(3, 11, 20, 1));
}

.profile-container {
  max-width: 600px;
  margin: 0 auto;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.85), rgba(6, 25, 44, 0.9));
  border-radius: 24px;
  border: 1px solid rgba(88, 178, 255, 0.08);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.32);
  padding: 48px;
}

.profile-header {
  margin-bottom: 40px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: #80d6ff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 24px;
}

.back-btn:hover {
  color: #49c5ff;
}

.profile-header h1 {
  font-size: 32px;
  margin: 0;
  letter-spacing: 1.6px;
  color: #e6f1ff;
}

.loading {
  text-align: center;
  padding: 40px;
  color: rgba(214, 232, 255, 0.78);
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
  color: #d6ecff;
  letter-spacing: 0.5px;
}

.form-group input {
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid rgba(128, 214, 255, 0.2);
  background: rgba(4, 16, 27, 0.6);
  color: #e6f1ff;
  font-size: 15px;
  transition: all 0.3s ease;
  outline: none;
}

.form-group input:focus {
  border-color: #49c5ff;
  background: rgba(4, 16, 27, 0.8);
  box-shadow: 0 0 0 3px rgba(73, 197, 255, 0.15);
}

.form-group input::placeholder {
  color: rgba(214, 232, 255, 0.4);
}

.success-message {
  padding: 12px 16px;
  border-radius: 8px;
  background: rgba(73, 197, 255, 0.15);
  border: 1px solid rgba(73, 197, 255, 0.3);
  color: #49c5ff;
  font-size: 14px;
  text-align: center;
}

.error-message {
  padding: 12px 16px;
  border-radius: 8px;
  background: rgba(255, 154, 158, 0.15);
  border: 1px solid rgba(255, 154, 158, 0.3);
  color: #ff9a9e;
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
  padding: 14px 28px;
  border-radius: 999px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  border: 1px solid rgba(128, 214, 255, 0.36);
  background: transparent;
  color: #80d6ff;
}

.cancel-btn:hover {
  background: rgba(128, 214, 255, 0.18);
}

.save-btn {
  border: none;
  color: #0b2338;
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  box-shadow: 0 16px 32px rgba(73, 197, 255, 0.25);
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 18px 38px rgba(73, 197, 255, 0.35);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

