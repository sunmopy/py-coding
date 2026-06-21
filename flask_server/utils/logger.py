import os
import sys
import json
import yaml
from typing import Optional, Dict, Any, Union
from loguru import logger as loguru_logger


class RequestLogger:
    """
    请求级别日志记录器
    
    在HTTP请求进入时初始化，绑定请求上下文（query参数、sn、轮次等）
    后续调用日志方法时自动携带这些上下文信息
    """
    
    def __init__(
        self,
        query: Optional[Dict[str, Any]] = None,
        sn: Optional[str] = "",
        round_num: Optional[int] = None,
    ):
        """
        初始化请求日志记录器
        
        :param query: 请求的query参数字典
        :param sn: 序列号
        :param round_num: 轮次
        """
        self.query = query or {}
        self.sn = sn or ""
        self.round_num = str(round_num) if round_num is not None else ""
    
    def _format_context(self) -> str:
        """
        格式化上下文信息：sn|轮次|query
        使用 JSON 序列化 query，确保可被 json.loads 解析
        """
        # 使用 json.dumps 序列化 query，确保输出标准 JSON 格式
        query_str = json.dumps(self.query, ensure_ascii=False)
        # 转义换行符，确保单行输出
        query_str = query_str.replace("\n", "\\n")
        return f"{self.sn}|{self.round_num}|{query_str}"
    
    def _format_message(self, message: Any) -> str:
        """
        格式化消息内容，处理各种类型并转义换行符
        dict/list 使用 JSON 序列化，确保可被 json.loads 解析
        """
        if isinstance(message, str):
            msg_str = message
        elif isinstance(message, (dict, list)):
            # dict/list 使用 JSON 序列化，ensure_ascii=False 支持中文
            msg_str = json.dumps(message, ensure_ascii=False)
        else:
            msg_str = str(message)
        # 转义换行符，确保单行输出
        return msg_str.replace("\n", "\\n")
    
    def trace(self, message: Union[str, dict, list, Any], **kwargs):
        context = self._format_context()
        msg = self._format_message(message)
        loguru_logger.trace(context + "|" + msg, **kwargs)
    
    def debug(self, message: Union[str, dict, list, Any], **kwargs):
        context = self._format_context()
        msg = self._format_message(message)
        loguru_logger.debug(context + "|" + msg, **kwargs)
    
    def info(self, message: Union[str, dict, list, Any], **kwargs):
        context = self._format_context()
        msg = self._format_message(message)
        loguru_logger.info(context + "|" + msg, **kwargs)
    
    def warning(self, message: Union[str, dict, list, Any], **kwargs):
        context = self._format_context()
        msg = self._format_message(message)
        loguru_logger.warning(context + "|" + msg, **kwargs)
    
    def error(self, message: Union[str, dict, list, Any], **kwargs):
        context = self._format_context()
        msg = self._format_message(message)
        loguru_logger.error(context + "|" + msg, **kwargs)
    
    def critical(self, message: Union[str, dict, list, Any], **kwargs):
        context = self._format_context()
        msg = self._format_message(message)
        loguru_logger.critical(context + "|" + msg, **kwargs)


class GlobalLogger:
    """
    全局日志记录器
    
    用于非请求上下文的日志记录，不携带请求相关信息
    """
    
    @staticmethod
    def _format_message(message: Any) -> str:
        """
        格式化消息内容，处理各种类型并转义换行符
        dict/list 使用 JSON 序列化，确保可被 json.loads 解析
        """
        if isinstance(message, str):
            msg_str = message
        elif isinstance(message, (dict, list)):
            msg_str = json.dumps(message, ensure_ascii=False)
        else:
            msg_str = str(message)
        return msg_str.replace("\n", "\\n")
    
    @staticmethod
    def trace(message: Union[str, dict, list, Any], **kwargs):
        msg = GlobalLogger._format_message(message)
        loguru_logger.trace("|||" + msg, **kwargs)
    
    @staticmethod
    def debug(message: Union[str, dict, list, Any], **kwargs):
        msg = GlobalLogger._format_message(message)
        loguru_logger.debug("|||" + msg, **kwargs)
    
    @staticmethod
    def info(message: Union[str, dict, list, Any], **kwargs):
        msg = GlobalLogger._format_message(message)
        loguru_logger.info("|||" + msg, **kwargs)
    
    @staticmethod
    def warning(message: Union[str, dict, list, Any], **kwargs):
        msg = GlobalLogger._format_message(message)
        loguru_logger.warning("|||" + msg, **kwargs)
    
    @staticmethod
    def error(message: Union[str, dict, list, Any], **kwargs):
        msg = GlobalLogger._format_message(message)
        loguru_logger.error("|||" + msg, **kwargs)
    
    @staticmethod
    def critical(message: Union[str, dict, list, Any], **kwargs):
        msg = GlobalLogger._format_message(message)
        loguru_logger.critical("|||" + msg, **kwargs)


# 默认日志配置
DEFAULT_CONFIG = {
    "log_level": "INFO",
    "console_output": True,
    "file_output": {
        "enabled": True,
        "path": "logs/app.log",
        "rotation": "100 MB",
        "retention": "7 days",
        "compression": "zip"
    }
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载日志配置文件（支持 YAML 格式）
    
    :param config_path: 配置文件路径，None 则使用默认配置
    :return: 配置字典
    """
    if config_path is None:
        return DEFAULT_CONFIG.copy()
    
    if not os.path.exists(config_path):
        print(f"[Logger] 配置文件不存在: {config_path}，使用默认配置")
        return DEFAULT_CONFIG.copy()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def init_logger(
    config_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    console_output: Optional[bool] = None,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
):
    """
    初始化日志配置
    
    优先级：函数参数 > 配置文件 > 默认配置
    
    :param config_path: 配置文件路径（如 "config/log_config.yaml"）
    :param config: 配置字典，与 config_path 二选一
    :param log_level: 日志级别（TRACE/DEBUG/INFO/WARNING/ERROR/CRITICAL）
    :param log_file: 日志文件路径，None表示不输出到文件
    :param console_output: 是否输出到控制台
    :param rotation: 文件轮换大小（如 "100 MB", "1 day"）
    :param retention: 日志保留时间（如 "7 days"）
    """
    # 加载配置
    if config is None:
        config = load_config(config_path)
    
    # 函数参数覆盖配置文件
    final_log_level = log_level if log_level is not None else config.get("log_level", "INFO")
    final_console_output = console_output if console_output is not None else config.get("console_output", True)
    
    # 文件输出配置
    file_config = config.get("file_output", {})
    final_log_file = log_file if log_file is not None else (
        file_config.get("path") if file_config.get("enabled", True) else None
    )
    final_rotation = rotation if rotation is not None else file_config.get("rotation", "100 MB")
    final_retention = retention if retention is not None else file_config.get("retention", "7 days")
    final_compression = file_config.get("compression", "zip")
    
    # 清除默认处理器
    loguru_logger.remove()
    
    # 定义日志格式：时间|sn|轮次|query|消息
    log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS}|{message}"
    
    # 添加控制台输出
    if final_console_output:
        loguru_logger.add(
            sys.stderr,
            format=log_format,
            level=final_log_level,
            colorize=True,
        )
    
    # 添加文件输出
    if final_log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(final_log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        loguru_logger.add(
            final_log_file,
            format=log_format,
            level=final_log_level,
            rotation=final_rotation,
            retention=final_retention,
            compression=final_compression,
        )


# 全局日志实例（用于非请求上下文）
logger = GlobalLogger()
