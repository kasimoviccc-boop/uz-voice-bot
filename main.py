import asyncio
import edge_tts
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# 1. Flask server Render "Live" turishi uchun
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is running!"

def run():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Bot sozlamalari
TOKEN = "8222754598:AAHO8XxWhcYCWxZrBN3mEhefB-WNckrk_dY"
VOICES = {"female": "uz-UZ-MadinaNeural", "male": "uz-UZ-SardorNeural"}
user_settings = {}

# 3. /start buyrug'i uchun funksiya
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_settings[user_id] = "female"
    
    keyboard = [
        [
            InlineKeyboardButton("👩 Madina (Ayol)", callback_data="set_female"),
            InlineKeyboardButton("👨 Sardor (Erkak)", callback_data="set_male"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Salom! Men matnni ovozga aylantiruvchi botman.\n"
        "Ovozni yaxshilash uchun matnda nuqta va vergullardan foydalaning.\n"
        "Matn yuboring, men uni audio qilib beraman.",
        reply_markup=reply_markup
    )

# 4. Tugmalar bosilganda ishlaydigan funksiya
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "set_female":
        user_settings[user_id] = "female"
        await query.edit_message_text("Ovoz o'zgartirildi: 👩 Madina. Endi matn yuboring.")
    elif query.data == "set_male":
        user_settings[user_id] = "male"
        await query.edit_message_text("Ovoz o'zgartirildi: 👨 Sardor. Endi matn yuboring.")

# 5. Matn yuborilganda ovozga aylantirish funksiyasi
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    gender = user_settings.get(user_id, "female")
    voice = VOICES[gender]
    
    status_msg = await update.message.reply_text("Ovoz yozilmoqda, kuting...")
    output_file = f"voice_{user_id}.mp3"
    
    try:
        # rate="-10%" - ovozni 10% sekinlashtiradi (tabiiylik uchun)
        # pitch="-1Hz" - ovozni biroz yo'g'onlashtiradi (robotlikni kamaytirish uchun)
        communicate = edge_tts.Communicate(text, voice, rate="-10%", pitch="-1Hz")
        await communicate.save(output_file)
        
        with open(output_file, 'rb') as audio:
            await update.message.reply_voice(voice=audio, caption="Tayyor!")
            
        await status_msg.delete()
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

# 6. Asosiy ishga tushirish qismi
if __name__ == "__main__":
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    
    print("Bot Renderda ishga tushdi...")
    app.run_polling()
    
