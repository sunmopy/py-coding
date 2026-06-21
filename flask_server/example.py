from flask import Flask, request
from utils import init_logger, RequestLogger, logger

app = Flask(__name__)


@app.before_request
def before_request():
    """
    请求前置钩子：在每个请求进入时初始化日志上下文
    """
    # 从请求中获取参数
    query_params = request.args.to_dict()
    sn = request.args.get('sn', '')
    round_num = request.args.get('round', type=int)
    
    # 将RequestLogger实例存储到请求上下文中
    request.logger = RequestLogger(
        query=query_params,
        sn=sn,
        round_num=round_num
    )


@app.route('/api/test')
def test_endpoint():
    """
    示例接口：展示日志使用方式
    """
    req_logger = request.logger
    
    # 使用请求级别的日志记录器
    req_logger.debug("这是一个debug日志（INFO级别不会打印）")
    req_logger.info("这是一个info日志")
    req_logger.warning("这是一个warning日志")
    
    # 打印字典和列表（JSON格式）
    req_logger.info({"name": "张三", "age": 18})
    req_logger.info([1, 2, 3])
    
    return {"status": "success"}


if __name__ == '__main__':
    # 方式1：使用配置文件（推荐）
    init_logger(config_path="config/log_config.yaml")
    
    # 方式2：使用默认配置（配置文件不存在时自动使用）
    # init_logger()
    
    # 方式3：函数参数覆盖配置文件
    # init_logger(
    #     config_path="config/log_config.yaml",
    #     log_level="DEBUG",  # 覆盖配置文件中的级别
    # )
    
    # 全局日志（非请求上下文）
    logger.info("应用启动中...")
    logger.info("日志系统已初始化")
    
    app.run(host='0.0.0.0', port=5000, debug=True)