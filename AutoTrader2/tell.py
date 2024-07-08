from config import TELEGRAM_TOKEN
from telegram.ext import Updater, CommandHandler, CallbackContext
from main import TradingBot


class Telegram:
    def __init__(self, token, trading_bot):
        self.updater = Updater(token, use_context=True)
        self.dp = self.updater.dispatch
        self.trading_bot = trading_bot

        # Set up command handlers
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("stop", self.stop))
        self.dp.add_handler(CommandHandler("balance", self.balance))
        self.dp.add_handler(CommandHandler("positions", self.positions))

tel = Telegram()
tel.__init__()