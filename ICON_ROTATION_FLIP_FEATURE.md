# 摄像头图标旋转和翻转功能

## 功能概述

在设备详细信息编辑页面（如图二所示）添加了图标旋转和镜面翻转设置功能，以及实时预览效果。

## 实现的功能

### 1. 图标旋转角度设置 ✅

- **控件类型**: 滑块（Slider）
- **范围**: 0-360度
- **步进**: 1度
- **显示**: 滑块 + 数字输入框 + 度数显示

### 2. 镜面翻转设置 ✅

- **水平翻转**: 复选框开关
- **垂直翻转**: 复选框开关

### 3. 实时预览效果 ✅

- **预览区域**: 右侧显示图标预览
- **实时更新**: 当旋转角度或翻转状态改变时，预览图标实时更新
- **变换效果**: 应用 CSS transform 属性实现旋转和翻转

## 实现细节

### 1. 前端组件修改 (`admin_frontend/src/views/admin/DeviceManagementView.vue`)

#### 添加的状态变量

```javascript
// 图标显示设置（仅摄像头设备）
const iconRotation = ref(0)              // 旋转角度（0-360度）
const iconFlipHorizontal = ref(false)    // 水平翻转
const iconFlipVertical = ref(false)      // 垂直翻转
```

#### 计算属性

```javascript
// 计算图标变换样式
const iconTransformStyle = computed(() => {
  const transforms = []
  if (iconRotation.value !== 0) {
    transforms.push(`rotate(${iconRotation.value}deg)`)
  }
  if (iconFlipHorizontal.value) {
    transforms.push('scaleX(-1)')
  }
  if (iconFlipVertical.value) {
    transforms.push('scaleY(-1)')
  }
  return {
    transform: transforms.length > 0 ? transforms.join(' ') : 'none'
  }
})
```

#### 图标路径获取

```javascript
// 获取摄像头图标路径（使用内联 SVG 数据 URL）
const getCameraIconSrc = () => {
  const cameraName = formData.value.name || ''
  const isCheckpoint = cameraName.includes('卡口')
  
  if (isCheckpoint) {
    // 球型摄像头（卡口）- 绿色圆形图标
    return 'data:image/svg+xml;base64,...'
  } else {
    // 监控摄像头（电警等）- 黄色摄像头图标
    return 'data:image/svg+xml;base64,...'
  }
}
```

#### UI 界面

```vue
<!-- 图标显示设置（仅摄像头设备） -->
<template v-if="deviceDetail?.device_type?.code === 'camera'">
  <el-divider content-position="left">图标显示设置</el-divider>
  
  <el-row :gutter="20">
    <el-col :span="16">
      <!-- 旋转角度 -->
      <el-form-item label="旋转角度">
        <el-slider
          v-model="iconRotation"
          :min="0"
          :max="360"
          :step="1"
          show-input
          @input="updateIconPreview"
        />
        <span>{{ iconRotation }}°</span>
      </el-form-item>
      
      <!-- 镜面翻转 -->
      <el-form-item label="镜面翻转">
        <el-checkbox v-model="iconFlipHorizontal" @change="updateIconPreview">
          水平翻转
        </el-checkbox>
        <el-checkbox v-model="iconFlipVertical" @change="updateIconPreview">
          垂直翻转
        </el-checkbox>
      </el-form-item>
    </el-col>
    
    <el-col :span="8">
      <!-- 图标预览 -->
      <el-form-item label="预览效果">
        <div class="icon-preview-container">
          <img
            :src="getCameraIconSrc()"
            alt="摄像头图标"
            class="icon-preview"
            :style="iconTransformStyle"
          />
        </div>
      </el-form-item>
    </el-col>
  </el-row>
</template>
```

### 2. 数据保存

图标显示设置会保存到设备的 `parameters` 中：
- `icon_rotation_angle`: 旋转角度（数字）
- `icon_flip_horizontal`: 水平翻转（布尔值）
- `icon_flip_vertical`: 垂直翻转（布尔值）

### 3. 数据加载

当编辑摄像头设备时，会自动从 `parameters` 中加载：
- `icon_rotation_angle` 或 `rotation_angle` → `iconRotation`
- `icon_flip_horizontal` 或 `flip_horizontal` → `iconFlipHorizontal`
- `icon_flip_vertical` 或 `flip_vertical` → `iconFlipVertical`

## 使用说明

### 1. 编辑摄像头设备

1. 打开设备管理页面
2. 点击摄像头设备的"编辑"按钮
3. 在编辑对话框中，向下滚动到"图标显示设置"部分

### 2. 设置旋转角度

1. 拖动滑块或输入数字设置旋转角度（0-360度）
2. 右侧预览区域会实时显示旋转后的图标效果

### 3. 设置镜面翻转

1. 勾选"水平翻转"复选框，图标会水平翻转
2. 勾选"垂直翻转"复选框，图标会垂直翻转
3. 可以同时勾选两个选项
4. 右侧预览区域会实时显示翻转后的图标效果

### 4. 保存设置

1. 点击"保存"按钮
2. 图标显示设置会保存到设备参数中

## 下一步工作

### 待实现功能

1. **地图显示应用变换** ⏳
   - 在地图显示摄像头图标时，需要应用旋转和翻转变换
   - 修改 `TellhowTraffic/src/views/HomeView.vue` 中的 `addCameraMarker` 函数
   - 从设备参数中读取 `icon_rotation_angle`, `icon_flip_horizontal`, `icon_flip_vertical`
   - 创建变换后的 SVG 图标或使用 CSS transform

2. **设备类型参数定义** ⏳
   - 在设备类型"摄像头"中添加默认参数定义（可选）
   - 或者直接在参数中使用自定义键名

## 技术细节

### 变换组合顺序

CSS transform 的组合顺序很重要：
1. 先旋转，再翻转：`rotate(90deg) scaleX(-1)`
2. 先翻转，再旋转：`scaleX(-1) rotate(90deg)`

**当前实现**：
- 先旋转，再翻转（符合直觉）
- 可以调整顺序以满足需求

### SVG 图标处理

由于图标在 `TellhowTraffic` 项目中，而编辑页面在 `admin_frontend` 项目中，使用了以下方案：
- 使用内联 SVG 数据 URL（base64 编码）
- 避免了跨项目路径问题

### 参数存储

图标显示设置存储在设备参数中：
- `icon_rotation_angle`: 数字（0-360）
- `icon_flip_horizontal`: 布尔值（true/false）
- `icon_flip_vertical`: 布尔值（true/false）

## 测试建议

1. ✅ **测试旋转角度设置**：
   - 拖动滑块设置不同角度（0°, 90°, 180°, 270°, 360°）
   - 确认预览图标正确旋转
   - 确认保存后数据正确

2. ✅ **测试镜面翻转**：
   - 勾选"水平翻转"，确认图标水平翻转
   - 勾选"垂直翻转"，确认图标垂直翻转
   - 同时勾选两个选项，确认效果叠加

3. ✅ **测试预览效果**：
   - 修改旋转角度或翻转状态
   - 确认预览图标实时更新
   - 确认变换效果正确

4. ⏳ **测试地图显示**：
   - 设置旋转和翻转后，保存设备
   - 在前端地图上查看设备图标
   - 确认图标应用了旋转和翻转变换（待实现）

## 结论

✅ **图标旋转和翻转功能已实现**

**实现内容**：
1. ✅ 图标旋转角度设置（滑块，0-360度）
2. ✅ 图标镜面翻转设置（水平翻转、垂直翻转）
3. ✅ 实时预览效果
4. ✅ 数据保存到设备参数
5. ✅ 数据加载和初始化

**待实现**：
- ⏳ 地图显示时应用变换（需要修改 `TellhowTraffic/src/views/HomeView.vue`）

---

**实现时间**: 2025-11-22  
**实现状态**: ✅ 已完成（编辑页面功能）  
**待实现**: ⏳ 地图显示应用变换  
**功能位置**: `admin_frontend/src/views/admin/DeviceManagementView.vue`
