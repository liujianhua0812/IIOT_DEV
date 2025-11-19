<template>
  <div class="module-container">
    <div id="storage-chart" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { onMounted } from 'vue';

export default {
  name: 'StorageComponent',
  setup() {
    let chartInstance;
    const nodes = ["节点1", "节点2", "节点3", "节点4", "节点5"];
    const nodeColors = [
      { used: '#980606', available: '#ed1f0a' }, // 节点1主题配色
      { used: '#2a6a4b', available: '#08ac4d' }, // 节点2主题配色
      { used: '#224485', available: '#0c90e8' }, // 节点3主题配色
      { used: '#9f4706', available: '#d17307' }, // 节点4主题配色
      { used: '#571f6e', available: '#a610e4' }  // 节点5主题配色
    ];

    const getColorGradient = (color) => {
      return new echarts.graphic.LinearGradient(0, 0, 1, 1, [
        { offset: 0, color: color },
        { offset: 1, color: echarts.color.lift(color, 0.1) }
      ]);
    };

    let chartData = nodes.map((node, index) => ({
      name: node,
      children: [
        {
          name: `${node}\n\n已使用`,
          value: Math.floor(Math.random() * 400) + 100, // 已使用 100-500 GB
          itemStyle: {
            color: getColorGradient(nodeColors[index].used)
          },
          additionalInfo: {
            cpuUsage: `${Math.floor(Math.random() * 100)}%`, // CPU使用率
            memoryUsage: `${Math.floor(Math.random() * 100)}%`, // 内存使用率
            diskIO: `${Math.floor(Math.random() * 200)} MB/s` // 磁盘IO
          }
        },
        {
          name: `${node}\n\n剩余`,
          value: Math.floor(Math.random() * 300) + 200, // 剩余 200-500 GB
          itemStyle: {
            color: getColorGradient(nodeColors[index].available)
          },
          additionalInfo: {
            cpuUsage: `${Math.floor(Math.random() * 100)}%`, // CPU使用率
            memoryUsage: `${Math.floor(Math.random() * 100)}%`, // 内存使用率
            diskIO: `${Math.floor(Math.random() * 200)} MB/s` // 磁盘IO
          }
        }
      ],
      itemStyle: {
        borderColor: 'transparent',
        borderWidth: 3,
        shadowColor: 'rgba(0, 0, 0, 0.5)',
        shadowBlur: 10,
      }
    }));

    const initChart = () => {
      const chartDom = document.getElementById('storage-chart');
      chartInstance = echarts.init(chartDom);
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const data = params.data;
            const additionalInfo = data.additionalInfo;
            const color = data.itemStyle.color.colorStops[0].color; // 从 itemStyle 中获取颜色
            return `
              <div style="background-color:${color}; padding: 10px; border-radius: 10px;">
                <strong style="color: #00ffff;font-size: 15px;font-weight: bolder">${params.name}</strong><br/>
                <strong style="color: #fff;">${data.value} GB</strong><br/>
                <span style="color: #fff">CPU使用率: ${additionalInfo.cpuUsage}</span><br/>
                <span style="color: #fff;">内存使用率: ${additionalInfo.memoryUsage}</span><br/>
                <span style="color: #fff;">磁盘IO: ${additionalInfo.diskIO}</span>
              </div>`;
          }
        },
        series: [
          {
            name: '存储容量',
            type: 'treemap',
            label: {
              show: true,
              formatter: '{b}:{c}GB',
              color: '#fff',
              fontSize: 13,
              fontWeight: 'bold'
            },
            data: chartData,
            itemStyle: {
              borderColor: 'transparent',
            },
            roam: false //不允许拖动
          }
        ]
      };

      chartInstance.setOption(option);
    };

    const updateChartData = () => {
      chartData.forEach(node => {
        node.children[0].value = Math.floor(Math.random() * 400) + 100; // 更新已使用 100-500 GB
        node.children[1].value = Math.floor(Math.random() * 300) + 200; // 更新剩余 200-500 GB

        node.children[0].additionalInfo.cpuUsage = `${Math.floor(Math.random() * 100)}%`; // 更新CPU使用率
        node.children[0].additionalInfo.memoryUsage = `${Math.floor(Math.random() * 100)}%`; // 更新内存使用率
        node.children[0].additionalInfo.diskIO = `${Math.floor(Math.random() * 200)} MB/s`; // 更新磁盘IO

        node.children[1].additionalInfo.cpuUsage = `${Math.floor(Math.random() * 100)}%`; // 更新CPU使用率
        node.children[1].additionalInfo.memoryUsage = `${Math.floor(Math.random() * 100)}%`; // 更新内存使用率
        node.children[1].additionalInfo.diskIO = `${Math.floor(Math.random() * 200)} MB/s`; // 更新磁盘IO
      });
      chartData.sort((a, b) => b.children[1].value - a.children[1].value); // 按剩余量从大到小排序
      chartInstance.setOption({
        series: [
          {
            data: chartData
          }
        ]
      });
    };

    onMounted(() => {
      initChart();
      setInterval(updateChartData, 60000); // 修改刷新间隔为60秒/一分钟
    });

    return {};
  }
};
</script>

<style scoped>
.module-container {
  top: 2vh;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.chart {
  width: 35vw;
  height: 23vh; /* 调整高度以适应新的样式 */
  position: absolute;
  margin: 20px 0;
  border-radius: 30px; /* 添加圆角效果 */
  z-index: 1;
}
</style>
