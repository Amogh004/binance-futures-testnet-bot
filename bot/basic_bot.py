import os
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any

from binance import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

from .logging_config import setup_logger

TESTNET_FUTURES_BASE = "https://testnet.binancefuture.com"
FAPI_SUFFIX = "/fapi"

class BasicBot:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = True):
        load_dotenv()
        self.logger = setup_logger()
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("API key/secret missing. Set env BINANCE_API_KEY and BINANCE_API_SECRET or pass to BasicBot.")

        # Initialize python-binance Client
        self.client = Client(self.api_key, self.api_secret, testnet=testnet)
        # Force Futures Testnet base URL (USDT-M)
        self.client.FUTURES_URL = TESTNET_FUTURES_BASE + FAPI_SUFFIX  # e.g., https://testnet.binancefuture.com/fapi
        self.logger.info("Initialized Client for Futures Testnet: %s", self.client.FUTURES_URL)

    # ---------- Validation Helpers ----------
    def _as_decimal(self, value: Any, field: str) -> Decimal:
        try:
            d = Decimal(str(value))
        except (InvalidOperation, TypeError):
            raise ValueError(f"Invalid decimal for {field}: {value}")
        if d <= 0:
            raise ValueError(f"{field} must be > 0")
        return d

    def validate_symbol(self, symbol: str) -> str:
        if not symbol or not symbol.strip():
            raise ValueError("symbol is required")
        symbol = symbol.upper().strip()
        info = self.client.futures_exchange_info()
        valid = any(s['symbol'] == symbol and s['contractType'] == 'PERPETUAL' for s in info['symbols'])
        if not valid:
            raise ValueError(f"Symbol {symbol} not found as USDT-M PERPETUAL on Futures Testnet.")
        return symbol

    def _apply_symbol_filters(self, symbol: str, quantity: Decimal, price: Optional[Decimal]) -> Dict[str, Any]:
        # Enforce exchange filters to reduce common rejections
        info = self.client.futures_exchange_info()
        s = next((x for x in info['symbols'] if x['symbol'] == symbol), None)
        if not s:
            return {}

        params: Dict[str, Any] = {}

        # lot size
        lot = next((f for f in s['filters'] if f['filterType'] == 'LOT_SIZE'), None)
        if lot:
            step = Decimal(lot['stepSize'])
            min_qty = Decimal(lot['minQty'])
            max_qty = Decimal(lot['maxQty'])
            # Quantize quantity down to valid step
            q = (quantity // step) * step
            if q < min_qty:
                raise ValueError(f"qty {quantity} is below minQty {min_qty} for {symbol}")
            if q > max_qty:
                raise ValueError(f"qty {quantity} exceeds maxQty {max_qty} for {symbol}")
            # normalize to remove exponent issues
            params['quantity'] = format(q.normalize(), 'f')

        # price filter
        if price is not None:
            pf = next((f for f in s['filters'] if f['filterType'] == 'PRICE_FILTER'), None)
            if pf:
                tick = Decimal(pf['tickSize'])
                min_price = Decimal(pf['minPrice'])
                max_price = Decimal(pf['maxPrice'])
                p = (price // tick) * tick
                if p < min_price:
                    raise ValueError(f"price {price} is below minPrice {min_price} for {symbol}")
                if p > max_price:
                    raise ValueError(f"price {price} exceeds maxPrice {max_price} for {symbol}")
                params['price'] = format(p.normalize(), 'f')

        return params

    # ---------- Core API ----------
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Any,
        price: Optional[Any] = None,
        time_in_force: str = "GTC",
        stop_price: Optional[Any] = None,
        reduce_only: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        order_type: MARKET | LIMIT | STOP (stop-limit)
        For STOP (Stop-Limit), you must provide stop_price and price.
        """
        side = side.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")

        order_type = order_type.upper()
        if order_type not in {"MARKET", "LIMIT", "STOP"}:
            raise ValueError("order_type must be MARKET, LIMIT, or STOP")

        symbol = self.validate_symbol(symbol)
        qty = self._as_decimal(quantity, "quantity")
        px = self._as_decimal(price, "price") if price is not None and order_type != "MARKET" else None
        spx = self._as_decimal(stop_price, "stop_price") if stop_price is not None else None

        # Validate STOP specifics
        if order_type == "STOP":
            if px is None or spx is None:
                raise ValueError("STOP order requires both price (limit) and stop_price (trigger).")

        params = dict(symbol=symbol, side=side, type=order_type)
        # Apply symbol filters (step/tick)
        filtered = self._apply_symbol_filters(symbol, qty, px)
        params.update(filtered)

        if order_type == "LIMIT":
            params["timeInForce"] = time_in_force
        if order_type == "STOP":
            params["timeInForce"] = time_in_force
            params["stopPrice"] = format(spx.normalize(), 'f')

        if reduce_only is not None:
            params["reduceOnly"] = reduce_only

        self.logger.info("Placing order: %s", params)
        try:
            resp = self.client.futures_create_order(**params)
            self.logger.info("Order placed. Response: %s", resp)
            return resp
        except (BinanceAPIException, BinanceRequestException) as e:
            self.logger.error("Order failed: %s", e)
            # Attach additional data for caller
            raise

    def get_order(self, symbol: str, order_id: Optional[int] = None, client_order_id: Optional[str] = None) -> Dict[str, Any]:
        symbol = self.validate_symbol(symbol)
        try:
            if order_id is not None:
                resp = self.client.futures_get_order(symbol=symbol, orderId=int(order_id))
            elif client_order_id is not None:
                resp = self.client.futures_get_order(symbol=symbol, origClientOrderId=client_order_id)
            else:
                raise ValueError("Provide order_id or client_order_id")
            self.logger.info("Fetched order: %s", resp)
            return resp
        except (BinanceAPIException, BinanceRequestException) as e:
            self.logger.error("Get order failed: %s", e)
            raise

    def ping(self) -> bool:
        try:
            self.client.futures_ping()
            return True
        except Exception as e:
            self.logger.error("Ping failed: %s", e)
            return False
