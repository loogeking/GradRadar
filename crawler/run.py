"""
爬虫执行入口

用法：
    python crawler/run.py --source kaoyan_cn --mode schools_only --max-pages 1
    python crawler/run.py --source kaoyan_cn --mode majors_only --schools 清华大学 北京大学
    python crawler/run.py --source kaoyan_cn --mode scores_only --schools 清华大学 --years 2024 2025 2026
    python crawler/run.py --source kaoyan_cn --mode full --schools 清华大学
"""
import argparse
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()


def run_kaoyan_cn(args):
    from crawler.spiders.kaoyan_cn_spider import KaoyanCnSpider
    spider = KaoyanCnSpider()
    spider.run(
        mode=args.mode,
        school_names=args.schools,
        years=args.years,
        max_school_pages=args.max_pages,
    )


SOURCES = {
    'kaoyan_cn': run_kaoyan_cn,
}


def main():
    parser = argparse.ArgumentParser(description='GradRadar 爬虫')
    parser.add_argument('--source', type=str, required=True,
                        choices=list(SOURCES.keys()),
                        help='数据源')
    parser.add_argument('--mode', type=str, default='full',
                        choices=['schools_only', 'majors_only', 'scores_only', 'full'],
                        help='爬取模式')
    parser.add_argument('--schools', nargs='+', default=None,
                        help='指定学校名（多个用空格分隔）')
    parser.add_argument('--years', nargs='+', type=int, default=None,
                        help='分数线年份')
    parser.add_argument('--max-pages', type=int, default=None,
                        help='学校列表最大页数（调试用）')

    args = parser.parse_args()
    SOURCES[args.source](args)


if __name__ == '__main__':
    main()