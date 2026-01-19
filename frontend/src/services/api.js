import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5분 (대용량 파일 업로드 고려)
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

