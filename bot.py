
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# === CHỈNH SỬA 2 DÒNG NÀY THÔI ===
IPA_FILE_PATH = './your_app.ipa'    # ← Đổi thành tên file .ipa thật của bạn, ví dụ './GameMod.ipa'
ADMIN_USER_ID = 123456789          # ← Đổi thành ID Telegram của bạn (lấy từ @userinfobot)
# =================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message:
        return

    keyboard = [
        [InlineKeyboardButton("📲 Nhận file .ipa", callback_data='send_ipa')],
        [InlineKeyboardButton("📤 Gửi file cho bot", callback_data='guide_upload')],
        [InlineKeyboardButton("🔄 Update code bot", callback_data='admin_update')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        '🤖 Bot Phân Phối .ipa\n\n'
        'Chọn chức năng bằng các nút bên dưới 👇\n'
        'Gõ tin nhắn bất kỳ để bot lặp lại.',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'send_ipa':
        if not os.path.isfile(IPA_FILE_PATH):
            await query.edit_message_text('❌ File .ipa chưa có trên server!\nAdmin cần upload lại.')
            return

        await query.edit_message_text('📲 Đang gửi file .ipa cho bạn...')
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=open(IPA_FILE_PATH, 'rb'),
            caption='🔥 App Name\n🆕 Phiên bản mới nhất\nCài đặt bằng AltStore / Sideloadly / TrollStore'
        )

    elif query.data == 'guide_upload':
        await query.edit_message_text(
            '📤 Cách gửi file cho bot:\n\n'
            '• Nhấn biểu tượng 📎\n'
            '• Chọn "File"\n'
            '• Chọn file bạn muốn gửi (.ipa, ảnh, video...)\n\n'
            'Bot sẽ lưu ngay!'
        )

    elif query.data == 'admin_update':
        if query.from_user.id != ADMIN_USER_ID:
            await query.edit_message_text('🔒 Chức năng chỉ dành cho admin.')
            return
        await query.edit_message_text(
            '🔄 Update code bot:\n\n'
            '/update + gửi file bot.py mới\n'
            '→ Bot tự thay code và restart trong vài giây.'
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.document:
        doc = update.message.document
        os.makedirs('downloads', exist_ok=True)
        await doc.get_file().download_to_drive(f'downloads/{doc.file_name}')
        await update.message.reply_text(f'✅ Đã lưu file:\n{doc.file_name}')

async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or msg.from_user.id != ADMIN_USER_ID:
        if msg:
            await msg.reply_text('⛔ Chỉ admin được phép update!')
        return

    if msg.document and msg.document.file_name.lower() == 'bot.py':
        await msg.document.get_file().download_to_drive('bot.py')
        await msg.reply_text('✅ Update code thành công!\nBot sẽ restart ngay...')
    else:
        await msg.reply_text('⚠️ Gửi đúng file tên "bot.py" kèm lệnh /update.')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error('Lỗi: %s', context.error)

if __name__ == '__main__':
    TOKEN = os.getenv('KEYTOKEN')
    if not TOKEN:
        logger.error("KEYTOKEN không tồn tại!")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_file))
    app.add_handler(CommandHandler('update', update_bot))
    app.add_error_handler(error_handler)

    logger.info("Bot đang chạy...")
    app.run_polling(drop_pending_updates=True)