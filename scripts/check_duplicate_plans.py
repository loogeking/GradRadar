"""
诊断同(学院+代码+名称)下不同 plan_id 的差异
看看到底是真的"重复"，还是有实质区别
"""
import os
import sys
import json
import django
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.schools.models import School


def analyze(school_name, max_check=5):
    school = School.objects.filter(name=school_name).first()
    if not school or not school.platform_id:
        return

    print(f'\n{"=" * 60}')
    print(f'诊断: {school.name} 的重复专业差异')
    print('=' * 60)

    raw_dir = BASE_DIR / 'data' / 'raw' / 'kaoyan_cn'
    page_files = sorted(raw_dir.glob(f'majors_{school.platform_id}_p*.json'))

    all_raw = []
    for f in page_files:
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
            all_raw.extend(data.get('data', {}).get('data', []) or [])

    # 分组
    groups = defaultdict(list)
    for m in all_raw:
        key = (m.get('depart_id'), m.get('special_code'),
               m.get('special_name'), m.get('recruit_type_name'))
        groups[key].append(m)

    duplicated = {k: v for k, v in groups.items() if len(v) > 1}
    print(f'\n找到 {len(duplicated)} 组重复\n')

    # 详细对比前 max_check 组
    count = 0
    for key, items in duplicated.items():
        if count >= max_check:
            break
        count += 1
        print(f'--- {key[2]}({key[1]}) @ {key[3]} ---')
        print(f'  共 {len(items)} 条')
        for idx, item in enumerate(items):
            print(f'  [{idx+1}] plan_id={item.get("plan_id")}, '
                  f'recruit_number={item.get("recruit_number")}, '
                  f'remark={item.get("remark", "")[:30]}')
        # 找差异字段
        all_keys = set()
        for item in items:
            all_keys.update(item.keys())
        for k in all_keys:
            values = [item.get(k) for item in items]
            if len(set(str(v) for v in values)) > 1:
                print(f'  ⚠️ 差异字段 [{k}]: {values}')
        print()


if __name__ == '__main__':
    analyze('清华大学', max_check=5)
    analyze('北京大学', max_check=3)
    analyze('浙江大学', max_check=3)