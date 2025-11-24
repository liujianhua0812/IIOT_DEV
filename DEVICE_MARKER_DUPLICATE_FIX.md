# 设备标记重复问题修复

## 问题描述

修改设备坐标后，地图上同时出现两个相同设备的标记：
- 左下角的黄色摄像头（原来的位置）
- 右下方的黄色摄像头（修改后的位置）

**问题现象**：
- 修改设备"韶山东路莲城大道北向电警500W"的坐标后
- 地图上出现两个相同设备的标记，分别在旧位置和新位置
- 如图一所示，地图上同时存在新旧两个位置的标记

## 问题根源

### 1. `loadAllDevices` 函数没有清除旧标记

`loadAllDevices` 函数在加载设备时，**没有先调用 `clearMarkers()`** 来清除旧的标记：

```javascript
// ❌ 错误：没有清除旧标记
const loadAllDevices = async () => {
  if (!map) return
  
  try {
    const response = await fetchMapDevices()
    const data = response.data
    
    // 直接添加新标记，但不清除旧标记
    if (data.devices && Array.isArray(data.devices)) {
      data.devices.forEach((device) => {
        // 添加标记...
        addCameraMarker(device, ...)
      })
    }
  } catch (error) {
    // ...
  }
}
```

### 2. 标记添加逻辑

每个设备都会调用 `addCameraMarker()` 等函数添加标记：
- `addCameraMarker()` 会将标记添加到地图：`map.add(marker)`
- 同时将标记推入 `markers` 数组：`markers.push(marker)`
- **但没有检查是否已存在相同设备的标记**

### 3. 设备更新流程

1. 用户在后台管理系统中更新设备坐标
2. 设备坐标更新成功（数据库中已更新）
3. 前端刷新或重新加载地图时，调用 `loadAllDevices()`
4. `loadAllDevices()` 直接从 API 获取最新数据
5. **问题**：直接添加新标记，但没有清除旧标记
6. 结果：新旧标记同时存在

## 修复方案

### 1. 在 `loadAllDevices` 开始时清除旧标记（已修复）

在 `loadAllDevices` 函数开始处添加 `clearMarkers()` 调用：

```javascript
// ✅ 正确：先清除旧标记
const loadAllDevices = async () => {
  if (!map) return
  
  try {
    // 清除所有旧标记，避免重复添加
    clearMarkers()
    
    const response = await fetchMapDevices()
    const data = response.data
    
    // 然后添加新标记...
    if (data.devices && Array.isArray(data.devices)) {
      data.devices.forEach((device) => {
        // 添加标记...
        addCameraMarker(device, ...)
      })
    }
  } catch (error) {
    // ...
  }
}
```

**修复位置**：`TellhowTraffic/src/views/HomeView.vue` 第 588 行

### 2. `clearMarkers` 函数实现

`clearMarkers` 函数已经存在，它会：
1. 关闭活动信息窗口
2. 遍历所有标记并移除
3. 清空 `markers` 数组
4. 清除拓扑线条（如果不在拓扑视图中）

```javascript
const clearMarkers = () => {
  closeActiveInfoWindow()
  markers.forEach(marker => {
    if (marker && map && map.remove) {
      map.remove(marker)
    }
  })
  markers = []
  if (!showTopology.value) {
    clearTopologyLines()
  }
}
```

**位置**：`TellhowTraffic/src/views/HomeView.vue` 第 1248-1259 行

## 修复效果

### 修复前
- ❌ 修改设备坐标后，地图上同时存在新旧两个位置的标记
- ❌ `loadAllDevices()` 直接添加新标记，不清除旧标记
- ❌ 设备列表中出现重复的设备标记

### 修复后
- ✅ 修改设备坐标后，地图上只显示新位置的标记
- ✅ `loadAllDevices()` 先清除旧标记，再添加新标记
- ✅ 设备列表中没有重复的设备标记

## 影响范围

### 受影响的函数
- ✅ `loadAllDevices()` - 加载所有设备（已修复）
- ❌ `loadIntersectionData()` - 加载路口数据（已正确调用 `clearMarkers()`）
- ❌ `toggleDeviceType()` - 切换设备类型显示（已正确调用 `clearMarkers()`）
- ❌ `toggleTopologyView()` - 切换拓扑视图（已正确调用 `clearMarkers()`）

### 不受影响的功能
- ✅ 路口数据加载（已正确处理）
- ✅ 设备类型切换（已正确处理）
- ✅ 拓扑视图切换（已正确处理）

## 为什么其他函数没问题？

其他函数（`loadIntersectionData`, `toggleDeviceType`, `toggleTopologyView`）在调用 `loadAllDevices()` 之前已经调用了 `clearMarkers()`：

```javascript
const toggleDeviceType = (type) => {
  // ...切换逻辑...
  if (selectedIntersection.value) {
    loadIntersectionData(selectedIntersection.value)
  } else {
    clearMarkers()  // ✅ 已调用
    loadAllDevices()
  }
}

const toggleTopologyView = () => {
  // ...切换逻辑...
  if (selectedIntersection.value) {
    loadIntersectionData(selectedIntersection.value)
  } else {
    clearMarkers()  // ✅ 已调用
    loadAllDevices()
  }
}
```

**但是**，如果其他地方直接调用 `loadAllDevices()`（例如页面刷新、API 更新等），就会出现问题。

## 测试建议

1. ✅ **测试修改设备坐标**：
   - 在后台管理系统中修改设备"韶山东路莲城大道北向电警500W"的坐标
   - 刷新前端页面
   - 确认地图上只显示新位置的标记，没有旧位置的标记

2. ✅ **测试页面刷新**：
   - 在地图页面刷新浏览器
   - 确认所有设备标记正常显示，没有重复

3. ✅ **测试设备类型切换**：
   - 切换设备类型显示（摄像头、信号机等）
   - 确认标记正常切换，没有重复

4. ✅ **测试拓扑视图切换**：
   - 切换拓扑视图
   - 确认标记和线条正常显示，没有重复

## 结论

✅ **问题已修复**

**修复内容**：
1. 在 `loadAllDevices()` 函数开始处添加 `clearMarkers()` 调用
2. 确保每次加载设备时都先清除旧标记，再添加新标记

**修复效果**：
- ✅ 修改设备坐标后，地图上只显示新位置的标记
- ✅ 不会再出现重复的设备标记
- ✅ 所有设备标记正常显示和更新

---

**修复时间**: 2025-11-22  
**修复状态**: ✅ 已完成  
**问题类型**: 逻辑缺陷（缺少标记清除）  
**解决方案**: 在 `loadAllDevices()` 中先清除旧标记，再添加新标记  
**修复位置**: `TellhowTraffic/src/views/HomeView.vue` - `loadAllDevices()` 函数
