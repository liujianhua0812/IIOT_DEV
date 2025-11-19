#!/usr/bin/env python3
"""更新视频流文件路径脚本
将 video_streams 表中的 file_path 从 ./data/ 更新为 ./data/video/
"""

import sys
from database import SessionLocal
from sqlalchemy import text

def update_video_paths():
    """更新视频流文件路径"""
    db = SessionLocal()
    try:
        # 查询所有需要更新的记录
        result = db.execute(text('''
            SELECT id, file_path
            FROM video_streams
            WHERE file_path LIKE './data/%'
            AND file_path NOT LIKE './data/video/%'
        '''))
        rows = result.fetchall()
        
        if not rows:
            print('没有需要更新的记录')
            return
        
        print(f'找到 {len(rows)} 条需要更新的记录')
        
        # 更新每条记录
        updated_count = 0
        for row in rows:
            old_path = row.file_path
            # 将 ./data/文件名 替换为 ./data/video/文件名
            if old_path.startswith('./data/'):
                # 提取文件名（去掉 ./data/ 前缀）
                filename = old_path.replace('./data/', '', 1)
                new_path = f'./data/video/{filename}'
                
                # 更新数据库
                db.execute(text('''
                    UPDATE video_streams
                    SET file_path = :new_path
                    WHERE id = :id
                '''), {'new_path': new_path, 'id': row.id})
                
                print(f'更新 ID {row.id}: {old_path} -> {new_path}')
                updated_count += 1
        
        # 提交更改
        db.commit()
        print(f'\n成功更新 {updated_count} 条记录')
        
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
    print('更新视频流文件路径')
    print('=' * 50)
    update_video_paths()
    print('=' * 50)
    print('完成')

