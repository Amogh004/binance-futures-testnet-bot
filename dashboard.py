from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt
import os, time, json
from decimal import Decimal
from bot.basic_bot import BasicBot

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    console.print("\n[bold cyan]Press Enter to continue...[/bold cyan]", end="")
    input()

def banner():
    clear_screen()
    console.rule("[bold green]🚀 Binance Futures Testnet Bot[/bold green]")

def show_table(title, data_dicts, columns):
    table = Table(title=title, show_lines=True)
    for col in columns:
        table.add_column(col, style="cyan")
    for row in data_dicts:
        table.add_row(*[str(row.get(col, "")) for col in columns])
    console.print(table)

def place_order(bot):
    banner()
    console.print(Panel.fit("📦 [bold yellow]Place a New Order[/bold yellow]"))
    symbol = Prompt.ask("Symbol", default="BTCUSDT").upper()
    side = Prompt.ask("Side", choices=["BUY", "SELL"]).upper()
    otype = Prompt.ask("Order Type", choices=["MARKET", "LIMIT", "STOP"]).upper()
    qty = Prompt.ask("Quantity")
    price = stop_price = None
    tif = "GTC"
    if otype in ["LIMIT", "STOP"]:
        price = Prompt.ask("Limit Price")
        if otype == "STOP":
            stop_price = Prompt.ask("Stop Trigger Price")
        tif = Prompt.ask("TimeInForce", default="GTC")
    try:
        resp = bot.place_order(symbol, side, otype, qty, price, tif, stop_price)
        console.print_json(json.dumps(resp))
        console.print("[green]✅ Order placed successfully[/green]")
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")
    pause()

def show_balance(bot):
    banner()
    console.print(Panel.fit("💰 [bold yellow]Account Balances[/bold yellow]"))
    try:
        balances = bot.client.futures_account_balance()
        rows = [b for b in balances if float(b["balance"]) > 0]
        show_table("Balances", rows, ["asset", "balance", "availableBalance"])
    except Exception as e:
        console.print(f"[red]❌ {e}[/red]")
    pause()

def show_positions(bot):
    banner()
    console.print(Panel.fit("📊 [bold yellow]Open Positions[/bold yellow]"))
    try:
        positions = bot.client.futures_position_information()
        active = [p for p in positions if float(p["positionAmt"]) != 0]
        if not active:
            console.print("[yellow]No open positions.[/yellow]")
        else:
            show_table("Positions", active, ["symbol", "positionAmt", "entryPrice", "unRealizedProfit"])
    except Exception as e:
        console.print(f"[red]❌ {e}[/red]")
    pause()

def show_orders(bot):
    banner()
    console.print(Panel.fit("📜 [bold yellow]Open Orders[/bold yellow]"))
    try:
        orders = bot.client.futures_get_open_orders()
        if not orders:
            console.print("[yellow]No open orders.[/yellow]")
        else:
            show_table("Open Orders", orders, ["symbol", "side", "origQty", "price", "status"])
    except Exception as e:
        console.print(f"[red]❌ {e}[/red]")
    pause()

def run_twap(bot):
    banner()
    console.print(Panel.fit("🕒 [bold yellow]TWAP Strategy[/bold yellow]"))
    symbol = Prompt.ask("Symbol", default="BTCUSDT").upper()
    side = Prompt.ask("Side", choices=["BUY", "SELL"]).upper()
    total_qty = Decimal(Prompt.ask("Total Quantity", default="0.01"))
    parts = int(Prompt.ask("Number of Parts", default="5"))
    interval = int(Prompt.ask("Seconds Between Orders", default="20"))
    order_type = Prompt.ask("Type", choices=["MARKET", "LIMIT"], default="MARKET")
    price = None
    if order_type == "LIMIT":
        price = Prompt.ask("Limit Price")

    part_qty = total_qty / Decimal(parts)
    console.print(f"\nExecuting TWAP: [bold]{total_qty} {symbol}[/bold] in [cyan]{parts}[/cyan] parts ({part_qty} each)\n")

    for i in track(range(parts), description="[cyan]Placing orders...[/cyan]"):
        try:
            resp = bot.place_order(symbol, side, order_type, str(part_qty), price)
            console.log(f"[green]Part {i+1}/{parts} → orderId {resp.get('orderId')}[/green]")
        except Exception as e:
            console.log(f"[red]Error in part {i+1}: {e}[/red]")
        if i < parts - 1:
            time.sleep(interval)
    console.print("[bold green]\n✅ TWAP strategy completed.[/bold green]")
    pause()

def main():
    bot = BasicBot()
    while True:
        banner()
        console.print(
            """
[bold cyan][1][/bold cyan] Place Order
[bold cyan][2][/bold cyan] Check Account Balance
[bold cyan][3][/bold cyan] View Open Positions
[bold cyan][4][/bold cyan] View Open Orders
[bold cyan][5][/bold cyan] Run TWAP Strategy
[bold cyan][6][/bold cyan] Exit
"""
        )
        choice = Prompt.ask("Select Option", choices=["1","2","3","4","5","6"])
        if choice == "1": place_order(bot)
        elif choice == "2": show_balance(bot)
        elif choice == "3": show_positions(bot)
        elif choice == "4": show_orders(bot)
        elif choice == "5": run_twap(bot)
        else:
            banner()
            console.print("[bold green]👋 Exiting dashboard. Goodbye![/bold green]\n")
            break

if __name__ == "__main__":
    main()
