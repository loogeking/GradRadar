"""
爬虫基类
所有爬虫继承自此类，统一处理：日志、重试、UA轮换、原始数据存档
"""
import time
import random
import logging
import json
from datetime import datetime
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class BaseCrawler:
    """爬虫基类"""

    # 子类必须定义
    source_name = None       # 数据源名称（如 'kaoyan_cn'）

    # UA 池
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    # 请求间隔（秒），子类可覆盖
    request_delay_min = 1.0
    request_delay_max = 2.5

    def __init__(self):
        if not self.source_name:
            raise ValueError(f'{self.__class__.__name__} 必须定义 source_name')

        self.session = self._init_session()
        self.logger = self._init_logger()

        # 原始数据存档目录
        self.raw_dir = BASE_DIR / 'data' / 'raw' / self.source_name
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def _init_session(self):
        """带重试的session"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods=['GET', 'POST'],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _init_logger(self):
        """初始化日志"""
        log_dir = BASE_DIR / 'crawler' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(self.source_name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # 控制台
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(logging.Formatter(
                f'[{self.source_name}] %(asctime)s %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            ))
            logger.addHandler(ch)

            # 文件
            log_file = log_dir / f'{self.source_name}_{datetime.now().strftime("%Y%m%d")}.log'
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setLevel(logging.INFO)
            fh.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s - %(message)s'
            ))
            logger.addHandler(fh)

        return logger

    def request(self, method, url, **kwargs):
        """统一请求方法"""
        headers = kwargs.pop('headers', {})
        headers.setdefault('User-Agent', random.choice(self.USER_AGENTS))

        try:
            response = self.session.request(method, url, headers=headers, timeout=15, **kwargs)
            response.raise_for_status()

            # 礼貌延时
            time.sleep(random.uniform(self.request_delay_min, self.request_delay_max))
            return response
        except Exception as e:
            self.logger.error(f'请求失败 [{method}] {url}: {e}')
            return None

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def save_raw(self, filename, data):
        """保存原始数据"""
        filepath = self.raw_dir / filename
        if isinstance(data, (dict, list)):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif isinstance(data, bytes):
            with open(filepath, 'wb') as f:
                f.write(data)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        self.logger.debug(f'原始数据已保存: {filepath.name}')