"""
kaoyan.cn 数据适配器
负责把平台 API 返回的原始 JSON 转换为标准化的数据库友好格式
"""


class KaoyanCnAdapter:
    """掌上考研数据适配器"""

    # 学校类型映射
    SCHOOL_TYPE_MAP = {
        '综合类': 'comprehensive',
        '理工类': 'science_eng',
        '师范类': 'normal_edu',
        '医药类': 'medical',
        '财经类': 'finance',
        '政法类': 'political_law',
        '农林类': 'agriculture',
        '民族类': 'ethnic',
        '艺术类': 'art',
        '军事类': 'military',
        '语言类': 'language',
        '体育类': 'sports',
    }

    # 学位类型映射（平台 1=专硕 2=学硕；我们 academic=学硕 professional=专硕）
    DEGREE_TYPE_MAP = {
        1: 'professional',
        2: 'academic',
    }

    # 学习方式映射
    LEARNING_TYPE_MAP = {
        '全日制': 'full_time',
        '非全日制': 'part_time',
    }

    # 考试类型映射
    EXAM_TYPE_MAP = {
        '统考': 'unified',
        '单考': 'single',
        '联考': 'joint',
        '管理类联考': 'management',
        '推免': 'recommend',
    }

    # 学位点映射
    DOCTORAL_POINT_MAP = {
        '一级学科博士点': 'doctoral_first',
        '二级学科博士点': 'doctoral_second',
        '博士点': 'doctoral',
        '硕士点': 'master',
        '无': 'none',
    }

    # ============== 学校 ==============

    @classmethod
    def adapt_school(cls, raw):
        """
        平台学校数据 → 数据库格式
        输入：单个学校的 dict（来自 schoolList 接口）
        """
        return {
            'name': raw.get('school_name'),
            'platform_id': raw.get('school_id'),
            'province_name': raw.get('province_name'),
            'province_area': raw.get('province_area', ''),
            # 平台 1=是 2=否
            'is_985': raw.get('is_985') == 1,
            'is_211': raw.get('is_211') == 1,
            'is_double_first': raw.get('syl') == 1,  # syl=双一流
            'is_self_scoring': raw.get('is_zihuaxian') == 1,
            'school_type': cls.SCHOOL_TYPE_MAP.get(raw.get('type_name', ''), ''),
            # 自动判断层次
            'level': cls._infer_school_level(raw),
        }

    @staticmethod
    def _infer_school_level(raw):
        if raw.get('is_985') == 1:
            return '985'
        if raw.get('is_211') == 1:
            return '211'
        if raw.get('syl') == 1:
            return 'double_first'
        return 'normal'

    # ============== 学院 ==============

    @classmethod
    def adapt_college(cls, raw):
        """
        从专业列表项里抽取学院信息
        输入：planListV2 接口返回的单条专业 dict
        """
        depart_id = raw.get('depart_id')
        # depart_id=0 表示"不区分院系"，不当作真实学院
        if not depart_id or depart_id == 0:
            return None
        return {
            'name': raw.get('depart_name'),
            'platform_id': depart_id,
        }

    # ============== 专业 ==============

    @classmethod
    def adapt_major(cls, raw):
        """
        从专业列表项 → 数据库格式
        输入：planListV2 接口的单条 dict
        """
        # 学科归属：优先用一级学科代码(level2_code)，没有时用门类代码
        subject_code = raw.get('level2_code') or raw.get('level1_code')
        subject_name = raw.get('level2_name') or raw.get('level1_name')

        return {
            'code': raw.get('special_code'),
            'name': raw.get('special_name'),
            'degree_type': cls.DEGREE_TYPE_MAP.get(raw.get('degree_type'), 'academic'),
            'learning_type': cls.LEARNING_TYPE_MAP.get(raw.get('recruit_type_name'), 'full_time'),
            'exam_type': cls.EXAM_TYPE_MAP.get(raw.get('exam_class_name'), 'unified'),
            'platform_id': raw.get('spe_id'),
            'subject_category_code': subject_code,
            'subject_category_name': subject_name,  # 新增：学科名称
        }

    # ============== 研究方向 ==============

    @classmethod
    def adapt_research_directions(cls, raw_detail):
        """
        从专业详情接口的 research_area_data 里抽取所有研究方向（多年份）
        输入：planDetailV2 接口的完整 dict
        返回：list of dict
        """
        results = []
        area_data = raw_detail.get('research_area_data', {}) or {}

        for year_str, directions in area_data.items():
            try:
                year = int(year_str)
            except (ValueError, TypeError):
                continue

            for d in directions or []:
                raw_text = d.get('research_area', '')
                direction_code, direction_name = cls._parse_direction(raw_text)
                if not direction_name:
                    continue

                results.append({
                    'year': year,
                    'direction_code': direction_code,
                    'direction_name': direction_name,
                    'raw_text': raw_text,
                    'recruit_number': d.get('recruit_number'),
                    'is_direction_based': d.get('is_statistic_direction') == 1,
                    'exam_subjects': d.get('exam_subject', ''),
                    'note': d.get('note', ''),
                })
        return results

    @staticmethod
    def _parse_direction(raw_text):
        """
        解析方向文本，提取 code 和 name
        例：'（01）马克思主义哲学' → ('01', '马克思主义哲学')
            '01（全日制）马克思主义哲学' → ('01', '马克思主义哲学')
            '01马克思主义哲学' → ('01', '马克思主义哲学')
            '马克思主义哲学' → ('', '马克思主义哲学')
        """
        import re
        if not raw_text:
            return '', ''
        text = raw_text.strip()

        # 模式1：（XX）名称
        m = re.match(r'^[（(](\d+)[）)]\s*(.+)$', text)
        if m:
            return m.group(1), m.group(2).strip()

        # 模式2：XX名称  或  XX（其他描述）名称
        m = re.match(r'^(\d+)\s*[（(]?[^）)]*[）)]?\s*(.+)$', text)
        if m and len(m.group(1)) <= 3:
            name_part = m.group(2).strip()
            # 去掉前面可能残留的括号
            name_part = re.sub(r'^[（(][^）)]*[）)]\s*', '', name_part)
            return m.group(1), name_part

        return '', text

    # ============== 参考书 ==============

    @classmethod
    def adapt_reference_books(cls, raw_detail):
        """
        从专业详情接口提取参考书
        输入：planDetailV2 完整 dict
        返回：list of dict
        """
        exam_book = raw_detail.get('exam_book', '')
        year = raw_detail.get('exam_book_year')
        if not exam_book:
            return []

        # 简单处理：整段存为一条原始文本
        # 解析具体书目是个复杂的活，先用 raw_text 兜底
        return [{
            'book_name': '参考书目（汇总）',
            'year': year,
            'raw_text': exam_book.replace('<br/>', '\n').replace('<br>', '\n'),
            'exam_subject': '初试综合',
        }]

    # ============== 学科评级 ==============

    @classmethod
    def adapt_subject_rating(cls, raw_detail):
        """
        从专业详情提取本校在该学科的评级
        """
        rating = raw_detail.get('major_rate')
        if not rating:
            return None

        subject_code = raw_detail.get('level2_code') or raw_detail.get('level1_code')
        subject_name = raw_detail.get('level2_name') or raw_detail.get('level1_name')
        if not subject_code:
            return None

        return {
            'subject_code': subject_code,
            'subject_name': subject_name,  # 新增
            'rating': rating,
            'evaluation_round': 'round_4',
        }

    # ============== 分数线 ==============

    @classmethod
    def adapt_score_lines(cls, raw_score_list, year, school_obj):
        """
        分数线接口返回的 list → 标准化分数线数据
        """
        results = []
        for raw in raw_score_list or []:
            data_type = raw.get('data_type')
            code = raw.get('code', '')

            if data_type == 'score_level':
                score_type = 'subject'
                subject_category_code = code
                subject_category_name = raw.get('name', '')  # 学科名
            elif data_type == 'school_score':
                score_type = 'major'
                subject_category_code = None
                subject_category_name = None
            else:
                continue

            total = raw.get('total')
            if total is None or total == 0:
                continue

            result = {
                'score_type': score_type,
                'school_obj': school_obj,
                'year': year,
                'total_score': total,
                'politics_score': cls._safe_int(raw.get('politics')),
                'english_score': cls._safe_int(raw.get('english')),
                'subject_one_score': cls._safe_int(raw.get('special_one')),
                'subject_two_score': cls._safe_int(raw.get('special_two')),
                'diff_total': cls._safe_int(raw.get('diff_total')),
                'diff_politics': cls._safe_int(raw.get('diff_politics')),
                'diff_english': cls._safe_int(raw.get('diff_english')),
                'diff_subject_one': cls._safe_int(raw.get('diff_special_one')),
                'diff_subject_two': cls._safe_int(raw.get('diff_special_two')),
                'note': raw.get('note', '') or raw.get('special_remark', ''),
            }

            if score_type == 'subject':
                result['subject_category_code'] = subject_category_code
                result['subject_category_name'] = subject_category_name  # 新增
            else:
                result['_raw_code'] = code
                result['_raw_depart_id'] = raw.get('depart_id')

            results.append(result)
        return results

    @staticmethod
    def _safe_int(value):
        """安全转 int，0 视为 None（表示不考）"""
        if value is None:
            return None
        try:
            v = int(value)
            return v if v > 0 else None
        except (ValueError, TypeError):
            return None