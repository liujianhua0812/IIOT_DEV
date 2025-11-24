# TRAFFIC_LIGHT_005 图标不亮问题修复

## 问题原因

**TRAFFIC_LIGHT_005 的 `traffic_light_status` 参数值是数字 `1`，而不是字符串 `'red'`、`'yellow'` 或 `'green'`**

### 数据库查询结果

**正常设备（TRAFFIC_LIGHT_001-004）**:
- `traffic_light_status` 参数值：NULL（空值）

**问题设备（TRAFFIC_LIGHT_005）**:
- `traffic_light_status` 参数值：`1`（数字值）← 问题所在

### 前端代码逻辑

1. **初始图标创建** (`HomeView.vue` 第1161行):
```javascript
const status = light.traffic_light_status || 'red'
```
   - 如果 `traffic_light_status` 为 `null` → 使用默认值 `'red'` → 图标亮起 ✅
   - 如果 `traffic_light_status` 为 `1`（数字）→ 使用 `1` → 图标不亮起 ❌

2. **图标生成函数** (`HomeView.vue` 第1110-1149行):
```javascript
const createTrafficLightIcon = (status) => {
  const statusLower = (status || 'red').toLowerCase()
  if (statusLower === 'red') {
    redOpacity = 1  // 亮起红灯
  } else if (statusLower === 'yellow' || statusLower === 'amber') {
    yellowOpacity = 1  // 亮起黄灯
  } else if (statusLower === 'green') {
    greenOpacity = 1  // 亮起绿灯
  }
  // 如果都不匹配，所有灯的透明度都是 0.1 → 图标不亮起
}
```

**关键点**：
- 只有当 `status` 为 `'red'`、`'yellow'`、`'amber'` 或 `'green'` 时才会亮起
- 数字 `1` 不匹配任何条件，所有灯的透明度都是 0.1 → 图标不亮起

## 修复方案

### 方案1: 删除无效的参数值（已完成，推荐）

删除 TRAFFIC_LIGHT_005 的 `traffic_light_status` 参数值，让它与其他红绿灯保持一致：

```sql
DELETE FROM device_parameter_values 
WHERE device_id = (
  SELECT id FROM devices WHERE code = 'TRAFFIC_LIGHT_005'
) 
AND param_key = 'traffic_light_status';
```

**优点**：
- 与其他红绿灯保持一致（都没有参数值）
- 前端会使用默认值 `'red'`，图标会正常亮起
- 如果将来需要设置状态，可以通过设备管理界面设置正确的字符串值

### 方案2: 将参数值设置为正确的字符串值

如果需要保留参数值，可以设置为正确的字符串：

```sql
UPDATE device_parameter_values 
SET param_value = 'red'
WHERE device_id = (
  SELECT id FROM devices WHERE code = 'TRAFFIC_LIGHT_005'
) 
AND param_key = 'traffic_light_status';
```

## 验证修复

修复后，TRAFFIC_LIGHT_005 应该：
1. ✅ `traffic_light_status` 参数值为 NULL（与其他红绿灯一致）
2. ✅ API 返回的 `traffic_light_status` 为 `null`
3. ✅ 前端使用默认值 `'red'` 创建图标
4. ✅ 图标显示为亮起的红灯

## 预期结果

刷新地图页面后，TRAFFIC_LIGHT_005 应该：
- 显示为亮起的红灯（与 TRAFFIC_LIGHT_001-004 一致）
- 图标正常显示
- 点击图标可以查看设备信息

---

**修复时间**: 2025-11-22  
**修复状态**: ✅ 已完成  
**问题原因**: traffic_light_status 参数值是数字 `1`，而不是字符串 `'red'`  
**解决方案**: 删除无效的参数值，使用默认值 `'red'`
