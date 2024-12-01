import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

class SystemLogger:
    def __init__(self):
        # 创建logs目录
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # 设置日志文件名（按日期）
        log_file = f'logs/system_{datetime.now().strftime("%Y%m%d")}.log'
        
        # 创建logger
        self.logger = logging.getLogger('system_logger')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器（限制文件大小和备份数量）
        handler = RotatingFileHandler(
            log_file, 
            maxBytes=10485760,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def log_error(self, message):
        self.logger.error(f"ERROR: {message}")
        
    def log_warning(self, message):
        self.logger.warning(f"WARNING: {message}")
        
    def log_info(self, message):
        self.logger.info(f"INFO: {message}") 