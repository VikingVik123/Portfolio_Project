import logging
from config import TELEGRAM_TOKEN, API_KEY, API_SECRET
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackContext
import time

class TelegramBot:
    def __init__(self, trading_engine):
        self.application = Application.builder().token(TELEGRAM_TOKEN).build()
        self.trading_engine = trading_engine
        self.running = False

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("stats", self.stats))
        self.application.add_handler(CommandHandler("stop", self.stop))
        self.application.add_handler(CommandHandler("balance", self.balance))
        self.application.add_handler(CommandHandler("positions", self.positions))
        self.application.add_handler(CommandHandler("runbot", self.runbot))
        self.application.add_handler(CommandHandler("stopbot", self.stopbot))

        self.reply_keyboard = [['/start', '/stats', '/stop'], ['/balance', '/positions'], ['/runbot', '/stopbot']]
        self.reply_markup = ReplyKeyboardMarkup(self.reply_keyboard, resize_keyboard=True)

    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text(
            "Welcome! Choose an option:",
            reply_markup=self.reply_markup
        )

    async def stats(self, update: Update, context: CallbackContext):
        stats = self.trading_engine.show_trade_stats()
        await update.message.reply_text(stats)

    async def stop(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Bot stopped!")

    async def balance(self, update: Update, context: CallbackContext):
        balance = self.trading_engine.get_balance()
        await update.message.reply_text(f"Balance: {balance}")

    async def positions(self, update: Update, context: CallbackContext):
        positions = self.trading_engine.show_open_positions()
        await update.message.reply_text(positions)

    async def runbot(self, update: Update, context: CallbackContext):
        if not self.running:
            self.running = True
            await update.message.reply_text("Trading bot started!")
        else:
            await update.message.reply_text("Trading bot is already running.")

    async def stopbot(self, update: Update, context: CallbackContext):
        self.running = False
        await update.message.reply_text("Trading bot stopped!")

    def run_trading_bot(self):
        while self.running:
            try:
                ohlcv = self.trading_engine.fetch_data()
                self.trading_engine.save_to_db(ohlcv)
                self.trading_engine.execute_order()
            except Exception as e:
                logging.error(f"An error occurred: {e}")
            time.sleep(60)

    def run(self):
        self.application.run_polling()