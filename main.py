import os
import random
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find("table", {"id": "proxylisttable"}).tbody.find_all("tr"):
        cols = row.find_all("td")
        ip = cols[0].text
        port = cols[1].text
        https = cols[6].text == "yes"
        if https:
            proxies.append(f"http://{ip}:{port}")
    return proxies

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 سلام! لینک رو بفرست تا دانلود کنم با آی‌پی متغیر!")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    proxies = get_proxies()

    await update.message.reply_text("📡 در حال تلاش برای دانلود...")

    output_path = 'downloads'
    os.makedirs(output_path, exist_ok=True)

    for proxy in random.sample(proxies, min(10, len(proxies))):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(output_path, 'video.%(ext)s'),
                'format': 'best[ext=mp4]/best',
                'proxy': proxy,
                'quiet': True,
                'noplaylist': True,
                'retries': 2,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            with open(filename, 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file)
            os.remove(filename)
            return

        except Exception as e:
            print(f"❌ Proxy failed: {proxy} -> {e}")
            continue

    await update.message.reply_text("🚫 نتونستم با هیچ پراکسی‌ای دانلود کنم.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
print("🚀 Bot is running...")
app.run_polling()
