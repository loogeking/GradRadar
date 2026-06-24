"""
诊断专业数量差异
对比平台返回数 vs 入库数
"""
import os
import sys
import json
import django
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.schools.models import School
from apps.majors.models import Major


def analyze_school(school_name):
    school = School.objects.filter(name=school_name).first()
    if not school or not school.platform_id:
        print(f'找不到学校: {school_name}')
        return

    print(f'\n{"=" * 60}')
    print(f'诊断: {school.name} (platform_id={school.platform_id})')
    print('=' * 60)

    # 1. 读取爬虫存档的原始数据
    raw_dir = BASE_DIR / 'data' / 'raw' / 'kaoyan_cn'
    page_files = sorted(raw_dir.glob(f'majors_{school.platform_id}_p*.json'))

    if not page_files:
        print(f'没有找到原始数据文件，路径: {raw_dir}')
        return

    all_raw_majors = []
    for f in page_files:
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
            all_raw_majors.extend(data.get('data', {}).get('data', []) or [])

    print(f'\n📥 原始数据：共 {len(all_raw_majors)} 条专业记录')
    print(f'   分布在 {len(page_files)} 个分页文件')

    # 2. 分析平台数据
    print(f'\n🔍 平台数据分析：')
    print(f'   不区分院系(depart_id=0): {sum(1 for m in all_raw_majors if m.get("depart_id") == 0)}')

    # 按 (depart_id, special_code, recruit_type_name) 去重
    unique_keys = set()
    for m in all_raw_majors:
        key = (m.get('depart_id'), m.get('special_code'),
               m.get('special_name'), m.get('recruit_type_name'))
        unique_keys.add(key)
    print(f'   按(院系+代码+名称+学习方式)去重后: {len(unique_keys)} 条')

    # 按年份分布
    year_count = Counter(m.get('year') for m in all_raw_majors)
    print(f'   按年份分布: {dict(year_count)}')

    # 同一专业在不同年份重复
    dedup_no_year = set()
    for m in all_raw_majors:
        key = (m.get('depart_id'), m.get('special_code'),
               m.get('special_name'), m.get('recruit_type_name'))
        dedup_no_year.add(key)
    print(f'   忽略年份去重后: {len(dedup_no_year)} 条')

    # 3. 数据库实际数据
    db_majors = Major.objects.filter(college__school=school)
    print(f'\n💾 数据库实际入库: {db_majors.count()} 条专业')

    # 4. 找出"被跳过"的专业（depart_id=0 的）
    skipped = [m for m in all_raw_majors if m.get('depart_id') == 0]
    if skipped:
        print(f'\n❌ 因 depart_id=0 被跳过的专业（前10个）：')
        seen = set()
        for m in skipped[:30]:
            key = (m.get('special_code'), m.get('special_name'))
            if key in seen:
                continue
            seen.add(key)
            print(f'   {m.get("special_code")} {m.get("special_name")} '
                  f'({m.get("recruit_type_name")}, {m.get("year")}年)')
            if len(seen) >= 10:
                break
        print(f'   ... 共 {len(set((m.get("special_code"), m.get("special_name")) for m in skipped))} 种唯一专业')

    # 5. 找出可能因为同名重复被合并的
    raw_keys = defaultdict(list)
    for m in all_raw_majors:
        if m.get('depart_id') == 0:
            continue
        key = (m.get('depart_id'), m.get('special_code'),
               m.get('special_name'), m.get('recruit_type_name'))
        raw_keys[key].append(m)

    duplicated = {k: v for k, v in raw_keys.items() if len(v) > 1}
    if duplicated:
        print(f'\n🔀 同(院系+代码+名称+学习方式)的重复记录数: {len(duplicated)} 组')
        for k, v in list(duplicated.items())[:5]:
            print(f'   {k[2]}({k[1]}) - {k[3]}: {len(v)} 条')
            for m in v:
                print(f'      year={m.get("year")}, plan_id={m.get("plan_id")}')


if __name__ == '__main__':
    analyze_school('清华大学')
    analyze_school('北京大学')
    analyze_school('浙江大学')