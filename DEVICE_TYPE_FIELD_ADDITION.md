# 设备详细信息添加"类型"字段

## 修改内容

在设备详细信息标签页中，在"IP地址"下方添加了"类型"信息行。

## 修改说明

### 1. 后端修改 (`backend/app.py` 第961-991行)

**修改前**：
- 只从参数值中获取 `ip_address` 和 `traffic_light_status`
- 没有获取 `type` 参数值

**修改后**：
- 增加了获取 `type` 参数值的逻辑
- 对于红绿灯设备，将 `type` 参数值添加到返回数据中，使用 `type_name` 字段（避免与设备类型代码 `type` 冲突）

```python
# 从参数值中获取 ip_address、traffic_light_status 和 type
ip_address = None
traffic_light_status = None
device_type_param = None
if device.parameter_values:
    for pv in device.parameter_values:
        if pv.param_key == "ip_address":
            ip_address = pv.param_value
        elif pv.param_key == "traffic_light_status":
            traffic_light_status = pv.param_value
        elif pv.param_key == "type":
            device_type_param = pv.param_value

# 如果是红绿灯，添加类型参数值
if device.device_type and device.device_type.code == 'traffic_light':
    device_dict["traffic_light_status"] = traffic_light_status
    if device_type_param:
        device_dict["type_name"] = device_type_param
```

### 2. 前端修改 (`TellhowTraffic/src/views/HomeView.vue` 第1227行)

**修改前**：
```javascript
fields: [
  { label: '设备编号', value: light.code || 'N/A' },
  { label: '红绿灯状态', value: statusText },
  { label: 'IP 地址', value: light.ip_address || 'N/A' }
]
```

**修改后**：
```javascript
fields: [
  { label: '设备编号', value: light.code || 'N/A' },
  { label: '红绿灯状态', value: statusText },
  { label: 'IP 地址', value: light.ip_address || 'N/A' },
  { label: '类型', value: light.type_name || light.parameters?.type || 'N/A' }
]
```

## API 返回数据验证

从 `/map/devices` API 返回的数据中，TRAFFIC_LIGHT_005 现在包含：
```json
{
  "code": "TRAFFIC_LIGHT_005",
  "name": "红绿灯05",
  "type": "traffic_light",
  "type_name": "行人及非机动车交通指示灯",
  "ip_address": "",
  "traffic_light_status": "1",
  ...
}
```

## 数据库数据

TRAFFIC_LIGHT_005 的参数值：
- `param_key`: "type"
- `param_value`: "行人及非机动车交通指示灯"

## 显示效果

在设备详细信息弹窗中，现在会显示：
1. 设备编号：TRAFFIC_LIGHT_005
2. 红绿灯状态：红色
3. IP 地址：N/A
4. **类型：行人及非机动车交通指示灯** ← 新增

## 注意事项

- 使用 `type_name` 字段避免与设备类型代码 `type` 冲突
- 如果设备没有 `type` 参数值，将显示 "N/A"
- 兼容性：如果没有 `type_name`，会尝试从 `light.parameters?.type` 获取

---

**修改时间**: 2025-11-22  
**修改状态**: ✅ 已完成  
**影响范围**: 红绿灯设备的详细信息显示
