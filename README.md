# 🪙 Binance Futures Testnet Trading Bot

> A **Python-based Binance Futures Testnet Trading Bot** with support for **Market**, **Limit**, and **TWAP (Time-Weighted Average Price)** orders — featuring a beautiful **interactive Rich CLI dashboard** and detailed logging.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Binance API](https://img.shields.io/badge/Binance-Futures-yellow)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Complete-success)

---

## 🚀 Overview

This project implements a simplified **automated trading bot** for the **Binance Futures Testnet (USDT-M)** using the official [python-binance](https://github.com/sammchardy/python-binance) SDK.

It allows you to:

* Place **Market**, **Limit**, and **Stop-Limit (optional)** orders
* Execute **TWAP (Time-Weighted Average Price)** strategies
* View **balances**, **positions**, and **open orders**
* Interact via a clean **interactive Rich CLI Dashboard**

Built with **modular, reusable classes**, detailed **error handling**, and **logging** — perfect for projects, demos, or learning algorithmic trading fundamentals.

---

## 🧠 Features

| Feature                               | Description                                               |
| ------------------------------------- | --------------------------------------------------------- |
| ✅ Binance Futures Testnet Integration | Uses REST API at `https://testnet.binancefuture.com/fapi` |
| ✅ Market & Limit Orders               | Full support for BUY/SELL sides                           |
| ✅ TWAP Strategy                       | Splits large orders into timed smaller trades             |
| ✅ CLI Dashboard                       | Interactive UI with Rich styling                          |
| ✅ Account Tools                       | Check balance, positions, and open orders                 |
| ✅ Logging                             | All API requests, responses, and errors logged            |
| ✅ Modular Design                      | Built with a `BasicBot` class for reuse                   |

---

## ⚙️ Setup Instructions (macOS / Linux / Windows)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Amogh004/binance-futures-testnet-bot.git
cd binance-futures-testnet-bot
```

### 2️⃣ Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up environment variables

Copy the example:

```bash
cp .env.example .env
```

Edit `.env` and fill in your **Binance Testnet API credentials**:

```
BINANCE_API_KEY=your_testnet_key_here
BINANCE_API_SECRET=your_testnet_secret_here
```

Create them here: [https://testnet.binancefuture.com](https://testnet.binancefuture.com)

---

## 💻 Usage

### 🟢 Launch the Interactive Dashboard

```bash
python dashboard.py
```

You’ll see:

```
🚀 Binance Futures Testnet Bot Dashboard
[1] Place Order
[2] Check Account Balance
[3] View Open Positions
[4] View Open Orders
[5] Run TWAP Strategy
[6] Exit
```

### 🧾 Example CLI Commands

You can also use direct CLI commands:

```bash
# Place a Market order
python cli.py order place --symbol BTCUSDT --side BUY --type MARKET --qty 0.001

# Place a Limit order
python cli.py order place --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 120000 --timeInForce GTC

# Run TWAP Strategy
python cli.py twap --symbol BTCUSDT --side BUY --totalQty 0.01 --parts 5 --interval 20
```

---

## 📊 Project Structure

```
binance-futures-testnet-bot/
│
├── bot/
│   ├── basic_bot.py          # Core Binance API wrapper class
│   ├── logging_config.py     # Logger setup (console + file)
│   └── __init__.py
│
├── cli.py                    # Command-line interface
├── dashboard.py              # Interactive Rich CLI dashboard
├── requirements.txt          # Dependencies
├── .env.example              # Example environment file
├── logs/                     # Stores logs
└── README.md                 # Documentation
```

---

## 🧩 Example TWAP Output

```
🚀 Starting TWAP strategy for BUY 0.01 BTCUSDT in 5 parts, 20s apart.
Each order: 0.002 BTCUSDT, type: MARKET

📦 Executing part 1/5 ...
✅ Order filled @ 101974.1

📦 Executing part 2/5 ...
✅ Order filled @ 101982.0
...
✅ TWAP strategy complete.
```

---

## 🪄 Technologies Used

* **Python 3.10+**
* **Binance Futures Testnet API**
* **python-binance**
* **Rich (for CLI UI)**
* **dotenv**
* **logging**

---

## 🧰 Future Enhancements

* Add WebSocket-based live trade and position updates
* Implement Grid or OCO order strategies
* Add a lightweight web dashboard (Streamlit or Flask)

---

## 🧑‍💻 Author

**Amogh Kulkarni**
🎓 CSE Undergraduate | 💼 Aspiring Software Engineer | 🤖 AI & FinTech Enthusiast
🔗 [GitHub Profile](https://github.com/Amogh004)

---

## 🪪 License

This project is licensed under the **MIT License** — feel free to use, modify, and share it.

---

### ⭐ If you found this project helpful, give it a star on GitHub!

```
git clone https://github.com/Amogh004/binance-futures-testnet-bot.git
```

---
