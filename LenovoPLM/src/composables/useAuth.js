import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const user = ref(null)
const token = ref(localStorage.getItem('token') || null)

// 从 localStorage 恢复用户信息
const savedUser = localStorage.getItem('user')
if (savedUser) {
  try {
    user.value = JSON.parse(savedUser)
  } catch (e) {
    console.error('Failed to parse saved user:', e)
  }
}

export function useAuth() {
  const router = useRouter()

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = (userData, authToken) => {
    user.value = userData
    token.value = authToken
    localStorage.setItem('token', authToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push({ name: 'login' })
  }

  const updateUser = (userData) => {
    user.value = { ...user.value, ...userData }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    updateUser,
  }
}

