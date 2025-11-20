<template>
  <!--地图动态背景-->
  <div class="mapbox">
  </div>
  <div id="HeatMap" style="width: 100%; height: 80vh;"></div>
</template>

<script setup>
import {onMounted} from "vue";
import * as echarts from "echarts";

const geoCoordMap = {
  '北京': [116.4551, 40.2539],
  '天津': [117.4219, 39.4189],
  '河北': [114.4995, 38.1006],
  '山西': [112.3352, 37.9413],
  '内蒙古': [110.3467, 41.4899],
  '辽宁': [123.1238, 42.1216],
  '吉林': [125.8154, 44.2584],
  '黑龙江': [127.9688, 45.368],
  '上海': [121.4648, 31.2891],
  '江苏': [118.8062, 31.9208],
  '浙江': [119.5313, 29.8773],
  '安徽': [117.29, 32.0581],
  '福建': [119.4543, 25.9222],
  '江西': [116.0046, 28.6633],
  '山东': [117.1582, 36.8701],
  '河南': [113.4668, 34.6234],
  '湖北': [114.3896, 30.6628],
  '湖南': [113.0823, 28.2568],
  '重庆': [108.384366, 30.439702],
  '四川': [103.9526, 30.7617],
  '贵州': [106.6992, 26.7682],
  '云南': [102.9199, 25.4663],
  '西藏': [91.11, 29.97],
  '陕西': [109.1162, 34.2004],
  '甘肃': [103.5901, 36.3043],
  '青海': [101.4038, 36.8207],
  '宁夏': [106.3586, 38.1775],
  '新疆': [87.9236, 43.5883],
  '广东': [113.12244, 23.009505],
  '广西': [108.479, 23.1152],
  '海南': [110.3893, 19.8516]
};

const heatmapData = [
  {
    name: '北京',
    totalPower: 251,
    utilization: 85,
    taskCount: 15612,
    efficiency: 75,
    growthRate: 5
  },
  {
    name: '江苏',
    totalPower: 286,
    utilization: 88,
    taskCount: 14106,
    efficiency: 78,
    growthRate: 6
  },
  {
    name: '广东',
    totalPower: 217,
    utilization: 82,
    taskCount: 13532,
    efficiency: 73,
    growthRate: 4
  },
  {
    name: '陕西',
    totalPower: 212,
    utilization: 129,
    taskCount: 11232,
    efficiency: 62,
    growthRate: 6
  },
];

onMounted(() => {
  const chart = echarts.init(document.getElementById("HeatMap"));

  const convertData = (data) => {
    const res = [];
    for (let i = 0; i < data.length; i++) {
      const fromCoord = geoCoordMap[data[i].name];
      for (let j = i + 1; j < data.length; j++) {
        const toCoord = geoCoordMap[data[j].name];
        if (fromCoord && toCoord) {
          res.push({
            fromName: data[i].name,
            toName: data[j].name,
            coords: [fromCoord, toCoord],
          });
        }
      }
    }
    return res;
  };

  const option = {
    visualMap: {
      min: 0,
      max: 250,
      left: '10%',
      bottom: '30%',
      text: ['高', '低'],
      textStyle: {
        color: '#fff',
        fontSize: 17
      },
      calculable: true,
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      }
    },
    geo: [
      {
        map: 'china',
        layoutCenter: ['50%', '60%'],
        zoom: 1.2,
        aspectScale: 1,
        itemStyle: {
          areaColor: "rgb(5,201,234)",
          shadowColor: "rgba(0, 255, 233, 0.6)",
          shadowBlur: 50,
          shadowOffsetX: 0,
          shadowOffsetY: 0,
        },
        emphasis: {
          areaColor: "rgba(0, 254, 233, 0.8)",
          shadowColor: "rgba(255, 255, 0, 1)",
          shadowBlur: 60,
          shadowOffsetX: 0,
          shadowOffsetY: 0,
          borderColor: '#fff',
          borderWidth: 4
        }
      },
      {
        map: 'china',
        layoutCenter: ['50%', '60%'],
        zoom: 1.2,
        aspectScale: 1,
        label: {
          show: true,
          textStyle: {
            color: '#fff',
            fontSize: 15,
            fontFamily: "华文楷体",
          },
          emphasis: {
            show: true,
            textStyle: {
              color: '#dae60d',
              fontWeight: 'bold'
            }
          }
        },
        itemStyle: {
          areaColor: {
            type: "linear-gradient",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {offset: 0, color: "#155168"},
              {offset: 1, color: "#094f6e"}
            ],
            global: true,
          },
          borderColor: "#0ae4a3",
          borderWidth: 1.5,
          shadowColor: "rgba(0, 0, 0, 0.5)",
          shadowOffsetX: 0,
          shadowOffsetY: 15,
          shadowBlur: 20,
          emphasis: {
            areaColor: "rgba(0, 254, 233, 0.6)",
          }
        }
      },
      {
        map: 'china',
        layoutCenter: ['50%', '55%'],
        zoom: 1.2,
        zlevel: -1,
        roam: false,
        aspectScale: 1,
        silent: true,
        itemStyle: {
          borderWidth: 1,
          // borderColor: "rgba(57, 132, 188,0.4)",
          borderColor: "rgba(58,149,253,0.6)",
          shadowColor: "rgba(0, 254, 233, 0.6)",
          shadowOffsetY: 10,
          shadowBlur: 20,
          areaColor: "transpercent",
        },
        label: {
          show: true,
          textStyle: {
            color: '#fff',
            fontSize: 15,
            fontFamily: "华文楷体",
          },
          emphasis: {
            show: true,
            textStyle: {
              color: '#dae60d',
              fontWeight: 'bold'
            }
          }
        },

      }
    ],
    series: [
      {
        name: '算力总量',
        type: 'heatmap',
        zlevel: 10,
        coordinateSystem: 'geo',
        geoIndex: 1,
        data: heatmapData.map(item => ({
          name: item.name,
          value: [...geoCoordMap[item.name], item.totalPower]
        })),
        pointSize: 25,
        blurSize: 15,
        itemStyle: {
          borderColor: "rgba(244,231,6,0.13)",
          borderWidth: 2,
          shadowColor: 'rgba(255, 255, 255, 0.8)',
          shadowBlur: 20,
          shadowOffsetX: 0,
          shadowOffsetY: 0
        },
      },
      {
        name: '算力调度连接线',
        type: 'lines',
        zlevel: 20,
        coordinateSystem: 'geo',
        effect: {
          show: true,
          period: 3,
          trailLength: 0.7,
          color: '#f4e705',
          symbol: 'arrow',
          symbolSize: 5,
          shadowBlur: 7,
          shadowColor: 'rgba(255, 255, 0, 0.8)'
        },
        lineStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            {offset: 0, color: '#00c0ff'},
            {offset: 1, color: '#f4e705'}
          ]),
          width: 3,
          opacity: 0.9,
          curveness: 0.15,
          shadowBlur: 20,
          shadowColor: 'rgba(0, 176, 255, 0.7)'
        },
        data: convertData(heatmapData)
      }
    ],
    graphic: []
  };

  chart.setOption(option);

  let currentIndex = 0;

  const autoHighlight = () => {
    const dataLen = heatmapData.length;

    // 移除之前的图形元素
    chart.setOption({
      graphic: []
    });

    currentIndex = (currentIndex + 1) % dataLen;
    const provinceData = heatmapData[currentIndex];

    // 添加新的图形元素，用于显示信息框，固定在地图的右上角
    chart.setOption({
      graphic: {
        type: 'group',
        left: '80%', // 固定在地图右上角
        top: '25%',
        children: [
          {
            type: 'rect',
            left: 'center',
            top: 'middle',
            z: 90, // 在文字下方
            shape: {
              width: 180,
              height: 200,
              r: 15 // 圆角矩形
            },
            style: {
              fill: 'rgba(25, 28, 41, 0.8)', // 使用深色半透明背景
              stroke: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 1,
                y2: 1,
                colorStops: [
                  {offset: 0, color: '#00ffcc'},
                  {offset: 0.5, color: '#7e02fd'},
                  {offset: 1, color: '#00309a'}
                ]
              }, // 动态霓虹灯边框
              lineWidth: 4, // 边框宽度
              shadowBlur: 50, // 增加阴影模糊效果
              shadowColor: '#00ffcc', // 阴影颜色与边框颜色一致
              shadowOffsetX: 0,
              shadowOffsetY: 0
            }
          },
          {
            type: 'rect',
            left: 'center',
            top: 'middle',
            z: 80, // 在背景下方制造模糊效果
            shape: {
              width: 190,
              height: 210,
              r: 15 // 圆角矩形
            },
            style: {
              fill: 'rgba(0, 255, 204, 0.5)', // 边框颜色的半透明
              shadowBlur: 40, // 更大的阴影模糊效果
              shadowColor: '#00ffcc', // 更浓的霓虹灯颜色
              shadowOffsetX: 0,
              shadowOffsetY: 0,
              filter: 'blur(10px)', // 模糊效果
              opacity: 0.7
            }
          },
          {
            type: 'text',
            left: 'center',
            top: 'middle',
            z: 100,
            style: {
              text: `
{header|${provinceData.name}—调度中心}\n\n
{body|总算力: }{value|${provinceData.totalPower}}\n
{body|利用率: }{value|${provinceData.utilization}%}\n
{body|任务量: }{value|${provinceData.taskCount}}\n
{body|能效比: }{value|${provinceData.efficiency}}\n
{body|增长率: }{value|${provinceData.growthRate}%}
    `,
              fill: '#00ffcc', // 霓虹灯文字颜色
              font: '18px Microsoft YaHei', // 基础字体
              lineHeight: 5, // 行高
              textAlign: 'center', // 左对齐
              rich: {
                header: {
                  fontSize: 18,
                  color: '#00ffcc', // 标题颜色
                  fontWeight: 'bold', // 标题加粗
                  lineHeight: 12,
                  align: 'center',
                  textShadowColor: '#00ffcc'
                },
                body: {
                  fontSize: 18,
                  color: '#00ffcc', // 标签文字颜色
                  lineHeight: 5,
                  align: 'center'
                },
                value: {
                  fontSize: 18,
                  color: '#ffffff', // 数值部分的颜色为白色
                  fontWeight: 'bold', // 数值部分加粗
                  lineHeight: 25,
                  align: 'left'
                }
              }
            }
          },
        ]
      }
    });

    // 模拟高亮当前的节点
    chart.dispatchAction({
      type: 'highlight',
      seriesIndex: 0,
      dataIndex: currentIndex
    });
  };

  // 一开始立即显示第一个信息框
  autoHighlight();

  // 设置定时器，每隔几秒轮播显示一个节点的数据
  setInterval(autoHighlight, 3000); // 3秒轮播一次

});
</script>

<style scoped>
#HeatMap {
  width: 100%;
  height: 80vh;
}
</style>
