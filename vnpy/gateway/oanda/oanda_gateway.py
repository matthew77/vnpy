""" gateway for Oanda """
from vnpy.trader.gateway import BaseGateway
from vnpy.api.rest import RestClient, Request

from vnpy.trader.constant import (
    Direction,
    Exchange,
    OrderType,
    Product,
    Status,
    Offset,
    Interval
)
from vnpy.trader.object import (
    TickData,
    OrderData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    BarData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
    HistoryRequest
)


__author__ = "ZHANG Liang"
__email__ = "zhangliang@keepswalking.com"

# hostname: api-fxpractice.oanda.com
# streaming_hostname: stream-fxpractice.oanda.com
# port: 443
# ssl: true
# token:  43ca7cd61a62 521dcfeaae762f0
# username: keepa test
# datetime_format: RFC3339
# accounts:
# - 101-01 455-001
# active_account: 101- 55-001

REST_HOST = "https://api-fxtrade.oanda.com"
STREAMING_HOST = "https://stream-fxtrade.oanda.com"

PRACTICE_REST_HOST = "https://api-fxpractice.oanda.com"
PRACTICE_STREAMING_HOST = "https://stream-fxpractice.oanda.com"


class OandaGateway(BaseGateway):
    """
    VN Trader Gateway for Oanda connection
    """
    default_setting = {

        "API Key": "",
        "会话数": 3,
        "服务器": ["REAL", "PRACTICE"],
        "代理地址": "",
        "代理端口": "",
    }

    exchanges = [Exchange.OANDA]

    def __init__(self, event_engine):
        """ constructor """
        super(OandaGateway, self).__init__(event_engine, "OANDA")

        self.rest_api = OandaRestApi(self)

    def connect(self, setting: dict):
        key = setting["API Key"]
        # secret = setting["Secret"]
        session_number = setting["会话数"]
        server = setting["服务器"]
        proxy_host = setting["代理地址"]
        proxy_port = setting["代理端口"]

        if proxy_port.isdigit():
            proxy_port = int(proxy_port)
        else:
            proxy_port = 0

        self.rest_api.connect(key, session_number,
                              proxy_host, proxy_port)

    def subscribe(self, req: SubscribeRequest):
        """"""
        # ??? no web socket, use streaming ???
        pass

    def send_order(self, req: OrderRequest):
        """"""
        pass

    def cancel_order(self, req: CancelRequest):
        """"""
        pass

    def query_account(self):
        """"""
        pass

    def query_position(self):
        """"""
        pass

    def query_history(self, req: HistoryRequest):
        """"""
        return self.rest_api.query_history(req)

    def close(self):
        """"""
        self.rest_api.stop()



class OandaRestApi(RestClient):
    """ Oanda REST API """
    def __init__(self, gateway: BaseGateway):
        super().__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name

    def sign(self, request):
        # ??? 将key加入到 request ？？？
        pass

    def on_failed(self, status_code: int, request: Request):
        pass

    def on_error(
            self,
            exception_type: type,
            exception_value: Exception,
            tb,
            request: Request
    ):
        pass








# TODO: how to use streaming part ???