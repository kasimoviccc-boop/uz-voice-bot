import asyncio
import edge_tts
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# Flask server (Render "Live" turishi uchun)
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is running!"

def run():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT SOZLAMALARI ---
TOKEN = "8222754598:AAHO8XxWhcYCWxZrBN3mEhefB-WNckrk_dY"
VOICES = {"female": "uz-UZ-MadinaNeural", "male": "uz-UZ-SardorNeural"}
user_settings = {}

# (Qolgan barcha funksiyalar: start, button_handler, handle_text yuqoridagidek qoladi...)

if __name__ == "__main__":
    keep_alive() # Web serverni ishga tushirish
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    
    print("Bot Renderda ishga tushmoqda...")
    app.run_polling()
  
