""" gateway for Oanda """
from datetime import datetime

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

ORDER_TYPE_OANDA_TO_VNPY = {
    "MARKET": OrderType.MARKET,
    "FIXED_PRICE": OrderType.LIMIT,
    "LIMIT": OrderType.LIMIT,
    "STOP": OrderType.STOP,
    "MARKET_IF_TOUCHED": OrderType.MARKET,
    "TAKE_PROFIT": OrderType.LIMIT,
    "STOP_LOSS": OrderType.STOP,
    "TRAILING_STOP_LOSS": OrderType.STOP
}

STATUS_OANDA_TO_VNPY = {
    "PENDING": Status.SUBMITTING,
    "FILLED": Status.ALLTRADED,
    "CANCELLED": Status.CANCELLED,
    "TRIGGERED": Status.SUBMITTING
}


class OandaGateway(BaseGateway):
    """
    VN Trader Gateway for Oanda connection
    """
    default_setting = {

        "Account ID":"",
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
        account_id = setting["Account ID"]
        key = setting["API Key"]
        session_number = setting["会话数"]
        server = setting["服务器"]
        proxy_host = setting["代理地址"]
        proxy_port = setting["代理端口"]

        if proxy_port.isdigit():
            proxy_port = int(proxy_port)
        else:
            proxy_port = 0

        self.rest_api.connect(account_id, key, session_number,
                              server, proxy_host, proxy_port)

    def subscribe(self, req: SubscribeRequest):
        """"""
        # ??? no web socket, use streaming ???
        self.rest_api.subscribe(req)

    def send_order(self, req: OrderRequest):
        """"""
        return self.rest_api.send_order(req)

    def cancel_order(self, req: CancelRequest):
        """"""
        self.rest_api.cancel_order(req)

    def query_account(self):
        """"""
        # ??? not sure Oanda has the api
        self.rest_api.query_account_balance()

    def query_position(self):
        """"""
        # ??? not sure Oanda has the api
        self.rest_api.query_position()

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

        self.key = ""
        self.account_id = ""

    def sign(self, request):
        # for Oanda rest request, just use Bearer token in the HTTP Authorization header
        headers = {
            'Authorization': "Bearer {}".format(self.key)
        }
        request.headers = headers
        return request

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

    def connect(self,
                account_id: str,
                key: str,
                session_number: int,
                base_url: str,
                proxy_host: str,
                proxy_port: int
                ):
        self.key = key
        self.account_id = account_id
        self.init(base_url, proxy_host, proxy_port)
        self.start(session_number)
        self.gateway.write_log("REST API启动成功")
        self.query_contract()   # instrument
        self.query_account()
        self.query_position()
        self.query_order()

    def query_contract(self):
        """ oanda instruments """
        self.add_request(
            method="GET",
            path="/v3/accounts/{}/instruments".format(self.account_id),
            callback=self.on_query_contract
        )

    def on_query_contract(self, data, request: Request):
        """ callback function for query instruments
            get tradeable instruments from the account  """
        for d in data["instruments"]:
            symbol = d["name"]

            if d["type"] == 'CFD' or d["type"] == 'METAL':
                product = Product.CFD
            else:
                product = Product.FOREX

            pip_location = int(d["pipLocation"])    # Oanda use "pipLocation": -4, so will need to convert to decimal.

            contract = ContractData(
                symbol=symbol,
                exchange=Exchange.OANDA,
                name=symbol,
                product=product,
                size=1,
                pricetick=float(10 ** pip_location),
                gateway_name=self.gateway_name
            )
            self.gateway.on_contract(contract)

        self.gateway.write_log("合约信息查询成功")

    def query_account(self):
        self.add_request(
            method="GET",
            path="/v3/accounts/{}".format(self.account_id),
            callback=self.on_query_account
        )

    def on_query_account(self, data, request):
        account = AccountData(
            accountid=self.account_id,
            balance=float(data["balance"]),
            gateway_name=self.gateway_name
        )
        self.gateway.on_account(account)

    def query_position(self):
        self.add_request(
            method="GET",
            path="/v3/accounts/{}/openPositions".format(self.account_id),
            callback=self.on_query_position
        )

    def on_query_position(self, data, request):
        positions = data["positions"]
        for pos in positions:
            symbol = pos["instrument"]
            long_pos = pos["long"]
            if long_pos["units"] != "0":
                direction = Direction.LONG
                volume = int(long_pos["units"])
                avg_price = float(long_pos["averagePrice"])
                pnl = float(long_pos["pl"]) + float(long_pos["unrealizedPL"])
                position = PositionData(
                    symbol=symbol,
                    exchange=Exchange.OANDA,
                    direction=direction,
                    volume=volume,
                    price=avg_price,
                    pnl=pnl,
                    gateway_name=self.gateway_name,
                )
                self.gateway.on_position(position)
            short_pos = pos["short"]
            if short_pos["units"] != "0":
                direction = Direction.SHORT
                volume = int(long_pos["units"])
                avg_price = float(long_pos["averagePrice"])
                pnl = float(long_pos["pl"]) + float(long_pos["unrealizedPL"])
                position = PositionData(
                    symbol=symbol,
                    exchange=Exchange.OANDA,
                    direction=direction,
                    volume=volume,
                    price=avg_price,
                    pnl=pnl,
                    gateway_name=self.gateway_name,
                )
                self.gateway.on_position(position)

    def query_order(self):
        self.add_request(
            method="GET",
            path="/v3/accounts/{}/orders".format(self.account_id),
            callback=self.on_query_order
        )

    def on_query_order(self, data, request):
        for d in data["orders"]:
            dt = datetime.fromtimestamp(d["time"] / 1000)
            time = dt.strftime("%Y-%m-%d %H:%M:%S")

            order = OrderData(
                orderid=d["id"],
                symbol=d["instrument"],
                exchange=Exchange.OANDA,
                price=float(d["price"]),
                volume=float(d["units"]),
                type=ORDER_TYPE_OANDA_TO_VNPY[d["type"]],
                direction=Direction.LONG if float(d["units"]) > 0 else Direction.SHORT,
                # traded=float(d["executedQty"]),
                status=STATUS_OANDA_TO_VNPY.get(d["state"], None),
                time=time,
                gateway_name=self.gateway_name,
            )
            self.gateway.on_order(order)

        self.gateway.write_log("委托信息查询成功")

