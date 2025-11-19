import * as echarts from 'echarts'
import 'echarts-gl'
import { createApp } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { TooltipComponent, GeoComponent, TitleComponent } from 'echarts/components'
import { EffectScatterChart } from 'echarts/charts'
import App from './App.vue'
import router from './router'
import './style.css'

use([CanvasRenderer, TooltipComponent, GeoComponent, TitleComponent, EffectScatterChart])

const app = createApp(App)

app.use(router)
app.mount('#app')
