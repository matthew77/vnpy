import multiprocessing
from time import sleep
from datetime import datetime, time
from logging import INFO

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine

from vnpy.gateway.oanda import OandaGateway
# from vnpy.gateway.ctp import CtpGateway
# from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True


ctp_setting = {
    "用户名": "",
    "密码": "",
    "经纪商代码": "",
    "交易服务器": "",
    "行情服务器": "",
    "产品名称": "",
    "授权编码": "",
    "产品信息": ""
}

if __name__ == "__main__":
    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(OandaGateway)
    # cta_engine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    main_engine.connect(ctp_setting, "CTP")
    main_engine.write_log("连接CTP接口")

    sleep(10)

    # cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    # cta_engine.init_all_strategies()
    sleep(60)   # Leave enough time to complete strategy initialization
    main_engine.write_log("CTA策略全部初始化")

    # cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")

    while True:
        sleep(1)
