"""
kaoyan.cn 主爬虫
"""
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from crawler.base import BaseCrawler
from crawler.pipeline import Pipeline
from crawler.adapters.kaoyan_cn_adapter import KaoyanCnAdapter
from apps.schools.models import School, College
from apps.majors.models import Major


class KaoyanCnSpider(BaseCrawler):
    """掌上考研爬虫"""

    source_name = 'kaoyan_cn'

    BASE_HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.kaoyan.cn",
        "referer": "https://www.kaoyan.cn/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    }

    def __init__(self):
        super().__init__()
        self.pipeline = Pipeline(logger=self.logger)
        self.adapter = KaoyanCnAdapter()

    # ============== 接口1：学校列表 ==============

    def fetch_school_list(self, page=1, limit=20):
        """获取学校列表（单页）"""
        url = "https://api.kaoyan.cn/pc/school/schoolList"
        payload = {
            "page": page,
            "limit": limit,
            "province_id": "",
            "type": "",
            "feature": "syl",     # syl = 双一流
            "school_name": ""
        }
        resp = self.post(url, headers=self.BASE_HEADERS,
                         data=json.dumps(payload, separators=(',', ':')))
        if not resp:
            return None
        return resp.json()

    def crawl_all_schools(self, max_pages=None):
        """
        爬取所有学校并入库
        :param max_pages: 限制最大页数（调试用，None=不限制）
        """
        self.logger.info('=== 开始爬取学校列表 ===')
        page = 1
        total_schools = 0

        while True:
            self.logger.info(f'第 {page} 页...')
            data = self.fetch_school_list(page=page, limit=20)
            if not data or data.get('code') != '0000':
                self.logger.warning(f'第 {page} 页返回异常')
                break

            schools = data.get('data', {}).get('data', []) or []
            if not schools:
                self.logger.info('没有更多学校了')
                break

            # 存原始数据
            self.save_raw(f'schools_page_{page}.json', data)

            # 适配 + 入库
            for raw_school in schools:
                school_data = self.adapter.adapt_school(raw_school)
                if school_data.get('name'):
                    self.pipeline.save_school(school_data)
                    total_schools += 1

            page += 1
            if max_pages and page > max_pages:
                self.logger.info(f'已达到最大页数 {max_pages}，停止')
                break

        self.logger.info(f'=== 学校爬取完成，共处理 {total_schools} 所 ===')

    # ============== 接口2：专业列表 ==============

    def fetch_major_list(self, school_platform_id, page=1, limit=50):
        """获取某学校的专业列表（单页）"""
        url = "https://api.kaoyan.cn/pc/school/planListV2"
        payload = {
            "school_id": str(school_platform_id),
            "recruit_type": "",
            "page": page,
            "limit": limit,
            "keyword": "",
            "is_apply": 2,
            "degree_type": "",
            "first_class": "",
            "second_class": ""
        }
        resp = self.post(url, headers=self.BASE_HEADERS,
                         data=json.dumps(payload, separators=(',', ':')))
        if not resp:
            return None
        return resp.json()

    def crawl_school_majors(self, school):
        """
        爬取某学校所有专业及详情
        :param school: School 对象
        """
        if not school.platform_id:
            self.logger.warning(f'{school.name} 无 platform_id，跳过')
            return

        self.logger.info(f'\n>>> 爬取 {school.name}(平台ID={school.platform_id}) 的专业')
        page = 1
        total = 0
        plan_ids = []  # 收集 plan_id 用于详情接口

        while True:
            data = self.fetch_major_list(school.platform_id, page=page, limit=50)
            if not data or data.get('code') != '0000':
                self.logger.warning(f'  第 {page} 页返回异常')
                break

            majors = data.get('data', {}).get('data', []) or []
            if not majors:
                break

            # 存原始数据
            self.save_raw(f'majors_{school.platform_id}_p{page}.json', data)

            for raw_major in majors:
                # 1. 学院
                college_data = self.adapter.adapt_college(raw_major)
                if not college_data:
                    # 无学院信息，跳过该专业
                    continue
                college = self.pipeline.save_college(school, college_data)
                if not college:
                    continue

                # 2. 专业
                major_data = self.adapter.adapt_major(raw_major)
                major = self.pipeline.save_major(college, major_data)
                if not major:
                    continue

                total += 1

                # 收集 plan_id 备用
                plan_id = raw_major.get('plan_id')
                if plan_id:
                    plan_ids.append((plan_id, major.id))

                # 3. 招生计划（基础信息：年份+招生人数）
                year = raw_major.get('year')
                recruit_number = raw_major.get('recruit_number')
                if year and recruit_number is not None:
                    self.pipeline.save_enrollment(major, {
                        'year': year,
                        'plan_total': recruit_number,
                        'plan_id': plan_id,
                    })

            page += 1

        self.logger.info(f'<<< {school.name} 完成，处理 {total} 个专业')
        return plan_ids

    # ============== 接口3：专业详情 ==============

    def fetch_major_detail(self, plan_id):
        """获取专业详情"""
        url = "https://api.kaoyan.cn/pc/school/planDetailV2"
        payload = {
            "plan_id": str(plan_id),
            "is_apply": 2
        }
        resp = self.post(url, headers=self.BASE_HEADERS,
                         data=json.dumps(payload, separators=(',', ':')))
        if not resp:
            return None
        return resp.json()

    def crawl_major_details(self, plan_id_major_pairs):
        """
        爬取专业详情（含研究方向、参考书、评级）
        :param plan_id_major_pairs: [(plan_id, major_id), ...]
        """
        self.logger.info(f'\n>>> 爬取 {len(plan_id_major_pairs)} 个专业的详情')

        for plan_id, major_id in plan_id_major_pairs:
            try:
                major = Major.objects.select_related('college__school').get(id=major_id)
            except Major.DoesNotExist:
                continue

            data = self.fetch_major_detail(plan_id)
            if not data or data.get('code') != '0000':
                continue

            detail = data.get('data', {})
            if not detail:
                continue

            # 存原始数据
            self.save_raw(f'detail_{plan_id}.json', data)

            # 1. 研究方向
            directions = self.adapter.adapt_research_directions(detail)
            for d in directions:
                self.pipeline.save_research_direction(major, d)

            # 2. 参考书
            books = self.adapter.adapt_reference_books(detail)
            for b in books:
                self.pipeline.save_reference_book(major, b)

            # 3. 学科评级
            rating = self.adapter.adapt_subject_rating(detail)
            if rating:
                self.pipeline.save_subject_rating(major.college.school, rating)

            # 4. 学位点（更新到 Major）
            doctoral = detail.get('doctoral_point')
            if doctoral:
                doctoral_key = self.adapter.DOCTORAL_POINT_MAP.get(doctoral, '')
                if doctoral_key and major.doctoral_point != doctoral_key:
                    major.doctoral_point = doctoral_key
                    major.save(update_fields=['doctoral_point'])

        self.logger.info('<<< 专业详情爬取完成')

    # ============== 接口4：分数线 ==============

    def fetch_score_lines(self, school_platform_id, year):
        """获取学校某年所有分数线"""
        url = "https://api.kaoyan.cn/pc/school/schoolScore"
        payload = {
            "school_id": str(school_platform_id),
            "year": year,
            "degree_type": ""
        }
        resp = self.post(url, headers=self.BASE_HEADERS,
                         data=json.dumps(payload, separators=(',', ':')))
        if not resp:
            return None
        return resp.json()

    def crawl_school_score_lines(self, school, years=None):
        """
        爬取某学校多年分数线
        :param years: 年份列表，None=默认近3年
        """
        if not school.platform_id:
            return
        if years is None:
            years = [2026, 2025, 2024]

        self.logger.info(f'\n>>> 爬取 {school.name} 的分数线（年份: {years}）')

        for year in years:
            data = self.fetch_score_lines(school.platform_id, year)
            if not data or data.get('code') != '0000':
                continue

            score_list = data.get('data', []) or []
            if not score_list:
                continue

            # 存原始
            self.save_raw(f'score_{school.platform_id}_{year}.json', data)

            # 适配
            adapted = self.adapter.adapt_score_lines(score_list, year, school)

            # 入库
            for item in adapted:
                if item['score_type'] == 'major':
                    # 专业线：根据专业代码 + 学院ID 找 Major
                    raw_code = item.pop('_raw_code', None)
                    raw_depart_id = item.pop('_raw_depart_id', None)
                    if not raw_code:
                        continue
                    qs = Major.objects.filter(
                        college__school=school,
                        code=raw_code
                    )
                    if raw_depart_id:
                        qs = qs.filter(college__platform_id=raw_depart_id)
                    major = qs.first()
                    if not major:
                        self.logger.debug(f'找不到专业: code={raw_code}, depart_id={raw_depart_id}')
                        continue
                    item['major_obj'] = major

                self.pipeline.save_score_line(item)

        self.logger.info(f'<<< {school.name} 分数线爬取完成')

    # ============== 综合入口 ==============

    def run(self, mode='full', school_names=None, years=None, max_school_pages=None):
        """
        执行爬取
        :param mode:
            'schools_only'  : 只爬学校列表
            'majors_only'   : 爬指定学校的专业
            'scores_only'   : 爬指定学校的分数线
            'full'          : 完整流程（学校→专业→详情→分数线）
        :param school_names: 指定学校名列表（不指定则全部）
        :param years: 分数线年份
        :param max_school_pages: 学校列表最大页数（调试用）
        """
        self.logger.info(f'\n{"=" * 60}\n开始爬取，模式: {mode}\n{"=" * 60}')

        if mode in ('schools_only', 'full'):
            self.crawl_all_schools(max_pages=max_school_pages)

        if mode in ('majors_only', 'full'):
            schools = School.objects.filter(platform_id__isnull=False)
            if school_names:
                schools = schools.filter(name__in=school_names)

            for school in schools:
                plan_pairs = self.crawl_school_majors(school) or []
                # 爬完专业立刻爬详情
                if plan_pairs:
                    self.crawl_major_details(plan_pairs)

        if mode in ('scores_only', 'full'):
            schools = School.objects.filter(platform_id__isnull=False)
            if school_names:
                schools = schools.filter(name__in=school_names)

            for school in schools:
                self.crawl_school_score_lines(school, years=years)

        self.pipeline.print_stats()


if __name__ == '__main__':
    spider = KaoyanCnSpider()
    # 测试：只爬一页学校
    spider.run(mode='schools_only', max_school_pages=1)