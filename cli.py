import argparse
import json
import sys
import time
from decimal import Decimal
from bot.basic_bot import BasicBot


def place_order(args):
    bot = BasicBot()
    try:
        resp = bot.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.qty,
            price=args.price,
            time_in_force=args.timeInForce,
            stop_price=args.stopPrice,
            reduce_only=args.reduceOnly
        )
        print(json.dumps({"ok": True, "data": resp}, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


def order_status(args):
    bot = BasicBot()
    try:
        resp = bot.get_order(symbol=args.symbol, order_id=args.orderId, client_order_id=args.clientOrderId)
        print(json.dumps({"ok": True, "data": resp}, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


# ---------------- ACCOUNT FUNCTIONS ---------------- #
def account_balance(args):
    bot = BasicBot()
    try:
        resp = bot.client.futures_account_balance()
        print(json.dumps({"ok": True, "balances": resp}, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


def account_positions(args):
    bot = BasicBot()
    try:
        resp = bot.client.futures_position_information()
        print(json.dumps({"ok": True, "positions": resp}, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


def account_open_orders(args):
    bot = BasicBot()
    try:
        resp = bot.client.futures_get_open_orders()
        print(json.dumps({"ok": True, "open_orders": resp}, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


# ---------------- TWAP STRATEGY ---------------- #
def twap_strategy(args):
    """
    Executes a TWAP strategy by placing multiple smaller orders over time.
    Example:
    python cli.py twap --symbol BTCUSDT --side BUY --totalQty 0.01 --parts 10 --interval 30 --type MARKET
    """
    bot = BasicBot()
    total_qty = Decimal(args.totalQty)
    parts = int(args.parts)
    interval = int(args.interval)
    order_type = args.type
    side = args.side.upper()

    if parts <= 0 or total_qty <= 0:
        print("Invalid parts or quantity.")
        sys.exit(1)

    part_qty = total_qty / Decimal(parts)

    print(f"\nStarting TWAP strategy for {side} {total_qty} {args.symbol} in {parts} parts, {interval}s apart.")
    print(f"Each order: {part_qty} {args.symbol}, type: {order_type}\n")

    for i in range(parts):
        print(f"📦 Executing part {i+1}/{parts} ...")
        try:
            resp = bot.place_order(
                symbol=args.symbol,
                side=side,
                order_type=order_type,
                quantity=str(part_qty),
                price=args.price if order_type == "LIMIT" else None,
                time_in_force=args.timeInForce
            )
            print(json.dumps({"ok": True, "data": resp}, indent=2))
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}), file=sys.stderr)
        if i < parts - 1:
            time.sleep(interval)

    print("\nTWAP strategy complete.")


def main():
    parser = argparse.ArgumentParser(description="Binance Futures Testnet Trading Bot CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # ----- ORDER COMMAND -----
    order = sub.add_parser("order", help="Manage orders")
    order_sub = order.add_subparsers(dest="order_cmd", required=True)

    p_place = order_sub.add_parser("place", help="Place a new order")
    p_place.add_argument("--symbol", required=True)
    p_place.add_argument("--side", required=True, choices=["BUY", "SELL"])
    p_place.add_argument("--type", required=True, choices=["MARKET", "LIMIT", "STOP"])
    p_place.add_argument("--qty", required=True)
    p_place.add_argument("--price", type=str)
    p_place.add_argument("--stopPrice", type=str)
    p_place.add_argument("--timeInForce", default="GTC")
    p_place.add_argument("--reduceOnly", action="store_true")
    p_place.set_defaults(func=place_order)

    p_status = order_sub.add_parser("status", help="Get order status")
    p_status.add_argument("--symbol", required=True)
    p_status.add_argument("--orderId", type=int)
    p_status.add_argument("--clientOrderId")
    p_status.set_defaults(func=order_status)

    # ----- ACCOUNT COMMAND -----
    account = sub.add_parser("account", help="View account info")
    account_sub = account.add_subparsers(dest="account_cmd", required=True)

    a_balance = account_sub.add_parser("balance", help="Show account balance")
    a_balance.set_defaults(func=account_balance)

    a_positions = account_sub.add_parser("positions", help="Show open positions")
    a_positions.set_defaults(func=account_positions)

    a_orders = account_sub.add_parser("orders", help="Show open orders")
    a_orders.set_defaults(func=account_open_orders)

    # ----- TWAP COMMAND -----
    twap = sub.add_parser("twap", help="Run TWAP (Time-Weighted Average Price) strategy")
    twap.add_argument("--symbol", required=True, help="Symbol, e.g. BTCUSDT")
    twap.add_argument("--side", required=True, choices=["BUY", "SELL"])
    twap.add_argument("--totalQty", required=True, help="Total quantity to trade")
    twap.add_argument("--parts", type=int, default=5, help="Number of splits")
    twap.add_argument("--interval", type=int, default=30, help="Seconds between each order")
    twap.add_argument("--type", choices=["MARKET", "LIMIT"], default="MARKET")
    twap.add_argument("--price", type=str, help="Price for LIMIT orders")
    twap.add_argument("--timeInForce", default="GTC")
    twap.set_defaults(func=twap_strategy)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
