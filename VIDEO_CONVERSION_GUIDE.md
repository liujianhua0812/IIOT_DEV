# AVI 转 MP4 视频转换指南

## 前置要求

### 1. 安装 FFmpeg

FFmpeg 是视频转换工具，需要先安装：

#### Windows 安装方法：

**方法一：使用 Chocolatey（推荐）**
```powershell
choco install ffmpeg
```

**方法二：使用 winget**
```powershell
winget install ffmpeg
```

**方法三：手动安装**
1. 访问 https://ffmpeg.org/download.html
2. 下载 Windows 版本
3. 解压到任意目录（如 `C:\ffmpeg`）
4. 将 `C:\ffmpeg\bin` 添加到系统 PATH 环境变量

**验证安装：**
```powershell
ffmpeg -version
```

## 使用方法

### 基本用法

```powershell
cd E:\code\IIOT_code\backend
python convert_avi_to_mp4.py
```

### 高级选项

```powershell
# 指定视频质量（high/medium/low）
python convert_avi_to_mp4.py --quality high

# 转换后删除原始 AVI 文件
python convert_avi_to_mp4.py --delete-original

# 组合使用
python convert_avi_to_mp4.py --quality medium --delete-original
```

### 使用批处理文件（Windows）

```powershell
cd E:\code\IIOT_code\backend
.\convert_avi_to_mp4.bat
```

## 功能说明

### 视频质量选项

- **high**: 高质量（文件较大，转换较慢）
  - CRF: 18, Preset: slow
  - 适合：最终发布版本
  
- **medium**: 中等质量（推荐，平衡文件大小和质量）
  - CRF: 23, Preset: medium
  - 适合：一般用途
  
- **low**: 低质量（文件较小，转换较快）
  - CRF: 28, Preset: fast
  - 适合：快速预览或测试

### 自动功能

1. **自动扫描**: 扫描 `data/video` 目录下的所有 AVI 文件
2. **自动转换**: 使用 FFmpeg 将 AVI 转换为 MP4
3. **自动更新数据库**: 转换成功后自动更新数据库中的文件路径
4. **智能跳过**: 如果 MP4 文件已存在，自动跳过转换

## 转换过程

1. 脚本会扫描 `E:\code\IIOT_code\data\video` 目录
2. 找到所有 `.avi` 文件
3. 使用 FFmpeg 转换为 `.mp4` 格式
4. 更新数据库 `video_streams` 表中的 `file_path` 字段
5. （可选）删除原始 AVI 文件

## 注意事项

1. **转换时间**: 视频转换可能需要较长时间，取决于视频大小和数量
2. **磁盘空间**: 确保有足够的磁盘空间（MP4 文件可能比 AVI 稍大或稍小）
3. **备份**: 建议在删除原始文件前先备份
4. **数据库**: 脚本会自动更新数据库路径，无需手动操作

## 示例输出

```
==================================================
AVI 转 MP4 视频转换工具
==================================================

✓ ffmpeg 已安装
找到 17 个 AVI 文件
视频质量: medium
删除原始文件: 否
==================================================
  正在转换: 韶山东路莲城大道西向电警500W1 20251103 072000 20251103 072300.avi
  ✓ 转换成功 (150MB -> 120MB)
  ✓ 已更新数据库路径: 1 条记录
  ...
==================================================
转换完成!
  成功: 17 个
  失败: 0 个
  跳过: 0 个
==================================================
```

## 故障排除

### 错误: 未找到 ffmpeg

**解决方案**: 按照上述方法安装 FFmpeg，并确保已添加到 PATH

### 转换失败

**可能原因**:
- 视频文件损坏
- 磁盘空间不足
- FFmpeg 版本不兼容

**解决方案**: 检查视频文件是否完整，确保有足够磁盘空间

### 数据库更新失败

**解决方案**: 检查数据库连接，确保后端服务可以正常访问数据库

