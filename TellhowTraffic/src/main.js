import { createApp } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { TooltipComponent, GeoComponent, TitleComponent, GridComponent, LegendComponent } from 'echarts/components'
import { EffectScatterChart, LineChart, BarChart } from 'echarts/charts'
import App from './App.vue'
import router from './router'
import './style.css'

use([
  CanvasRenderer,
  TooltipComponent,
  GeoComponent,
  TitleComponent,
  GridComponent,
  LegendComponent,
  EffectScatterChart,
  LineChart,
  BarChart
])

const app = createApp(App)

app.use(router)

app.mount('#app')
