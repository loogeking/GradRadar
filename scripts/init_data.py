"""
初始化种子数据脚本
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

from apps.schools.models import Province, School
from apps.subjects.models import SubjectCategory, SubjectRating


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


def import_schools():
    print('=== 导入院校 ===')
    data = load_json('schools.json')
    created_count = 0
    for item in data:
        try:
            province = Province.objects.get(name=item['province'])
        except Province.DoesNotExist:
            print(f'  ✗ 跳过 {item["name"]}：找不到省份 {item["province"]}')
            continue

        obj, created = School.objects.update_or_create(
            name=item['name'],
            defaults={
                'code': item.get('code', ''),
                'province': province,
                'level': item.get('level', 'normal'),
                'is_985': item.get('is_985', False),
                'is_211': item.get('is_211', False),
                'is_double_first': item.get('is_double_first', False),
                'is_self_scoring': item.get('is_self_scoring', False),
                'school_type': item.get('school_type', ''),
                'province_area': item.get('province_area', 'A'),
                'official_url': item.get('official_url', ''),
            }
        )
        if created:
            created_count += 1
            print(f'  ✓ 新增 {obj.name}')
        else:
            print(f'  - 更新 {obj.name}')
    print(f'共 {School.objects.count()} 条，本次新增 {created_count} 条\n')


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


def import_subject_ratings():
    """导入学科评级"""
    filepath = BASE_DIR / 'data' / 'seed' / 'subject_ratings.json'
    if not filepath.exists():
        print('=== 跳过学科评级（文件不存在）===\n')
        return

    print('=== 导入学科评级 ===')
    data = load_json('subject_ratings.json')
    created_count = 0
    for item in data:
        try:
            school = School.objects.get(code=item['school_code'])
            subject = SubjectCategory.objects.get(code=item['subject_code'])
        except (School.DoesNotExist, SubjectCategory.DoesNotExist) as e:
            print(f'  ✗ 跳过：{e}')
            continue

        obj, created = SubjectRating.objects.update_or_create(
            school=school,
            subject=subject,
            evaluation_round=item['round'],
            defaults={'rating': item['rating']}
        )
        if created:
            created_count += 1
            print(f'  ✓ {school.name} - {subject.name} - {item["rating"]}')

    print(f'共 {SubjectRating.objects.count()} 条评级，本次新增 {created_count} 条\n')


if __name__ == '__main__':
    import_provinces()
    import_schools()
    import_subjects()
    import_subject_ratings()
    print('=== 全部导入完成 ===')