import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_snap_media(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(5000)

        video = await page.query_selector("video")
        if video:
            return await video.get_attribute("src")

        img = await page.query_selector("img")
        if img:
            return await img.get_attribute("src")

        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط قصة من Snapchat مثل: https://story.snapchat.com/s/...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    snap_url = text if text.startswith("http") else f"https://www.snapchat.com/add/{text}"

    await update.message.reply_text("جارٍ تحميل المحتوى...")

    media_url = await get_snap_media(snap_url)
    if media_url:
        try:
            if ".mp4" in media_url:
                await update.message.reply_video(media_url)
            else:
                await update.message.reply_photo(media_url)
        except Exception as e:
            logger.error(f"خطأ في إرسال الوسائط: {e}")
            await update.message.reply_text("تم العثور على الوسائط ولكن حدث خطأ أثناء الإرسال.")
    else:
        await update.message.reply_text("لم يتم العثور على محتوى عام أو رابط غير صالح.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
