"""
初始化种子数据脚本
执行方式：python scripts/init_data.py
"""
import os
import sys
import json
import django

# 把项目根目录加入Python路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.schools.models import Province, School


def load_json(filename):
    path = os.path.join(BASE_DIR, 'data', 'seed', filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_provinces():
    """导入省份"""
    print('\n=== 开始导入省份 ===')
    data = load_json('provinces.json')
    created_count = 0
    for item in data:
        obj, created = Province.objects.get_or_create(
            name=item['name'],
            defaults={'short_name': item.get('short_name', '')}
        )
        if created:
            created_count += 1
            print(f'  ✓ 新增: {obj.name}')
        else:
            print(f'  - 已存在: {obj.name}')
    print(f'省份导入完成，新增 {created_count} 条，共 {Province.objects.count()} 条\n')


def import_schools():
    """导入院校"""
    print('=== 开始导入院校 ===')
    data = load_json('schools.json')
    created_count = 0
    for item in data:
        try:
            province = Province.objects.get(name=item['province'])
        except Province.DoesNotExist:
            print(f'  ✗ 跳过 {item["name"]}：找不到省份 {item["province"]}')
            continue

        obj, created = School.objects.get_or_create(
            name=item['name'],
            defaults={
                'code': item.get('code', ''),
                'province': province,
                'level': item.get('level', 'normal'),
                'is_985': item.get('is_985', False),
                'is_211': item.get('is_211', False),
                'is_double_first': item.get('is_double_first', False),
                'official_url': item.get('official_url', ''),
            }
        )
        if created:
            created_count += 1
            print(f'  ✓ 新增: {obj.name}')
        else:
            print(f'  - 已存在: {obj.name}')
    print(f'院校导入完成，新增 {created_count} 条，共 {School.objects.count()} 条\n')


if __name__ == '__main__':
    import_provinces()
    import_schools()
    print('=== 所有种子数据导入完成 ===')