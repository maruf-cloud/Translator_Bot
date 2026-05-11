import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
import sqlite3

TOKEN = "8766018338:AAHGJH_VXsPd3PCMvV0htp0lIVEydhx5vC0"

logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect('user_lang.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, lang TEXT DEFAULT 'en')''')
conn.commit()

def get_user_lang(user_id):
    c.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    return result[0] if result else 'en'

def set_user_lang(user_id, lang):
    c.execute("REPLACE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang))
    conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Hello! I am Universal Translator Bot.\n\nSet your language: /set_lang en\n(Use language codes like: en, bn, zh, hi, ar, es, fr, de, ru, ja)")

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Example: /set_lang en\n\nUse /langs to see supported language codes")
        return
    lang_code = context.args[0].lower()
    try:
        GoogleTranslator(source='auto', target=lang_code).translate("test")
        set_user_lang(update.effective_user.id, lang_code)
        await update.message.reply_text(f"✅ Language changed. Your code: {lang_code}")
    except:
        await update.message.reply_text("❌ Invalid language code. Please use correct code.")

async def my_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text(f"Your current language code: {lang}")

async def langs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Supported languages:\nbn - Bengali\nen - English\nzh - Chinese\nhi - Hindi\nar - Arabic\nes - Spanish\nfr - French\nde - German\nru - Russian\nja - Japanese\nko - Korean\ntr - Turkish\nur - Urdu\nth - Thai")

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    target_lang = get_user_lang(user_id)
    text = update.message.text
    
    if text.startswith('/'):
        return
    
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        await update.message.reply_text(translated)
    except Exception as e:
        await update.message.reply_text("Translation failed. Please try again.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_lang", set_lang))
    app.add_handler(CommandHandler("my_lang", my_lang))
    app.add_handler(CommandHandler("langs", langs))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
    app.run_polling()

if __name__ == "__main__":
    main()
