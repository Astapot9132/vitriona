import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { setupApi } from './lib/api-setup'
import router from './router'
import './styles.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
setupApi(pinia)

app.use(router)
app.mount('#app')
