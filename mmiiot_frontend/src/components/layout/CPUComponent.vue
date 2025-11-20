<template>
  <div class="water-eval-container">
    <div class="CPU-3D-chart" id="CPU-3D-chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: "cityGreenLand",
  data() {
    return {
      optionData: [
        {
          name: '算力统计',
          value: 11727,
          itemStyle: {
            color: '#00bfff', // 柔和的蓝色
          }
        },
        {
          name: 'CPU使用统计',
          value: 12116,
          itemStyle: {
            color: '#7fff00', // 明亮的绿色
          }
        },
        {
          name: 'CPU未使用统计',
          value: 16616,
          itemStyle: {
            color: '#ff7f50', // 温暖的橙色
          }
        }
      ]
    };
  },
  mounted() {
    this.$nextTick(function() {
      this.initChart();
    });
  },
  methods: {
    initChart() {
      let chartDom = document.getElementById('CPU-3D-chart');
      let myChart = echarts.init(chartDom);

      // 传入数据生成 option
      this.option = this.getPie3D(this.optionData, 0.8);
      myChart.setOption(this.option);
      this.bindListen(myChart);
    },

    getPie3D(pieData, internalDiameterRatio) {
      // internalDiameterRatio:透明的空心占比
      let series = [];
      let sumValue = 0;
      let startValue = 0;
      let endValue = 0;
      let legendData = [];
      let legendBfb = [];
      let k = 1 - internalDiameterRatio;

      pieData.sort((a, b) => b.value - a.value);

      for (let i = 0; i < pieData.length; i++) {
        sumValue += pieData[i].value;
        let seriesItem = {
          name: pieData[i].name || `series${i}`,
          type: 'surface',
          parametric: true,
          wireframe: { show: false },
          pieData: pieData[i],
          pieStatus: { selected: false, hovered: false, k: k },
          center: ['10%', '50%']
        };


        if (pieData[i].itemStyle) {
          seriesItem.itemStyle = { ...pieData[i].itemStyle };
        }
        series.push(seriesItem);
      }

      // 使用上一次遍历时，计算出的数据和 sumValue，调用 getParametricEquation 函数，
      // 向每个 series-surface 传入不同的参数方程 series-surface.parametricEquation，也就是实现每一个扇形。
      legendData = [];
      legendBfb = [];
      for (let i = 0; i < series.length; i++) {
        endValue = startValue + series[i].pieData.value;
        series[i].pieData.startRatio = startValue / sumValue;
        series[i].pieData.endRatio = endValue / sumValue;
        series[i].parametricEquation = this.getParametricEquation(
            series[i].pieData.startRatio,
            series[i].pieData.endRatio,
            false,
            false,
            k,
            series[i].pieData.value
        );
        startValue = endValue;
        let bfb = this.fomatFloat(series[i].pieData.value / sumValue, 4);
        legendData.push({ name: series[i].name, value: bfb });
        legendBfb.push({ name: series[i].name, value: bfb });
      }

      let boxHeight = this.getHeight3D(series, 30); //通过传参设定3d饼/环的高度，26代表26px
      // 准备待返回的配置项，把准备好的 legendData、series 传入。
      let option = {
        legend: {
          data: legendData,
          orient: 'left',
          left: 10,
          itemGap: 10,
          textStyle: {
            color: '#A1E2FF',
            fontSize: 13,
          },
          show: true,
          icon: "circle",
          formatter: function(param) {
            let item = legendBfb.filter(item => item.name === param)[0];
            let bfs = this.fomatFloat(item.value * 100, 2) + "%";
            return `${item.name}  ${bfs}`;
          }.bind(this)
        },

        label: {
          show: true,
          position: 'outside',
          rich: {
            b: {
              color: '#7BC0CB',
              fontSize: 12,
              lineHeight: 20
            },
            c: {
              fontSize: 16,
            },
          },
          formatter: '{b|{b} \n}{c|{c}}{b}',
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          borderColor: '#0ff3ae',
          borderWidth: 1,
          textStyle: {
            color: '#fff'
          },
          formatter: params => {
            if (params.seriesName !== 'mouseoutSeries' && params.seriesName !== 'pie2d') {
              let bfb = ((option.series[params.seriesIndex].pieData.endRatio - option.series[params.seriesIndex].pieData.startRatio) *
                  100).toFixed(2);
              return `${params.seriesName}<br/>` +
                  `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${params.color};"></span>` +
                  `${ bfb }%`;
            }
          }
        },
        xAxis3D: { min: -1, max: 1 },
        yAxis3D: { min: -1, max: 1 },
        zAxis3D: { min: -1, max: 1 },
        grid3D: {
          show: false,
          boxHeight: boxHeight, //圆环的高度
          left: '15%',
          right: '10%',
          viewControl: { //3d效果可以放大、旋转等，请自己去查看官方配置
            alpha: 35, //角度
            distance:130,//调整视角到主体的距离，类似调整zoom
            rotateSensitivity: 1, //设置为0无法旋转
            zoomSensitivity: 1, //设置为0无法缩放
            panSensitivity: 1, //设置为0无法平移
            autoRotate: true //自动旋转
          }
        },
        series: series
      };
      return option;
    },

    getHeight3D(series, height) {
      series.sort((a, b) => {
        return (b.pieData.value - a.pieData.value);
      });
      return height * 25 / series[0].pieData.value;
    },

    getParametricEquation(startRatio, endRatio, isSelected, isHovered, k, h) {
      let midRatio = (startRatio + endRatio) / 2;
      let startRadian = startRatio * Math.PI * 2;
      let endRadian = endRatio * Math.PI * 2;
      let midRadian = midRatio * Math.PI * 2;

      if (startRatio === 0 && endRatio === 1) {
        isSelected = false;
      }

      k = typeof k !== 'undefined' ? k : 1 / 3;

      let offsetX = isSelected ? Math.cos(midRadian) * 0.1 : 0;
      let offsetY = isSelected ? Math.sin(midRadian) * 0.1 : 0;

      let hoverRate = isHovered ? 1.05 : 1;

      return {
        u: {
          min: -Math.PI,
          max: Math.PI * 3,
          step: Math.PI / 32
        },
        v: {
          min: 0,
          max: Math.PI * 2,
          step: Math.PI / 20
        },
        x: function(u, v) {
          if (u < startRadian) {
            return offsetX + Math.cos(startRadian) * (1 + Math.cos(v) * k) * hoverRate;
          }
          if (u > endRadian) {
            return offsetX + Math.cos(endRadian) * (1 + Math.cos(v) * k) * hoverRate;
          }
          return offsetX + Math.cos(u) * (1 + Math.cos(v) * k) * hoverRate;
        },
        y: function(u, v) {
          if (u < startRadian) {
            return offsetY + Math.sin(startRadian) * (1 + Math.cos(v) * k) * hoverRate;
          }
          if (u > endRadian) {
            return offsetY + Math.sin(endRadian) * (1 + Math.cos(v) * k) * hoverRate;
          }
          return offsetY + Math.sin(u) * (1 + Math.cos(v) * k) * hoverRate;
        },
        z: function(u, v) {
          if (u < -Math.PI * 0.5) {
            return Math.sin(u);
          }
          if (u > Math.PI * 2.5) {
            return Math.sin(u) * h * .1;
          }
          return Math.sin(v) > 0 ? 1 * h * .1 : -1;
        }
      };
    },

    fomatFloat(num, n) {
      var f = parseFloat(num);
      if (isNaN(f)) {
        return false;
      }
      f = Math.round(num * Math.pow(10, n)) / Math.pow(10, n);
      var s = f.toString();
      var rs = s.indexOf('.');
      if (rs < 0) {
        rs = s.length;
        s += '.';
      }
      while (s.length <= rs + n) {
        s += '0';
      }
      return s;
    },

    bindListen(myChart) {
      let selectedIndex = '';
      let hoveredIndex = '';

      myChart.on('click', params => {
        let isSelected = !this.option.series[params.seriesIndex].pieStatus.selected;
        let isHovered = this.option.series[params.seriesIndex].pieStatus.hovered;
        let k = this.option.series[params.seriesIndex].pieStatus.k;
        let startRatio = this.option.series[params.seriesIndex].pieData.startRatio;
        let endRatio = this.option.series[params.seriesIndex].pieData.endRatio;

        if (selectedIndex !== '' && selectedIndex !== params.seriesIndex) {
          this.option.series[selectedIndex].parametricEquation = this.getParametricEquation(
              this.option.series[selectedIndex].pieData.startRatio,
              this.option.series[selectedIndex].pieData.endRatio,
              false,
              false,
              k,
              this.option.series[selectedIndex].pieData.value
          );
          this.option.series[selectedIndex].pieStatus.selected = false;
        }

        this.option.series[params.seriesIndex].parametricEquation = this.getParametricEquation(
            startRatio,
            endRatio,
            isSelected,
            isHovered,
            k,
            this.option.series[params.seriesIndex].pieData.value
        );
        this.option.series[params.seriesIndex].pieStatus.selected = isSelected;

        isSelected ? selectedIndex = params.seriesIndex : null;
        myChart.setOption(this.option);
      });

      myChart.on('mouseover', params => {
        let isSelected;
        let isHovered;
        let startRatio;
        let endRatio;
        let k;

        if (hoveredIndex === params.seriesIndex) {
          return;
        } else {
          if (hoveredIndex !== '') {
            isSelected = this.option.series[hoveredIndex].pieStatus.selected;
            isHovered = false;
            startRatio = this.option.series[hoveredIndex].pieData.startRatio;
            endRatio = this.option.series[hoveredIndex].pieData.endRatio;
            k = this.option.series[hoveredIndex].pieStatus.k;
            this.option.series[hoveredIndex].parametricEquation = this.getParametricEquation(
                startRatio,
                endRatio,
                isSelected,
                isHovered,
                k,
                this.option.series[hoveredIndex].pieData.value
            );
            this.option.series[hoveredIndex].pieStatus.hovered = isHovered;
            hoveredIndex = '';
          }

          if (params.seriesName !== 'mouseoutSeries' && params.seriesName !== 'pie2d') {
            isSelected = this.option.series[params.seriesIndex].pieStatus.selected;
            isHovered = true;
            startRatio = this.option.series[params.seriesIndex].pieData.startRatio;
            endRatio = this.option.series[params.seriesIndex].pieData.endRatio;
            k = this.option.series[params.seriesIndex].pieStatus.k;
            this.option.series[params.seriesIndex].parametricEquation = this.getParametricEquation(
                startRatio,
                endRatio,
                isSelected,
                isHovered,
                k,
                this.option.series[params.seriesIndex].pieData.value + 5
            );
            this.option.series[params.seriesIndex].pieStatus.hovered = isHovered;
            hoveredIndex = params.seriesIndex;
          }
          myChart.setOption(this.option);
        }
      });

      myChart.on('globalout', () => {
        let isSelected;
        let isHovered;
        let startRatio;
        let endRatio;
        let k;

        if (hoveredIndex !== '') {
          isSelected = this.option.series[hoveredIndex].pieStatus.selected;
          isHovered = false;
          k = this.option.series[hoveredIndex].pieStatus.k;
          startRatio = this.option.series[hoveredIndex].pieData.startRatio;
          endRatio = this.option.series[hoveredIndex].pieData.endRatio;
          this.option.series[hoveredIndex].parametricEquation = this.getParametricEquation(
              startRatio,
              endRatio,
              isSelected,
              isHovered,
              k,
              this.option.series[hoveredIndex].pieData.value
          );
          this.option.series[hoveredIndex].pieStatus.hovered = isHovered;
          hoveredIndex = '';
        }
        myChart.setOption(this.option);
      });
    }
  }
};
</script>

<style scoped>
.water-eval-container {
  width: 100%;
  height: 100%;
  z-index: 1;
}

.CPU-3D-chart {
  height: 15vh;
  width: 100%;
  position: absolute;
  margin-top: 30px;
}
</style>
