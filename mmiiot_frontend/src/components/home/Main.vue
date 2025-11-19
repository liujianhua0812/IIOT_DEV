<template>

  <!-- 切换按钮 -->
  <button @click="toggleMapAndCloseDetail" class="button" style="top: 11vh;left: 2vw; ">
    切换到{{ isHeatMap ? '原始地图' : '热力地图' }}
  </button>
  <!-- 热力图组件 -->
  <HeatMap v-if="isHeatMap"/>

  <!-- 原始地图 -->
  <div v-show="!isHeatMap">
    <button @click="showChinaMapAndCloseDetail" v-if="MapDataIds.length > 0" class="button">
      返回上一级
    </button>
    <!--地图动态背景-->
    <!--    <div class="mapbox">-->
    <!--      <div class="map">-->
    <!--        <div class="map1"><img src="@/assets/image/lbx.png" alt="该图片不存在"></div>-->
    <!--        <div class="map2"><img src="@/assets/image/jt.png" alt="该图片不存在"></div>-->
    <!--        <div class="map3"><img src="@/assets/image/map.png" alt="该图片不存在"></div>-->
    <!--        <div class="map4" id="map_1"></div>-->
    <!--      </div>-->
    <!--    </div>-->
    <div id="ChinaMap" style="top: -10%"></div>
  </div>
  <!-- 引入模态框组件 -->
  <Modal v-if="showModal" :data="modalData" @close="closeModal" is-active/>

  <SecondPage
      v-if="showSecondPage"
      :data="selectedNode"
      :onClose="closeSecondPage"
  />
</template>
<script setup>
import {onMounted, onUnmounted, ref} from "vue";
import * as echarts from 'echarts';
import map from '../../utils/map.json'
import axios from "axios"
import allMapData from '../../assets/mapjson/china-main-city-map' // 引入中国地图扩展
import Modal from '../layout/SecondPage.vue'; // 引入模态框组件
import HeatMap from "../home/HeatMap.vue";
import {useRouter} from 'vue-router';
import SecondPage from "@/components/layout/SecondPage.vue";

const router = useRouter();


var myChart = null
const MapDataIds = ref([])
const showModal = ref(false);
const showCityDetail = ref(false);
const modalData = ref({});
const cityTitle = ref('');
const cityContent = ref('');
const selectedNode = ref(null)
const showSecondPage = ref(false)

// 地图切换控制变量
const isHeatMap = ref(false);

// 切换地图类型并关闭 CityDetail 页面
const toggleMapAndCloseDetail = () => {
  isHeatMap.value = !isHeatMap.value;
  closeCityDetail();
};

// 显示中国地图并关闭 CityDetail 页面
const showChinaMapAndCloseDetail = () => {
  closeCityDetail();
  showChinaMap();
};
// 切换地图类型
const toggleMap = () => {
  isHeatMap.value = !isHeatMap.value;
};


const openModal = (data) => {
  modalData.value = data;
  showModal.value = true;
};

function handleClick(node) {
  selectedNode.value = node
  showSecondPage.value = true
}
const closeModal = () => {
  showModal.value = false;
  showChinaMap(); // 调用showChinaMap函数
};
function goToSecondPage(node) {
  router.push({
    name: 'SecondPage',
    query: { data: JSON.stringify(node) } // ⚠️ 对象需要序列化
  })
}
const showChinaMap = (() => {
  MapDataIds.value = []
  // 销毁已有的地图实例
  if (myChart) {
    myChart.dispose();
  }
  initMap()
  drawTips()
  drawFlyLines()

})
// 框的点
const toolTipData = ref([
  {
    name: '北京泰豪',
    value: 85,
    cpuCores: 32000, // CPU核心数
    memoryCapacity: 64000, // 内存容量（单位：GB）
    storageCapacity: 5000, // 存储容量（单位：TB）
    networkBandwidth: 100, // 网络带宽（单位：Gbps）
    taskQueueLength: 50, // 任务队列长度
    averageTaskCompletionTime: 30, // 平均任务完成时间（单位：分钟）
    utilizationRate: {
      cpu: 70, // CPU利用率（%）
      memory: 65, // 内存利用率（%）
      storage: 60, // 存储利用率（%）
      network: 75// 网络带宽利用率（%）
    },
    areas: ["昌平区", "房山区", "朝阳区", "丰台区"],
    lng: 116.3912, // 北京的经度
    lat: 39.9062   // 北京的纬度
  },
  {
    name: '西北工业大学',
    value: 90,
    cpuCores: 24000,
    memoryCapacity: 48000,
    storageCapacity: 3000,
    networkBandwidth: 80,
    taskQueueLength: 40,
    averageTaskCompletionTime: 25,
    utilizationRate: {
      cpu: 75,
      memory: 70,
      storage: 65,
      network: 70
    },
    areas: ["长安区", "碑林区"],
    lng: 108.91545, // 陕西省的经度,
    lat: 34.24441   // 陕西省的纬度
  },
  {
    name: '北京邮电大学',
    value: 73,
    cpuCores: 16000,
    memoryCapacity: 32000,
    storageCapacity: 2000,
    networkBandwidth: 60,
    taskQueueLength: 30,
    averageTaskCompletionTime: 20,
    utilizationRate: {
      cpu: 80,
      memory: 75,
      storage: 70,
      network: 65
    },
    areas: ["海淀区", "昌平区"],
    lng: 116.358103,  // 北京邮电大学的经度,
    lat: 39.961554   // 北京邮电大学的纬度
  },

  {
    name: '合肥联想',
    value: 65,
    cpuCores: 28000,
    memoryCapacity: 56000,
    storageCapacity: 4500,
    networkBandwidth: 120,
    taskQueueLength: 35,
    averageTaskCompletionTime: 22,
    utilizationRate: {
      cpu: 82,
      memory: 78,
      storage: 74,
      network: 80
    },
    areas: ["合肥"],
    lng: 117.29, // 安徽省的经度
    lat: 32.0581   // 安徽省的纬度
  },

])
//各省经纬度
const geoCoordMap = ref({
  // '北京泰豪': [116.51816, 39.78621],这个是真实坐标，为了和北京邮电大学错开位置
  '北京泰豪': [113.51816, 36.78621],
  // '北京邮电大学': [116.358103, 39.961554],这个是真实坐标，为了和北京豪泰错开位置
  '北京邮电大学': [117.358103, 39.261554],
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
  '合肥联想': [117.29, 32.0581],
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
  '西北工业大学': [108.91545, 34.24441],
  '甘肃': [103.5901, 36.3043],
  '青海': [101.4038, 36.8207],
  '宁夏': [106.3586, 38.1775],
  '新疆': [87.9236, 43.5883],
  '广东': [113.12244, 23.009505],
  '广西': [108.479, 23.1152],
  '海南': [110.3893, 19.8516]
})

onMounted(() => {
  showChinaMap(); // 初始化时显示中国地图
});

onUnmounted(() => {
  // 第一步：先获取 DOM 元素，判断是否存在
  const mapDom = document.getElementById('ChinaMap');
  if (mapDom) { // 只有 DOM 存在时，才执行后续操作
    // 第二步：获取 ECharts 实例并销毁
    const mapChart = echarts.getInstanceByDom(mapDom);
    if (mapChart) {
      mapChart.dispose(); // 销毁实例，释放资源
    }
  }
});


//显示各省或各市区地图
const getProvinceMap = (MapDataId) => {
  axios.get(`/static/json/${MapDataId}.json`).then((res) => {
    echarts.registerMap(MapDataId, res.data); // 注册省级地图
    let optionraw = myChart.getOption();
    let option = {
      series: [
        ...optionraw.series.filter(
            (series) =>
                !(
                    series.name === "flylines" ||
                    series.name === "flyeffectScatter" ||
                    series.name === "flyscatter"
                )
        ),
      ]
    };
    myChart.setOption(option, true);
    initMap(MapDataId); // 初始化或更新地图

    // 取消之前的点击事件绑定，防止多次绑定
    myChart.off('click');

    myChart.on('click', (params) => {
      console.log('Clicked city:', params.name); // 输出被点击的市县名称

      if (MapDataIds.value.length === 3) {
        console.log('Routing to CityDetail with name:', params.name);  // 确认是否进入了这部分逻辑
        openCityDetail(params.name, `详细内容展示：${params.name}`);


      } else {
        // 如果还在中国地图层，点击加载省级地图
        MapDataIds.value.push(MapDataId); // 更新MapDataIds表示已经进入省级地图
        getProvinceMap(params.name); // 加载并显示省级地图
        console.log(MapDataIds.value.length)
      }
    });
  });
};


const drawFlyLines = (() => {
      // console.log('绘制飞线');
      var convertData = function (data) {
        var res = [];
        for (var i = 0; i < data.length; i++) {
          const dataItem = data[i];
          const fromCoord = geoCoordMap.value[dataItem[0].name]; // 起点坐标
          const toCoord = [109.1162, 34.2004]; // 终点坐标（固定）
          if (fromCoord && toCoord) {
            res.push({
              coords: [toCoord, fromCoord], // 核心：lines 要求的二维坐标数组（起点→终点）
              value: dataItem[0].value // 保留数值信息（如需在 tooltip 中显示）
            });
          }
        }
        return res;
      };
      var chinaDatas = [
        [{name: "北京泰豪", value: 20}],
        [{name: "西北工业大学", value: 6}],
        [{name: "合肥联想", value: 10}],
        [{name: "北京邮电大学", value: 12}],
      ];

      const series = [];
      [['西北工业大学', chinaDatas]].forEach(function (item) {
        series.push(
            {
              type: 'lines',
              name: '飞线',
              zlevel: 1,
              effect: {
                show: true,
                period: 6, // 延长动画时间, //箭头指向速度，值越小速度越快
                trailLength: 0.1, //特效尾迹长度[0,1]值越大，尾迹越长重
                symbol: 'arrow', //箭头图标
                symbolSize: 8, //图标大小
              },
              lineStyle: {
                color: '#dce30c',
                width: 1, //尾迹线条宽度
                opacity: 1, //尾迹线条透明度
                curveness: 0.3, //尾迹线条曲直度
              },
              symbol: 'arrow',
              data: convertData(item[1]),
              tooltip: {
                // 可选：显示 value 信息
                formatter: function (params) {
                  return `数值：${params.data.value}`;
                }
              }
            },
            //top5
            {
              type: 'effectScatter',
              coordinateSystem:
                  'geo',
              name:
                  '飞效散射',
              zlevel:
                  1,
              rippleEffect:
                  {
                    //涟漪特效
                    period: 4, //动画时间，值越小速度越快
                    brushType:
                        'stroke', //波纹绘制方式 stroke, fill
                    scale:
                        10, //波纹圆环最大限制，值越大波纹越大
                  }
              ,
              label: {
                show: true,
                position:
                    'right', //显示位置
                offset:
                    [5, 0], //偏移设置
                formatter:

                    function (params) {
                      //圆环显示文字
                      return params.data.name;
                    }

                ,
                fontSize: 10,
              }
              ,
              emphasis: {
                label: {
                  show: true
                }
                , // 修复：emphasis.label 平级
              }
              ,
              symbol: 'circle',
              symbolSize:

                  function (val) {
                    return 1 * (val[2] ? val[2] : 1) //圆环大小
                  }

              ,
              itemStyle: {
                show: true,
                color:
                    '#0ff3ae',
              }
              ,
              data: item[1].map(function (dataItem) {
                return {
                  name: dataItem[0].name,
                  value: geoCoordMap.value[dataItem[0].name] ? geoCoordMap.value[dataItem[0].name].concat([dataItem[0].value]) : [],
                };
              }),
            }
            ,
            //中心点
            {
              type: 'scatter', // 定义系列类型为散点图
              name:
                  '飞线起始点', // 系列名称
              coordinateSystem:
                  'geo', // 使用地理坐标系
              zlevel:
                  1, // 层级，zlevel为1表示在较低层绘制
              rippleEffect:
                  { // 涟漪效果的配置
                    period: 4, // 动画周期，值越小动画速度越快
                    brushType:
                        'stroke', // 涟漪的绘制方式，stroke表示仅绘制轮廓
                    scale:
                        4, // 涟漪的缩放比例，值越大涟漪范围越大
                  }
              ,
              label: { // 标签的配置
                show: true, // 显示标签
                position:
                    'right', // 标签位置在点的右侧
                color:
                    '#0f0', // 标签颜色为绿色
                formatter:
                    '{b}', // 标签内容为数据项名称
                fontSize:
                    12, // 补充默认字体大小（原 textStyle 中未显式配置，按常识添加）
              }
              ,
              emphasis: {
                label: {
                  show: true,
                  color:
                      "#FFA54F", // 修复：emphasis.label 平级
                }
                ,
              }
              ,
              symbol: 'pin', // 标记的形状为图钉
              symbolSize:
                  20, // 标记的大小为20
              color:
                  '#f00', // 标记的颜色为红色
              data:
                  [ // 数据数组
                    {
                      name: item[0], // 数据项名称
                      value: geoCoordMap.value[item[0]].concat([10]), // 数据项的地理坐标和值
                    },
                  ],
            }
        )
        ;
      })
      ;

      let option = {
        tooltip: {
          // 鼠标是否可以进入悬浮框
          enterable: true,
          // 触发方式 mousemove, click, none, mousemove|click
          triggerOn: 'click',
          // item 图形触发， axis 坐标轴触发， none 不触发
          trigger: 'item',
          // 浮层隐藏的延迟
          hideDelay: 800,
          // 背景色
          backgroundColor: 'rgba(0,0,0,0)',

          formatter: function (params) {
            return '<div class="chartLabel">' +
                '<div class=title>' + params.name + '</div>' +
                '</div>'
          }
        },
        legend: {
          orient: 'vertical',
          left: '10%',
          bottom: '30%',
          //legend的形状
          icon: 'roundRect',
          data: ['Top5', '飞线', '飞效散射', '飞线起始点'],
          textStyle: {
            color: '#06ffd9',
            fontFamily: 'Arial',
            fontSize: 15,
          },
        },

      }
      // 获取当前配置项
      let optionraw = myChart.getOption();
      // 追加新系列
      option.series = optionraw.series.concat(series);
      myChart.setOption(option)

    }
)
const drawTips = (() => {
  const convertData = function (data) {
    const res = [];
    for (var i = 0; i < data.length; i++) {
      const geoCoord = geoCoordMap.value[data[i].name];
      if (geoCoord) {
        res.push({
          name: data[i].name,
          value: geoCoord.concat(data[i].value),
        });
      }
    }
    return res;
  };
  let options = {
    series: [
      //柱状体的主干
      {
        type: 'lines',
        zlevel: 2,
        effect: {
          show: false,
          symbolSize: 5 // 图标大小
        },
        lineStyle: {
          width: 6, // 尾迹线条宽度
          color: 'rgba(249, 105, 13, .6)',
          opacity: 10, // 尾迹线条透明度
          curveness: 0 // 尾迹线条曲直度
        },
        label: {
          show: 0,
          position: 'end',
          formatter: '245'
        },
        silent: true,
        data: lineData().map((line) => ({coords: line.coords})),
      },
      {
        type: 'scatter',
        coordinateSystem: 'geo',
        geoIndex: 0,
        zlevel: 2,
        label: {
          show: true,
          formatter: function (params) {
            const name = params.data[2].name;
            const value = params.data[2].value;
            return `{tline|${name}} : {fline|${value}}`;
          },
          color: '#e0e0e0', // 字体颜色使用较为柔和的颜色（浅灰色），以增加和背景的对比度,，增加对比度
          rich: {
            fline: {
              color: '#05f45a',  // 数字部分的颜色设置为淡蓝色，带有科技感的柔和颜色
              fontSize: 25,
              fontFamily: 'led regular',  // 数字使用等宽字体，增加视觉效果
            },
            tline: {
              color: '#fff', // 名字部分字体颜色调整为白色
              fontSize: 18,
              fontWeight: 600,
              fontFamily: 'Arial, sans-serif', // 使用清晰的无衬线字体
              textShadow: '2px 2px 4px rgba(0, 0, 0, 0.5)' // 添加阴影效果
            },
          },
          emphasis: {
            show: true // 鼠标悬停时显示标签
          }
        },
        itemStyle: {
          // 动态设置背景色
          color: function (params) {
            const value = params.data[2].value;
            // 判断 value 大小，设置不同的颜色
            if (value >= 80) {
              return new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                {offset: 0, color: '#0e7be6'}, // 深蓝色
                {offset: 1, color: '#011249'}  // 浅蓝色
              ]);
            } else {
              return new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                {offset: 0, color: '#cf0606'}, // 深红色
                {offset: 1, color: '#870702'}  // 浅红色
              ]);
            }
          },
          opacity: 0.9, // 透明度，增加神秘感
          borderWidth: 1,  // 边框宽度
          shadowBlur: 20,  // 阴影模糊程度
          shadowColor: function (params) {
            const value = params.data[2].value;
            // 根据 value 动态设置阴影颜色
            if (value >= 85) {
              return '#0e7be6'; // 深蓝色阴影
            } else {
              return '#d30505'; // 深红色阴影
            }
          },// 阴影颜色与背景色相呼应
          shadowOffsetX: 10, // 阴影水平偏移
          shadowOffsetY: 10, // 阴影垂直偏移
        },
        symbol: 'roundRect', // 使用椭圆形状来替代矩形，增加科幻感
        // symbol: img1, // 使用椭圆形状来替代矩形，增加科幻感
        symbolSize: [170, 35], // 确保符号大小足够大，以便圆角效果显现
        symbolOffset: [20, 10], // 设置偏移位置，使其显示效果更自然
        z: 10,
        data: scatterData(),
        emphasis: {
          itemStyle: {
            color: '#069acf',  // 鼠标悬停时的颜色
          },
        }
      },

      //top5
      {
        name: 'Top5',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: convertData(toolTipData.value),
        showEffectOn: 'render',
        rippleEffect: {
          scale: 5,
          brushType: 'stroke',
        },
        label: {
          formatter: '{b}',
          position: 'bottom',
          show: false,
          color: "#fff",
          distance: 10,
        },
        symbol: 'circle',
        symbolSize: [10, 5],
        itemStyle: {
          color: '#04f835',
          shadowBlur: 10,
          opacity: 1
        },
        zlevel: 10
      },
    ]
  }
  myChart.setOption(options)

  // 柱状体的主干
  function lineData() {
    return toolTipData.value.map((item) => {
      return {
        coords: [
          geoCoordMap.value[item.name],
          [geoCoordMap.value[item.name][0], geoCoordMap.value[item.name][1] + 1.5]]
      }
    })
  }

  // 柱状体的顶部
  function scatterData() {
    return toolTipData.value.map((item) => {
      return [geoCoordMap.value[item.name][0], geoCoordMap.value[item.name][1] + 2, item]
    })
  }

  myChart.on('click', (params) => {
    // 如果点击的是 effectScatter 类型，则只处理模态框，不进行地图跳转
    if (params.componentType === 'series' && params.seriesType === 'effectScatter') {
      const clickedData = toolTipData.value.find((d) => d.name === params.name);
      if (clickedData) {
        openModal(clickedData);
        showChinaMap();
      }
      return; // 阻止后续的地图跳转处理
    }

    // 如果点击的是 scatter 类型，则调用 showChinaMap
    if (params.componentType === 'series' && params.seriesType === 'scatter') {
      openModal(params.data[2])
      showChinaMap();
      return;
    }

    // 处理地图的点击事件
    if (params.componentType === 'geo' || (params.seriesType === 'map')) {
      const MapDataId = allMapData[params.name];
      if (MapDataId) {
        MapDataIds.value.push(MapDataId);
        getProvinceMap(MapDataId);
      }
    }
  });

})
// 初始化地图
const initMap = ((place) => {
  const mapName = 'china';
  const data = [
    {name: '北京', value: 5},
    {name: '天津', value: 14},
    {name: '河北', value: 157},
    {name: '山西', value: 110},
    {name: '内蒙古', value: 40},
    {name: '辽宁', value: 40},
    {name: '吉林', value: 40},
    {name: '黑龙江', value: 60},
    {name: '上海', value: 10},
    {name: '江苏', value: 60},
    {name: '浙江', value: 50},
    {name: '安徽', value: 151},
    {name: '福建', value: 60},
    {name: '江西', value: 74},
    {name: '山东', value: 200},
    {name: '河南', value: 100},
    {name: '湖北', value: 40},
    {name: '湖南', value: 50},
    {name: '重庆', value: 40},
    {name: '四川', value: 120},
    {name: '贵州', value: 135},
    {name: '云南', value: 90},
    {name: '西藏', value: 25},
    {name: '陕西', value: 100},
    {name: '甘肃', value: 60},
    {name: '青海', value: 20},
    {name: '宁夏', value: 110},
    {name: '新疆', value: 32},
    {name: '广东', value: 10},
    {name: '广西', value: 100},
    {name: '海南', value: 40},
  ];

  /*获取地图数据*/
  echarts.registerMap("china", {geoJSON: map});

  const mapFeatures = map.features
  mapFeatures.forEach(function (v) {
    // 地区名称
    const name = v.properties.name;
    // 地区经纬度
    geoCoordMap.value[name] = v.properties.cp;
  });


  let option = {
    tooltip: {
      trigger: 'none',
      backgroundColor: "#1263a5",
      borderColor: "#1b62a7",
      padding: [5, 10],
      textStyle: {
        color: "#fff",
        fontSize: "16",
        fontFamily: "华文楷体",
        fontWeight: 550,
      }
    },
    geo: [
      {
        layoutCenter: ['50%', '60%'],//位置
        // layoutSize: '120%',//大小
        show: true,
        map: place ? place : mapName,
        roam: false,
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
              color: '#fff'
            }
          }
        },
        regions: [
          {
            name: "南海诸岛",
            itemStyle: {
              // 隐藏地图
              opacity: 1, // 为 0 时不绘制该图形
            },
            label: {
              show: true, // 隐藏文字
            }
          }
        ],
        itemStyle: {
          areaColor: {
            type: "linear",
            x: 1200,
            y: 0,
            x2: 0,
            y2: 0,
            colorStops: [{
              offset: 0,
              color: "rgba(3,27,78,0.75)", // 0% 处的颜色
            }, {
              offset: 1,
              color: "rgba(58,149,253,0.75)", // 50% 处的颜色
            },],
            global: true, // 缺省为 false
          },
          borderColor: "#c0f3fb",
          borderWidth: 1,
          shadowColor: "#32b5e8",
          shadowOffsetY: 10,
          shadowBlur: 120,
        },
        emphasis: {
          areaColor: "rgba(0,254,233,0.6)",
          // borderWidth: 0
        }
      },

      //地图外边的边界线
      {
        type: "map",
        map: place ? place : mapName,
        zlevel: -1,
        aspectScale: 1,
        zoom: 1.2,
        layoutCenter: ['50%', '60%'],//位置
        // layoutSize: "180%",
        roam: false,
        silent: true,
        itemStyle: {
          borderWidth: 3,
          // borderColor:"rgba(17, 149, 216,0.6)",
          borderColor: "rgba(58,149,253,0.8)",
          shadowColor: "rgba(2,248,212,0.5)",
          shadowOffsetY: 5,
          shadowBlur: 15,
          areaColor: "rgba(5,21,35,0.1)",
        },
        regions: [
          {
            name: "南海诸岛",
            itemStyle: {
              // 隐藏地图
              opacity: 0, // 为 0 时不绘制该图形
            },
            label: {
              show: false // 隐藏文字
            }
          }
        ],
      },
      //     下面的阴影
      {
        type: "map",
        map: place ? place : mapName,
        zlevel: -2,
        aspectScale: 1,
        zoom: 1.2,
        layoutCenter: ['50%', '52%'],//位置
        layoutSize: "100%",
        roam: false,
        silent: true,
        itemStyle: {
          borderWidth: 1,
          // borderColor: "rgba(57, 132, 188,0.4)",
          borderColor: "rgba(58,149,253,0.6)",
          shadowColor: "rgba(65, 214, 255,1)",
          shadowOffsetY: 10,
          shadowBlur: 20,
          areaColor: "transpercent",
        },
        regions: [
          {
            name: "南海诸岛",
            itemStyle: {
              // 隐藏地图
              opacity: 1, // 为 0 时不绘制该图形
            },
            label: {
              show: false // 隐藏文字
            }
          }
        ],
      },

    ],
    series: [
      {
        type: 'map',
        map: place ? place : mapName,
        geoIndex: 0,
        aspectScale: 1,//长宽比
        zoom: 0.75,
        showLegendSymbol: true,
        roam: true,
        label: {
          show: true,
          textStyle: {
            color: "#fff",
            fontSize: 15
          },
        },
        itemStyle: {
          areaColor: {
            type: "linear",
            x: 1200,
            y: 0,
            x2: 0,
            y2: 0,
            colorStops: [{
              offset: 0,
              color: "rgba(3,27,78,0.75)", // 0% 处的颜色
            }, {
              offset: 1,
              color: "rgba(58,149,253,0.75)", // 50% 处的颜色
            },],
            global: true, // 缺省为 false
          },
          borderColor: "#fff",
          borderWidth: 0.2,
        },
        layoutCenter: ["50%", "10%"],
        layoutSize: "180%",
        animation: false,
        markPoint: {
          symbol: "none"
        },
        data: data,
      },
    ],
  };


  myChart = echarts.init(document.getElementById('ChinaMap'));
  myChart.setOption(option)

  myChart.off("click");
  // 绑定点击事件 获取对应省json 加载地图
  myChart.on('click', (params) => {
    const MapDataId = allMapData[params.name];
    MapDataIds.value.push(MapDataId)
    if (MapDataId) {
      MapDataIds.value.push(MapDataId);
      // 获取当前配置项
      getProvinceMap(MapDataId)
    }
  });

  //打开二级页面
  myChart.on('click', 'series.effectScatter', function (params) {
    openModal(params.data);
  });
})

</script>

<style scoped>
#ChinaMap {
  width: 100%;
  height: 80vh;
}


.button {
  position: relative;
  display: inline-block;
  padding: 10px 20px;
  color: #fff;
  left: 1vw;
  font-size: 14px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1.8px;
  background: linear-gradient(135deg, #002f4b, #005f99, #0096d6);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s ease;
  box-shadow: 0 0 15px rgba(0, 191, 255, 0.5), 0 0 30px rgba(0, 191, 255, 0.5), 0 0 45px rgba(0, 191, 255, 0.5),
  5px 5px 15px rgba(0, 0, 0, 0.3), -5px -5px 15px rgba(255, 255, 255, 0.1);
  transform: perspective(800px) rotateX(15deg) rotateY(15deg);
  z-index: 1;
}

.button::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  width: 300%;
  height: 300%;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.5s ease;
  border-radius: 50%;
  z-index: 0;
  transform: translate(-50%, -50%) scale(0.1);
}

.button:hover::before {
  transform: translate(-50%, -50%) scale(1);
}

.button::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(2, 255, 247, 0.3);
  border-radius: 6px;
  pointer-events: none;
  transition: opacity 0.3s ease;
  opacity: 0;
}

.button:hover::after {
  opacity: 1;
}

.button:hover {
  box-shadow: 0 0 20px rgba(0, 191, 255, 0.6), 0 0 40px rgba(0, 191, 255, 0.6), 0 0 60px rgba(0, 191, 255, 0.6),
  5px 5px 20px rgba(0, 0, 0, 0.4), -5px -5px 20px rgba(255, 255, 255, 0.15);
}

.button:active {
  background: linear-gradient(135deg, #003366, #004f80, #006699);
}

.button:focus {
  outline: none;
}

.button::after {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 15px rgba(0, 191, 255, 0.5), 0 0 30px rgba(0, 191, 255, 0.5), 0 0 45px rgba(0, 191, 255, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 191, 255, 0.6), 0 0 40px rgba(0, 191, 255, 0.6), 0 0 60px rgba(0, 191, 255, 0.6);
  }
  100% {
    box-shadow: 0 0 15px rgba(0, 191, 255, 0.5), 0 0 30px rgba(0, 191, 255, 0.5), 0 0 45px rgba(0, 191, 255, 0.5);
  }
}

/* 返回按钮样式 */
.back-button {
  width: 15%;
  left: 1%;
  display: flex;
  justify-content: center;
  position: absolute;
  top: 20vh;
  padding: 10px 10px;
  font-size: 18px;
  color: #08f5d1;
  background: linear-gradient(45deg, #1b2c3e, #085d80); /* 渐变背景 */
  border: 1px solid #00b3ff;
  border-radius: 10px;
  cursor: pointer;
  z-index: 10;
  box-shadow: 0 0 10px rgba(0, 179, 255, 0.7), 0 0 20px rgba(0, 179, 255, 0.5);
  transition: background 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
}

/* 按钮悬停时的效果 */
.back-button:hover {
  background: linear-gradient(45deg, #00b3ff, #004080);
  box-shadow: 0 0 20px rgba(0, 179, 255, 1), 0 0 30px rgba(0, 179, 255, 0.7);
  transform: translateY(-3px);
}

/* 背景光流动效果 */
.back-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(0, 179, 255, 0.5), transparent);
  transform: rotate(45deg);
  transition: all 0.5s ease;
  z-index: 0;
}

/* 鼠标悬停时触发流光效果 */
.back-button:hover::before {
  top: -30%;
  left: -30%;
  background: radial-gradient(circle, rgba(0, 255, 255, 0.8), transparent);
}

/* 文字的发光效果 */
.back-button::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  background: linear-gradient(90deg, rgba(0, 179, 255, 0.2), transparent);
  opacity: 0;
  transition: opacity 0.5s ease, transform 0.5s ease;
  z-index: -1;
}

.back-button:hover::after {
  opacity: 1;
  transform: translateX(200%);
}

</style>

