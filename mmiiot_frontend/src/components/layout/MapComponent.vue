<template>
  <div id="amap-container" class="amap-container"></div>
</template>

<script setup>
import {onMounted } from 'vue';

const props = defineProps({
  lng: {
    type: Number,
    required: true
  },
  lat: {
    type: Number,
    required: true
  }
});

const createFlyLines = (map, startPosition) => {
  const otherPositions = [
    { name: '北京泰豪', position: [116.51816, 39.78621], intensity: 0.8 },
    { name: '北京邮电大学', position: [116.358103, 39.961554], intensity: 0.6 },
    { name: '合肥联想', position: [117.29, 32.0581], intensity: 0.7 },
    { name: '西北工业大学', position: [108.91545, 34.24441], intensity: 0.9 }
  ];

  otherPositions.forEach((target) => {
    const path = [startPosition, target.position];

    // 线条颜色渐变
    const strokeColor = `rgba(245, 253, 2, ${target.intensity})`;


    const polyline = new AMap.Polyline({
      path: path,
      strokeColor: strokeColor, // 使用动态强度设置颜色透明度
      strokeWeight: target.intensity * 8, // 根据强度调整线条粗细
      showDir: true, // 显示方向
      lineJoin: 'round'
    });
    map.add(polyline);

    const startMarker = new AMap.Marker({
      position: startPosition,
    });


    const endMarker = new AMap.Marker({
      position: target.position,
      label: {
        content: `<div style="color: #f5fd02; font-size: 14px; background-color: #23103b; padding: 2px 5px; border-radius: 4px;">${target.name}</div>`,
        offset: new AMap.Pixel(20, 20)
      }
    });
    map.add(startMarker);
    map.add(endMarker);

    const movingMarker = new AMap.Marker({
      map: map,
      position: startPosition,
      offset: new AMap.Pixel(-13, -26),
      autoRotation: true
    });

    // 添加飞线动态效果
    movingMarker.moveAlong(path, {
      duration: 10000,
      autoRotation: true,
      easing: (t) => t * t * t // 加速飞行效果
    });
  });
};

onMounted(() => {
  if (props.lng !== undefined && props.lat !== undefined) {
    const map = new AMap.Map('amap-container', {
      center: [props.lng, props.lat],
      zoom: 12,
      mapStyle: 'amap://styles/darkblue',
      viewMode: '3D',
      pitch: 20,
      showLabel: true,
    });

    createFlyLines(map, [props.lng, props.lat]);
  } else {
    console.error('经纬度坐标未找到');
  }
});
</script>

<style scoped>
.amap-container {
  width: 100%;
  height: 100%;
  border-radius: 10px;
}
</style>
