# 红绿灯状态逻辑修复说明

## 修复内容

已修改代码逻辑，使其同时支持数字值和字符串值，**保留原有逻辑**。

## 修改的代码

### 1. 添加状态标准化函数 (`TellhowTraffic/src/views/HomeView.vue` 第1109-1128行)

```javascript
// 将状态值转换为标准字符串（支持数字和字符串）
const normalizeTrafficLightStatus = (status) => {
  if (!status) return 'red'  // 默认值
  
  // 转换为字符串并转为小写
  const statusStr = String(status).toLowerCase().trim()
  
  // 支持数字值：1=red, 2=yellow, 3=green
  if (statusStr === '1') return 'red'
  if (statusStr === '2') return 'yellow'
  if (statusStr === '3') return 'green'
  
  // 支持字符串值：red, yellow, amber, green
  if (statusStr === 'red') return 'red'
  if (statusStr === 'yellow' || statusStr === 'amber') return 'yellow'
  if (statusStr === 'green') return 'green'
  
  // 如果都不匹配，返回默认值
  return 'red'
}
```

### 2. 修改图标生成函数 (`TellhowTraffic/src/views/HomeView.vue` 第1130-1143行)

```javascript
// 根据红绿灯状态生成SVG图标
const createTrafficLightIcon = (status) => {
  const normalizedStatus = normalizeTrafficLightStatus(status)  // 先标准化状态
  let redOpacity = 0.1
  let yellowOpacity = 0.1
  let greenOpacity = 0.1
  
  if (normalizedStatus === 'red') {
    redOpacity = 1
  } else if (normalizedStatus === 'yellow') {
    yellowOpacity = 1
  } else if (normalizedStatus === 'green') {
    greenOpacity = 1
  }
  // ... 生成SVG图标
}
```

### 3. 修改初始图标创建 (`TellhowTraffic/src/views/HomeView.vue` 第1179行)

```javascript
// 根据状态生成图标（支持数字和字符串值）
const status = normalizeTrafficLightStatus(light.traffic_light_status)
const iconUrl = createTrafficLightIcon(status)
```

### 4. 修改状态更新逻辑 (`TellhowTraffic/src/views/HomeView.vue` 第376-394行)

```javascript
const newStatus = statusMap.get(deviceCode)

if (newStatus) {
  // 标准化状态值（支持数字和字符串）
  const normalizedStatus = normalizeTrafficLightStatus(newStatus)
  if (marker.extData && marker.extData.status !== normalizedStatus) {
    // 状态已改变，更新图标
    const iconUrl = createTrafficLightIcon(normalizedStatus)
    // ... 更新图标
  }
}
```

## 支持的状态值

### 数字值
- `1` → `'red'` (红色)
- `2` → `'yellow'` (黄色)
- `3` → `'green'` (绿色)

### 字符串值
- `'red'` → `'red'` (红色)
- `'yellow'` 或 `'amber'` → `'yellow'` (黄色)
- `'green'` → `'green'` (绿色)

### 默认值
- `null`、`undefined` 或空值 → `'red'` (红色)
- 不匹配的值 → `'red'` (红色)

## 恢复的数据库数据

已恢复 TRAFFIC_LIGHT_005 的 `traffic_light_status` 参数值：
- `param_value`: `1` (数字值)

## 预期结果

修复后，TRAFFIC_LIGHT_005 应该：
1. ✅ `traffic_light_status` 参数值为 `1`（已恢复）
2. ✅ 前端将数字 `1` 标准化为字符串 `'red'`
3. ✅ 图标显示为亮起的红灯（与其他红绿灯一致）
4. ✅ 同时支持字符串值 `'red'`、`'yellow'`、`'green'` 和数字值 `1`、`2`、`3`

---

**修复时间**: 2025-11-22  
**修复状态**: ✅ 已完成  
**修复方式**: 修改前端代码，支持数字值和字符串值，保留原有逻辑
