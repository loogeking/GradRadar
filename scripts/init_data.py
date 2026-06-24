"""
初始化种子数据脚本（精简版，不再导入学校）
学校数据全部由爬虫负责采集

执行：python scripts/init_data.py
"""
import os
import sys
import json
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.schools.models import Province
from apps.subjects.models import SubjectCategory


def load_json(filename):
    path = BASE_DIR / 'data' / 'seed' / filename
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_provinces():
    print('\n=== 导入省份 ===')
    data = load_json('provinces.json')
    created_count = 0
    for item in data:
        obj, created = Province.objects.get_or_create(
            name=item['name'],
            defaults={'short_name': item.get('short_name', '')}
        )
        if created:
            created_count += 1
            print(f'  ✓ {obj.name}')
    print(f'共 {Province.objects.count()} 条，本次新增 {created_count} 条\n')


def import_subjects():
    """两阶段导入：先建所有节点，再建parent关联"""
    print('=== 导入学科目录 ===')
    data = load_json('subjects.json')

    # 第一阶段：建所有节点
    for item in data:
        SubjectCategory.objects.update_or_create(
            code=item['code'],
            defaults={
                'name': item['name'],
                'level': item['level'],
                'category_code': item.get('category_code', ''),
                'category_name': item.get('category_name', ''),
                'is_academic': item.get('is_academic', True),
                'is_self_set': item.get('is_self_set', False),
            }
        )

    # 第二阶段：建parent关联
    for item in data:
        parent_code = item.get('parent_code')
        if parent_code:
            try:
                parent = SubjectCategory.objects.get(code=parent_code)
                SubjectCategory.objects.filter(code=item['code']).update(parent=parent)
            except SubjectCategory.DoesNotExist:
                print(f'  ⚠️ {item["code"]} 找不到父级 {parent_code}')

    print(f'共 {SubjectCategory.objects.count()} 条学科\n')


if __name__ == '__main__':
    import_provinces()
    import_subjects()
    print('=== 全部种子数据导入完成 ===')
    print('提示：学校数据由爬虫负责，请运行：')
    print('  python crawler/run.py --source kaoyan_cn --mode schools_only')