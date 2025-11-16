# 设备类型管理设计文档

## 概述

设备类型管理系统用于管理平台支持的设备类型，并为每种设备类型配置特有的参数。设备信息分为两部分：
- **通用字段**：存储在设备表（devices）中，所有设备类型共享
- **类型特有字段**：存储在设备类型参数表（device_type_parameters）中，每种设备类型有独立的参数配置

## 数据库设计

### 1. 设备类型表 (device_types)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| code | VARCHAR(50) | 类型代码（唯一，如：camera, switch, plc, server） |
| name | VARCHAR(100) | 类型名称（如：摄像头、交换机、PLC、服务器） |
| description | TEXT | 类型描述 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 2. 设备类型参数表 (device_type_parameters)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| device_type_id | INTEGER | 关联设备类型ID |
| param_key | VARCHAR(50) | 参数键（英文，如：exposure, resolution） |
| param_name | VARCHAR(100) | 参数名称（中文，如：曝光时间、分辨率） |
| param_type | VARCHAR(20) | 参数类型（string, number, boolean, date） |
| required | BOOLEAN | 是否必填 |
| default_value | TEXT | 默认值（可选） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 3. 设备表 (devices) - 通用字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| code | VARCHAR(50) | 设备编号（唯一） |
| name | VARCHAR(100) | 设备名称 |
| device_type_id | INTEGER | 关联设备类型ID |
| status | VARCHAR(20) | 设备状态（在线、离线、告警等） |
| health_status | VARCHAR(20) | 健康状况（良好、需关注、故障等） |
| ip_address | VARCHAR(50) | IP地址 |
| last_heartbeat | DATETIME | 最后心跳时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4. 设备参数值表 (device_parameter_values)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| device_id | INTEGER | 关联设备ID |
| param_key | VARCHAR(50) | 参数键（对应device_type_parameters.param_key） |
| param_value | TEXT | 参数值 |
| updated_at | DATETIME | 更新时间 |

## 预设计的设备类型

### 1. 摄像头 (Camera)

**类型代码**: `camera`

**类型特有参数**:
- `exposure` (曝光时间) - string - 必填 - 示例: "8ms", "10ms"
- `resolution` (分辨率) - string - 必填 - 示例: "1920x1080", "2048x1536"
- `frame_rate` (帧率) - number - 可选 - 示例: 30, 60
- `sensor_type` (传感器类型) - string - 可选 - 示例: "CMOS", "CCD"
- `lens_type` (镜头类型) - string - 可选 - 示例: "定焦", "变焦"
- `night_vision` (夜视功能) - boolean - 可选 - 示例: true, false

### 2. 交换机 (Switch)

**类型代码**: `switch`

**类型特有参数**:
- `model` (型号) - string - 必填 - 示例: "TL-SG1024", "TL-SG5428"
- `port_count` (端口数量) - number - 必填 - 示例: 24, 48
- `port_type` (端口类型) - string - 必填 - 示例: "千兆", "万兆"
- `management_type` (管理类型) - string - 可选 - 示例: "Web管理", "SNMP"
- `vlan_support` (VLAN支持) - boolean - 可选 - 示例: true, false
- `poe_support` (POE支持) - boolean - 可选 - 示例: true, false

### 3. PLC (Programmable Logic Controller)

**类型代码**: `plc`

**类型特有参数**:
- `program` (程序版本) - string - 必填 - 示例: "ReadCode_V2.1", "QC_V1.8"
- `port` (端口) - string - 必填 - 示例: "ETH1", "COM1"
- `cpu_model` (CPU型号) - string - 可选 - 示例: "Intel Core i5"
- `memory_size` (内存大小) - string - 可选 - 示例: "4GB", "8GB"
- `io_points` (IO点数) - number - 可选 - 示例: 32, 64
- `communication_protocol` (通信协议) - string - 可选 - 示例: "Modbus", "Ethernet/IP"

### 4. 服务器 (Server)

**类型代码**: `server`

**类型特有参数**:
- `model` (型号) - string - 必填 - 示例: "Dell PowerEdge", "HP ProLiant"
- `cpu` (CPU) - string - 必填 - 示例: "Intel Xeon", "Intel Core i5"
- `memory` (内存) - string - 必填 - 示例: "16GB", "32GB"
- `storage` (存储) - string - 可选 - 示例: "500GB SSD", "1TB HDD"
- `os` (操作系统) - string - 可选 - 示例: "Linux", "Windows Server"
- `server_type` (服务器类型) - string - 可选 - 示例: "MES服务器", "MBI服务器", "数据库服务器"

## API 接口设计

### 获取设备类型列表
```
GET /api/device-types
Response: {
  "data": {
    "device_types": [
      {
        "id": 1,
        "code": "camera",
        "name": "摄像头",
        "description": "工业摄像头设备",
        "parameters": [
          {
            "key": "exposure",
            "name": "曝光时间",
            "type": "string",
            "required": true
          },
          ...
        ]
      },
      ...
    ]
  }
}
```

### 创建设备类型
```
POST /api/device-types
Request: {
  "name": "摄像头",
  "code": "camera",
  "description": "工业摄像头设备",
  "parameters": [
    {
      "name": "曝光时间",
      "key": "exposure",
      "type": "string",
      "required": true
    },
    ...
  ]
}
```

### 更新设备类型
```
PUT /api/device-types/:id
Request: {
  "name": "摄像头",
  "description": "工业摄像头设备（更新）",
  "parameters": [...]
}
```

### 删除设备类型
```
DELETE /api/device-types/:id
```

## 前端页面功能

1. **设备类型列表展示**
   - 以卡片形式展示所有设备类型
   - 显示类型名称、代码、描述
   - 显示该类型的所有特有参数

2. **新增设备类型**
   - 输入类型名称、代码、描述
   - 动态添加/删除类型特有参数
   - 为每个参数配置：名称、键、类型、是否必填

3. **编辑设备类型**
   - 修改类型信息
   - 修改参数配置

4. **删除设备类型**
   - 确认删除操作
   - 删除前检查是否有设备使用该类型

## 使用说明

1. 在"设备类型管理"页面中，可以查看所有已配置的设备类型
2. 点击"新增设备类型"按钮，创建新的设备类型并配置其特有参数
3. 点击"编辑"按钮，修改已有设备类型的配置
4. 点击"删除"按钮，删除不需要的设备类型（需确保没有设备使用该类型）

## 注意事项

1. 设备类型代码（code）必须唯一，且只能包含小写字母、数字和下划线
2. 删除设备类型前，需要确保没有设备正在使用该类型
3. 修改设备类型的参数配置时，已存在的设备参数值不会自动更新，需要手动处理
4. 参数键（param_key）在同一设备类型内必须唯一

