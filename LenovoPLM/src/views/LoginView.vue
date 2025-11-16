<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login } from '@/services/api'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route = useRoute()
const { login: setAuth } = useAuth()

const formData = ref({
  username: '',
  password: '',
})

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

onMounted(() => {
  // 如果从注册页面跳转过来，显示成功提示
  if (route.query.registered === 'true') {
    successMessage.value = '注册成功，请登录'
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  }
})

const handleLogin = async () => {
  if (!formData.value.username || !formData.value.password) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await login({
      username: formData.value.username,
      password: formData.value.password,
    })
    
    // 保存用户信息和 token
    if (response.data.token && response.data.user) {
      setAuth(response.data.user, response.data.token)
    }
    
    // 登录成功后跳转
    router.push({ name: 'home' })
  } catch (error) {
    errorMessage.value = error.response?.data?.message || error.message || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-view">
    <div class="auth-container">
      <div class="auth-visual">
        <div class="pulse"></div>
        <div class="orb"></div>
        <div class="grid"></div>
      </div>
      
      <div class="auth-form-wrapper">
        <div class="auth-header">
          <div class="brand-mark">MMI</div>
          <h1>欢迎回来</h1>
          <p>登录多模态网络工业互联网平台</p>
        </div>

        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              placeholder="请输入用户名"
              autocomplete="username"
              required
            />
          </div>

          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              placeholder="请输入密码"
              autocomplete="current-password"
              required
            />
          </div>

          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading">登录中...</span>
            <span v-else>登录</span>
          </button>

          <div class="auth-footer">
            <span>还没有账号？</span>
            <router-link to="/register" class="link">立即注册</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: radial-gradient(circle at top, rgba(4, 17, 30, 0.98), rgba(3, 11, 20, 1));
}

.auth-container {
  position: relative;
  width: 100%;
  max-width: 480px;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.85), rgba(6, 25, 44, 0.9));
  border-radius: 24px;
  border: 1px solid rgba(88, 178, 255, 0.08);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.32);
  overflow: hidden;
  padding: 48px;
}

.auth-visual {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  opacity: 0.3;
}

.auth-visual .grid {
  position: absolute;
  inset: 12%;
  border-radius: 50%;
  border: 1px solid rgba(128, 214, 255, 0.18);
  background-image: radial-gradient(circle, rgba(128, 214, 255, 0.15) 1px, transparent 1px);
  background-size: 12px 12px;
}

.auth-visual .orb {
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(73, 197, 255, 0.65), rgba(11, 38, 66, 0));
  filter: blur(2px);
  animation: orbit 12s linear infinite;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.auth-visual .pulse {
  position: absolute;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(41, 131, 251, 0.8), rgba(6, 25, 44, 0.1));
  box-shadow: 0 0 30px rgba(41, 131, 251, 0.6);
  animation: pulse 3.5s ease-in-out infinite;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.9;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 1;
  }
}

@keyframes orbit {
  0% {
    transform: translate(-50%, -50%) rotate(0deg) translateX(40px) rotate(0deg);
  }
  100% {
    transform: translate(-50%, -50%) rotate(360deg) translateX(40px) rotate(-360deg);
  }
}

.auth-form-wrapper {
  position: relative;
  z-index: 1;
}

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #0a1d2f;
  background: linear-gradient(145deg, #49c5ff, #36a3f7);
  box-shadow: 0 12px 24px rgba(54, 163, 247, 0.35);
  margin-bottom: 24px;
}

.auth-header h1 {
  font-size: 32px;
  margin-bottom: 12px;
  letter-spacing: 1.6px;
  color: #e6f1ff;
}

.auth-header p {
  font-size: 15px;
  color: rgba(214, 232, 255, 0.78);
  margin: 0;
}

.auth-form {
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

.submit-btn {
  padding: 14px 28px;
  border-radius: 999px;
  border: none;
  color: #0b2338;
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 16px 32px rgba(73, 197, 255, 0.25);
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 18px 38px rgba(73, 197, 255, 0.35);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
  color: rgba(214, 232, 255, 0.7);
}

.auth-footer .link {
  color: #49c5ff;
  margin-left: 8px;
  text-decoration: none;
  transition: color 0.3s ease;
}

.auth-footer .link:hover {
  color: #80d6ff;
  text-decoration: underline;
}
</style>

