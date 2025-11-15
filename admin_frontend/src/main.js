import { createApp } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { TooltipComponent, GeoComponent, TitleComponent } from 'echarts/components'
import { EffectScatterChart } from 'echarts/charts'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './style.css'

use([CanvasRenderer, TooltipComponent, GeoComponent, TitleComponent, EffectScatterChart])

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus)

app.mount('#app')
