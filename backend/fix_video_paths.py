#!/usr/bin/env python3
"""修复视频流文件路径脚本
根据实际文件系统中的视频文件，更新数据库中的 file_path
"""

import os
import sys
from database import SessionLocal
from database import VideoStream
from sqlalchemy import text

def fix_video_paths():
    """修复视频流文件路径"""
    # 获取项目根目录
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VIDEO_DIR = os.path.join(PROJECT_ROOT, 'data', 'video')
    
    if not os.path.exists(VIDEO_DIR):
        print(f'错误: 视频目录不存在: {VIDEO_DIR}')
        return
    
    # 获取所有视频文件
    video_files = {}
    for filename in os.listdir(VIDEO_DIR):
        if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.webm')):
            # 提取文件名（不含扩展名）作为键
            base_name = os.path.splitext(filename)[0]
            video_files[base_name] = filename
    
    print(f'找到 {len(video_files)} 个视频文件')
    
    db = SessionLocal()
    try:
        # 查询所有视频流
        streams = db.query(VideoStream).all()
        print(f'数据库中有 {len(streams)} 条视频流记录')
        
        updated_count = 0
        not_found_count = 0
        
        for stream in streams:
            if not stream.file_path:
                continue
            
            # 获取当前路径的文件名（不含扩展名）
            current_path = stream.file_path
            # 提取文件名
            if '/' in current_path:
                current_filename = os.path.basename(current_path)
            elif '\\' in current_path:
                current_filename = os.path.basename(current_path)
            else:
                current_filename = current_path
            
            current_base_name = os.path.splitext(current_filename)[0]
            
            # 尝试匹配实际文件
            matched_file = None
            if current_base_name in video_files:
                matched_file = video_files[current_base_name]
            else:
                # 尝试模糊匹配（去掉空格、特殊字符等）
                current_clean = current_base_name.replace(' ', '').replace('_', '').replace('-', '')
                for file_base, file_name in video_files.items():
                    file_clean = file_base.replace(' ', '').replace('_', '').replace('-', '')
                    if current_clean in file_clean or file_clean in current_clean:
                        matched_file = file_name
                        print(f'  模糊匹配: {current_base_name} -> {file_name}')
                        break
            
            if matched_file:
                new_path = f'./data/video/{matched_file}'
                # 验证文件是否存在
                full_path = os.path.join(PROJECT_ROOT, 'data', 'video', matched_file)
                if os.path.exists(full_path):
                    if stream.file_path != new_path:
                        print(f'更新 ID {stream.id}: {stream.file_path} -> {new_path}')
                        stream.file_path = new_path
                        updated_count += 1
                    else:
                        print(f'ID {stream.id} 路径已正确: {new_path}')
                else:
                    print(f'警告: 文件不存在: {full_path}')
            else:
                print(f'未找到匹配文件: {current_base_name} (ID: {stream.id})')
                not_found_count += 1
        
        # 提交更改
        if updated_count > 0:
            db.commit()
            print(f'\n成功更新 {updated_count} 条记录')
        else:
            print('\n没有需要更新的记录')
        
        if not_found_count > 0:
            print(f'警告: {not_found_count} 条记录未找到匹配的视频文件')
        
        # 验证更新结果
        result = db.execute(text('''
            SELECT COUNT(*) as count
            FROM video_streams
            WHERE file_path LIKE './data/video/%'
        '''))
        count = result.fetchone()[0]
        print(f'现在有 {count} 条记录的路径指向 ./data/video/')
        
    except Exception as e:
        db.rollback()
        print(f'更新失败: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    print('=' * 50)
    print('修复视频流文件路径')
    print('=' * 50)
    fix_video_paths()
    print('=' * 50)
    print('完成')
    print('=' * 50)

