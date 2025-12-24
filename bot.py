import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# THAY TÊN FILE .IPA THẬT CỦA BẠN VÀO ĐÂY
IPA_FILE_PATH = './your_app.ipa'  # Ví dụ: './MyCoolApp.ipa'

# ID của bạn (admin) - lấy bằng cách gửi tin nhắn cho bot @userinfobot trên Telegram
ADMIN_USER_ID = 961574571  # <--- THAY BẰNG USER ID CỦA BẠN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        keyboard = [
            [InlineKeyboardButton("📲 Nhận file .ipa", callback_data='send_ipa')],
            [InlineKeyboardButton("📤 Gửi file cho bot", callback_data='guide_upload')],
            [InlineKeyboardButton("🔄 Update code bot (Admin)", callback_data='admin_update')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            '🤖 Xin chào! Bot có 3 chức năng chính:\n\n'
            'Click nút bên dưới để sử dụng nhé!\n'
            '(Bạn cũng có thể gửi tin nhắn văn bản để bot echo lại)',
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Đóng thông báo "đang tải"

    if query.data == 'send_ipa':
        if not os.path.exists(IPA_FILE_PATH):
            await query.edit_message_text('❌ File .ipa hiện chưa có trên server.')
            return
        
        await query.edit_message_text('📲 Đang gửi file .ipa cho bạn...')
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=open(IPA_FILE_PATH, 'rb'),
            caption='🔥 Your App Name\nPhiên bản: 1.0\nCài bằng AltStore/Sideloadly'
        )

    elif query.data == 'guide_upload':
        await query.edit_message_text(
            '📤 Để gửi file cho bot:\n'
            '• Click biểu tượng 📎 (đính kèm)\n'
            '• Chọn "File" hoặc "Document"\n'
            '• Chọn file bất kỳ (bao gồm .ipa)\n'
            'Bot sẽ nhận và lưu ngay!'
        )

    elif query.data == 'admin_update':
        if query.from_user.id != ADMIN_USER_ID:
            await query.edit_message_text('⛔ Bạn không phải admin!')
            return
        await query.edit_message_text(
            '🔄 Cách update code bot:\n'
            '1. Gõ /update\n'
            '2. Gửi file bot.py mới\n'
            'Bot sẽ tự thay thế và Render restart tự động.'
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.document:
        document = update.message.document
        os.makedirs("downloads", exist_ok=True)
        file_path = f"./downloads/{document.file_name}"
        file = await document.get_file()
        await file.download_to_drive(custom_path=file_path)
        await update.message.reply_text(f'✅ Đã nhận và lưu file: {document.file_name}')

async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text('⛔ Chỉ admin mới được update code!')
        return
    if update.message.document and update.message.document.file_name == 'bot.py':
        file = await update.message.document.get_file()
        await file.download_to_drive(custom_path='./bot.py')
        await update.message.reply_text('🔄 Update code thành công! Render sẽ restart bot trong vài giây.')
    else:
        await update.message.reply_text('⚠️ Gửi đúng file tên "bot.py" kèm lệnh /update.')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.warning('Update caused error: %s', context.error)

if __name__ == '__main__':
    TOKEN = os.getenv('BOT_TOKEN')
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))  # Xử lý nút bấm
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_file))
    app.add_handler(CommandHandler("update", update_bot))

    app.add_error_handler(error_handler)

    logger.info("Bot với 3 nút menu đã khởi động!")
    app.run_polling(drop_pending_updates=True)