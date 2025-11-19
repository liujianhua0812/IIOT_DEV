<template>
  <div id="BarsChart" style="width: 100%; height: 200px"></div>
</template>

<script setup>
import {onMounted, ref} from "vue";
import * as echarts from 'echarts';

let dataZoomMove = {
  start: 0,
  end: 4
}

const Chart = ref(null)
let dataZoomMoveTimer = null
let xdata = ["西北工业大学-友谊校区", "北京邮电大学", "东南大学", "中国科学技术大学", "清华大学", "西安工程大学", "联宝电子科技有限公司", "西北工业大学-长安校区"];
let sdata = [314, 129, 190, 181, 364, 152, 157, 267];
let sdata1 = [{symbolPosition: "end", value: 700}, {symbolPosition: "end", value: 700}, {
  symbolPosition: "end",
  value: 700
}, {symbolPosition: "end", value: 700}, {symbolPosition: "end", value: 700}, {
  symbolPosition: "end",
  value: 700
}, {symbolPosition: "end", value: 700}, {symbolPosition: "end", value: 700}];

// 基于准备好的dom，初始化echarts实例
onMounted(() => {
  Chart.value = echarts.init(document.getElementById('BarsChart'))
  let ranking1 =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAWCAYAAAA4oUfxAAAAAXNSR0IArs4c6QAAAH1JREFUSEvtlrENAlEMQ1/+v2sQEjtQsQw7sB+zsAgdFRLEDjqYgD6FlXSRosR+kefThQp/NWwchhBY1BBRWWXB1jsXZm6VdLJM4XpTU4TypzUZSlhFvcTcJX6K2ot8iPvBHG/miqOH99r74PrV2mTaXjtYOlIbJhqj/gHID8qzPmJQqvq2AAAAAElFTkSuQmCC";
  let ranking2 =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAWCAYAAAA4oUfxAAAAAXNSR0IArs4c6QAAAHRJREFUSEvtlsEJw1AMQ59/SQuZsgtksgzXnkpDbP3wky7QuzBCBxsMxpYVfZmeNAQhQHSEKOKHXklEMeJG0kk0OPKqif1kRZ6YRr4l30/RKGaSO8Wb4kGxIV6IFYWbe+xeOJ8aFhnLqx+LX6rNhG3UHwbyAFH8IFOor3h3AAAAAElFTkSuQmCC";
  let ranking3 =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAWCAYAAAA4oUfxAAAAAXNSR0IArs4c6QAAAHhJREFUSEvtlrENAlEMQ58/FFdSsRk927IFA1DRoJMgzqF/TEDvInIURYoUJba13ZYrg2ajkX7YGM2wkQpjBgYVoijVns/aVp8dZ9971ik0iqPMOszpULyeZsE8MGeaO82FVoZn7Tm4vFpIJvQaYYmkxkzERv1jIL8upfQu1X2WdQAAAABJRU5ErkJggg==";
  let ranking4 =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAWCAYAAAA4oUfxAAAAAXNSR0IArs4c6QAAAHlJREFUSEvtlrsNAkEMRJ93uYAMiruc+miLGhAB9hjdInIKmMAa2Ykly/OJ7f66ESiEDkQtoL7VFWPmr4/uTJHMzlCveYzTe6E6o0i2zlHK6K4nKs6VjEsxKCbFA3FF7Ci83Gf3w5lqFpkloZZXG4st1WHCMerPAPkBU7a6PWEESkIAAAAASUVORK5CYII=";
  let dataZoomMove = {
    start: 0,
    end: 4
  };


  let option = {
    //你的代码
    tooltip: {
      show: false,
      trigger: "axis"
    },
    dataZoom: [
      {
        show: false, // 为true 滚动条出现
        startValue: dataZoomMove.start,
        endValue: dataZoomMove.end,
        yAxisIndex: [0, 1], //关联多个y轴
      },
      {
        //没有下面这块的话，只能拖动滚动条，鼠标滚轮在区域内不能控制外部滚动条
        type: "inside",
        yAxisIndex: 0,
        zoomOnMouseWheel: false, //滚轮是否触发缩放
        moveOnMouseMove: true, //鼠标滚轮触发滚动
        moveOnMouseWheel: true,
      },
    ],
    grid: {
      containLabel: true,
      bottom: "5%",
      left: "0%",
      top: "5%",
      right: "1%",
    },
    xAxis: {
      type: "value",
      axisLabel: {
        show: false
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        show: false
      }
    },
    yAxis: [
      {
        type: "category",
        data: xdata,
        inverse: true,
        axisLabel: {
          fontSize: "18px",
          inside: false,
          verticalAlign: "center",

          padding: [5, 0, 0, 0],
          margin: 20, //刻度标签与轴线之间的距离
          formatter: function (value, index) {
            // console.log("formatterformatter", value, index);
            if (index < 3) {
              return `{img${index}|${xdata.indexOf(value) + 1
              }} {a|${value}}`;
            } else {
              return `{img3|${xdata.indexOf(value) + 1}} {a|${value}}`;
            }
          },
          rich: {
            a: {
              fontSize: "14px",
              color: "#00DEFF",
              padding: [0, -10, 0, 25],
              width: 110
            },
            b: {
              fontSize: "18px",
              color: "#8891B0",
              padding: [4, 15, 0, 15]
            },
            img0: {
              width: 26,
              height: 22,
              color: "#FF2E05",
              fontSize: "18px",

              align: "center",
              fontWeight: 400,
              padding: [3, 10, 0, 0],
              verticalAlign: "middle",
              backgroundColor: {
                image: ranking1
              }
            },
            img1: {
              width: 26,
              height: 22,
              color: "#FE6E07",
              fontSize: "18px",
              align: "center",
              fontWeight: 400,
              padding: [3, 10, 0, 0],
              verticalAlign: "middle",
              backgroundColor: {
                image: ranking2
              }
            },
            img2: {
              width: 26,
              height: 22,
              color: "#FFD648",
              fontSize: "18px",
              align: "center",
              fontWeight: 400,
              padding: [3, 10, 0, 0],
              verticalAlign: "middle",
              backgroundColor: {
                image: ranking3
              }
            },
            img3: {
              width: 26,
              height: 22,
              color: "#06CDF7",
              fontSize: "18px",
              align: "center",
              fontWeight: 400,
              padding: [3, 10, 0, 0],
              verticalAlign: "middle",
              backgroundColor: {
                image: ranking4
              }
            }
          }
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        splitLine: {
          show: false,
          lineStyle: {
            color: "#13387a"
          }
        }
      },

      {
        type: "category",
        data: xdata,
        inverse: true,
        padding: [0, 0, 0, 0],
        axisLabel: {
          inside: false,
          verticalAlign: "center",
          padding: [0, 0, 0, 0],
          margin: 10, //刻度标签与轴线之间的距离
          formatter: function (value, index) {
            return `{a|${sdata[xdata.indexOf(value)]}}`;
          },
          rich: {
            a: {
              fontSize: 23,
              fontFamily: "DS-Digital",
              color: "#00DEFF",
              padding: [4, 0, 0, 5]
            }
          }
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        splitLine: {
          show: false,
          lineStyle: {
            color: "#13387a"
          }
        }
      }
    ],
    series: [
      {
        data: sdata,
        type: "bar",
        barWidth: 6,
        borderRadius: 50,
        showBackground: true,
        verticalAlign: "center",
        zlevel: 10,
        color: {
          type: "linear",
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            {
              offset: 0,
              color: "rgba(44, 205, 223,1)" // 0% 处的颜色
            },
            // {
            //   offset: 0.2,
            //   color: "rgba(1,249,266, 0.5)" // 0% 处的颜色
            // },
            {
              offset: 1,
              color: "rgba(3,248,240, 0.6)" // 100% 处的颜色
            }
          ]
        },

        itemStyle: {
          verticalAlign: "center",
          zlevel: 10,
          borderRadius: 40,
          borderWidth: 0,
        },
        emphasis: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              {
                offset: 0,
                color: "rgba(255, 68, 0, 1)" // 0% 处的颜色
              },
              {
                offset: 1,
                color: "rgba(223, 45, 44, 1)" // 100% 处的颜色
              }
            ]
          }
        }
      },

      {
        type: "pictorialBar",
        // symbol: "react",
        symbolSize: [0, 0],
        symbolOffset: [3, 0],
        zlevel: 12,
        itemStyle: {
          color: "#fff",
          borderRadius: 3,
          shadowColor: "#006BFF",
          shadowBlur: 10
        },
        data: sdata1
      }
    ]
  };
  Chart.value.setOption(option)
  startMoveDataZoom()

})
//滚动方法实现
const startMoveDataZoom = () => {
  dataZoomMoveTimer = setInterval(() => {
    dataZoomMove.start += 1;
    dataZoomMove.end += 1;
    if (dataZoomMove.end > sdata.length - 1) {
      dataZoomMove.start = 0;
      dataZoomMove.end = 4;
    }
    Chart.value.setOption({
      dataZoom: [
        {
          type: "slider", // 有type这个属性，滚动条在最下面，也可以不行，写y：36，这表示距离顶端36px，一般就是在图上面。
          startValue: dataZoomMove.start,
          endValue: dataZoomMove.end,
        },
      ],
    });
  }, 2000);
  //设置滚动速度
};

</script>

<style scoped>
#BarsChart {
  background: linear-gradient(145deg, rgba(0, 0, 30, 0.9), rgba(0, 50, 100, 0.8));
  border: 2px solid #00f7ff;
  border-radius: 15px;
  box-shadow: 0 0 20px rgba(33, 239, 239, 0.5), inset 0 0 10px rgba(10, 213, 213, 0.3);
  position: relative;
  overflow: hidden;
  animation: glowing 2s infinite;
}

@keyframes glowing {
  0% {
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), 0 0 20px rgba(0, 255, 204, 0.3);
  }
  50% {
    box-shadow: 0 0 30px rgba(0, 234, 255, 0.7), 0 0 30px rgba(39, 198, 198, 0.5);
  }
  100% {
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), 0 0 20px rgba(0, 255, 204, 0.3);
  }
}
</style>
