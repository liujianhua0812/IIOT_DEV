#!/usr/bin/env python3
"""将 AVI 格式视频转换为 MP4 格式
使用 ffmpeg 进行转换，并更新数据库中的文件路径
"""

import os
import sys
import subprocess
from pathlib import Path
from database import SessionLocal
from database import VideoStream
from sqlalchemy import text

def check_ffmpeg():
    """检查 ffmpeg 是否已安装"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print('✓ ffmpeg 已安装')
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print('✗ 错误: 未找到 ffmpeg')
    print('请先安装 ffmpeg:')
    print('  Windows: https://ffmpeg.org/download.html')
    print('  或使用: choco install ffmpeg (需要 Chocolatey)')
    print('  或使用: winget install ffmpeg')
    return False

def convert_video(input_path, output_path, quality='medium'):
    """使用 ffmpeg 转换视频格式
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        quality: 视频质量 ('high', 'medium', 'low')
    
    Returns:
        bool: 转换是否成功
    """
    # 质量预设
    quality_presets = {
        'high': ['-crf', '18', '-preset', 'slow'],
        'medium': ['-crf', '23', '-preset', 'medium'],
        'low': ['-crf', '28', '-preset', 'fast']
    }
    
    preset = quality_presets.get(quality, quality_presets['medium'])
    
    # ffmpeg 命令
    # -i: 输入文件
    # -c:v libx264: 使用 H.264 编码器
    # -c:a aac: 使用 AAC 音频编码器
    # -movflags +faststart: 优化 MP4 文件，支持流式播放
    # -y: 覆盖输出文件（如果存在）
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-movflags', '+faststart',
        '-y'  # 覆盖输出文件
    ] + preset + [output_path]
    
    try:
        print(f'  正在转换: {os.path.basename(input_path)}')
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时
        )
        
        if result.returncode == 0:
            # 检查输出文件是否存在
            if os.path.exists(output_path):
                input_size = os.path.getsize(input_path)
                output_size = os.path.getsize(output_path)
                print(f'  ✓ 转换成功 ({input_size // 1024 // 1024}MB -> {output_size // 1024 // 1024}MB)')
                return True
            else:
                print(f'  ✗ 转换失败: 输出文件不存在')
                return False
        else:
            print(f'  ✗ 转换失败: {result.stderr[:200]}')
            return False
    except subprocess.TimeoutExpired:
        print(f'  ✗ 转换超时')
        return False
    except Exception as e:
        print(f'  ✗ 转换异常: {str(e)}')
        return False

def convert_all_avi_to_mp4(delete_original=False, quality='medium'):
    """转换所有 AVI 视频为 MP4 格式
    
    Args:
        delete_original: 是否删除原始 AVI 文件
        quality: 视频质量 ('high', 'medium', 'low')
    """
    # 检查 ffmpeg
    if not check_ffmpeg():
        return
    
    # 获取项目根目录
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VIDEO_DIR = os.path.join(PROJECT_ROOT, 'data', 'video')
    
    if not os.path.exists(VIDEO_DIR):
        print(f'错误: 视频目录不存在: {VIDEO_DIR}')
        return
    
    # 查找所有 AVI 文件
    avi_files = []
    for filename in os.listdir(VIDEO_DIR):
        if filename.lower().endswith('.avi'):
            avi_files.append(os.path.join(VIDEO_DIR, filename))
    
    if not avi_files:
        print('没有找到 AVI 文件')
        return
    
    print(f'找到 {len(avi_files)} 个 AVI 文件')
    print(f'视频质量: {quality}')
    print(f'删除原始文件: {"是" if delete_original else "否"}')
    print('=' * 50)
    
    # 转换统计
    converted_count = 0
    failed_count = 0
    skipped_count = 0
    
    db = SessionLocal()
    try:
        for avi_path in avi_files:
            # 生成 MP4 文件名
            base_name = os.path.splitext(avi_path)[0]
            mp4_path = base_name + '.mp4'
            
            # 如果 MP4 文件已存在，询问是否跳过
            if os.path.exists(mp4_path):
                print(f'跳过 (MP4 已存在): {os.path.basename(avi_path)}')
                skipped_count += 1
                # 更新数据库路径
                update_database_path(db, avi_path, mp4_path)
                continue
            
            # 转换视频
            if convert_video(avi_path, mp4_path, quality):
                converted_count += 1
                # 更新数据库路径
                update_database_path(db, avi_path, mp4_path)
                
                # 删除原始文件（如果选择）
                if delete_original:
                    try:
                        os.remove(avi_path)
                        print(f'  已删除原始文件: {os.path.basename(avi_path)}')
                    except Exception as e:
                        print(f'  警告: 删除原始文件失败: {str(e)}')
            else:
                failed_count += 1
        
        # 提交数据库更改
        db.commit()
        
        print('=' * 50)
        print(f'转换完成!')
        print(f'  成功: {converted_count} 个')
        print(f'  失败: {failed_count} 个')
        print(f'  跳过: {skipped_count} 个')
        
    except Exception as e:
        db.rollback()
        print(f'错误: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def update_database_path(db, avi_path, mp4_path):
    """更新数据库中的视频路径"""
    try:
        # 获取相对路径
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        avi_relative = os.path.relpath(avi_path, PROJECT_ROOT).replace('\\', '/')
        mp4_relative = os.path.relpath(mp4_path, PROJECT_ROOT).replace('\\', '/')
        
        # 确保路径以 ./ 开头
        if not avi_relative.startswith('./'):
            avi_relative = './' + avi_relative
        if not mp4_relative.startswith('./'):
            mp4_relative = './' + mp4_relative
        
        # 查找并更新数据库记录
        result = db.execute(text('''
            UPDATE video_streams
            SET file_path = :new_path
            WHERE file_path = :old_path
        '''), {'new_path': mp4_relative, 'old_path': avi_relative})
        
        if result.rowcount > 0:
            print(f'  ✓ 已更新数据库路径: {result.rowcount} 条记录')
        
    except Exception as e:
        print(f'  ⚠ 更新数据库路径失败: {str(e)}')

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='将 AVI 格式视频转换为 MP4 格式')
    parser.add_argument(
        '--quality',
        choices=['high', 'medium', 'low'],
        default='medium',
        help='视频质量 (默认: medium)'
    )
    parser.add_argument(
        '--delete-original',
        action='store_true',
        help='转换后删除原始 AVI 文件'
    )
    
    args = parser.parse_args()
    
    print('=' * 50)
    print('AVI 转 MP4 视频转换工具')
    print('=' * 50)
    print()
    
    convert_all_avi_to_mp4(
        delete_original=args.delete_original,
        quality=args.quality
    )
    
    print('=' * 50)

