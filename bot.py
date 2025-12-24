import os
import sys
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Thay bằng token bot của bạn (lấy từ BotFather)
TOKEN = "8493795583:AAE6hfwY9PpGuCiFWqe91Xjh5hDCRau4XSM"

# Thay bằng user ID của bạn (chủ bot). Lấy bằng cách gửi tin nhắn cho bot và xem log.
ADMIN_ID = 123456789  # <-- Thay thành ID thật của bạn

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot sẵn sàng! Gửi tin nhắn để echo, gửi file để upload lại, hoặc (nếu bạn là admin) gửi file bot.py mới để update code.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        await update.message.reply_text(f"Echo: {update.message.text}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id

    # Xử lý document (file chung)
    if message.document:
        file = await message.document.get_file()
        file_path = f"downloaded_{message.document.file_name}"
        await file.download_to_drive(file_path)
        await message.reply_document(document=open(file_path, 'rb'), caption="File đã được upload lại trực tiếp!")
        os.remove(file_path)  # Xóa file tạm

    # Xử lý photo (lấy ảnh chất lượng cao nhất)
    elif message.photo:
        file = await message.photo[-1].get_file()
        file_path = "downloaded_photo.jpg"
        await file.download_to_drive(file_path)
        await message.reply_photo(photo=open(file_path, 'rb'), caption="Photo đã được upload lại!")
        os.remove(file_path)

    # Xử lý video
    elif message.video:
        file = await message.video.get_file()
        file_path = "downloaded_video.mp4"
        await file.download_to_drive(file_path)
        await message.reply_video(video=open(file_path, 'rb'), caption="Video đã được upload lại!")
        os.remove(file_path)

    # Có thể thêm các loại media khác nếu cần

async def handle_update_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Bạn không có quyền update code!")
        return

    if not update.message.document or not update.message.document.file_name == "bot.py":
        await update.message.reply_text("Chỉ chấp nhận file tên đúng là 'bot.py' để update!")
        return

    # Tải file mới về
    file = await update.message.document.get_file()
    await file.download_to_drive("bot_new.py")

    # Ghi đè file hiện tại
    os.replace("bot_new.py", __file__)  # __file__ là đường dẫn file hiện tại (bot.py)

    await update.message.reply_text("Code đã được update! Đang restart bot...")

    # Restart bot (thay thế process hiện tại)
    python = sys.executable
    os.execv(python, [python] + sys.argv)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Error: {context.error}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))  # Echo text
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO, handle_file))  # Upload file lại
    app.add_handler(MessageHandler(filters.Document.FileExtension("py"), handle_update_code))  # Chỉ admin update code

    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == '__main__':
    main()