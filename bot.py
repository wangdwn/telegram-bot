# bot.py
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

app = ApplicationBuilder().token("8288157221:AAH7IDXYcZAsjrY9uHAmxKvDRvLw44FBoTs").build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()
