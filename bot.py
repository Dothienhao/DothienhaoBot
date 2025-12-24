import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Xin chào! Bot đang chạy trên Render.com.\n'
        'Gửi tin nhắn để echo.\n'
        'Gửi file để bot nhận và lưu.\n'
        'Dùng /update + gửi file bot.py mới để tự update code.'
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        file = await update.message.document.get_file()
        await file.download_to_drive(custom_path=f"./downloads/{update.message.document.file_name}")
        await update.message.reply_text(f'Đã lưu file: {update.message.document.file_name}')
    else:
        await update.message.reply_text('Gửi một file đi!')

async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document and update.message.document.file_name == 'bot.py':
        file = await update.message.document.get_file()
        await file.download_to_drive(custom_path='./bot.py')
        await update.message.reply_text('Đã update file bot.py thành công!\nBot sẽ tự restart trong vài giây nhờ Render.')
    else:
        await update.message.reply_text('Gửi đúng file tên "bot.py" kèm lệnh /update nhé!')

if __name__ == '__main__':
    TOKEN = os.getenv('BOT_TOKEN')  # Lấy token từ environment variable
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_file))
    app.add_handler(CommandHandler("update", update_bot))

    # Render yêu cầu port từ environment
    port = int(os.environ.get('PORT', 10000))
    app.run_polling()  # Dùng polling vì dễ nhất trên Render miễn phí