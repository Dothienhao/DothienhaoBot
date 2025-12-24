
    import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Cấu hình logging để dễ theo dõi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# === CẤU HÌNH CỦA BẠN (chỉ cần sửa ở đây) ===
IPA_FILE_PATH = './your_app.ipa'          # ← Thay thành tên file .ipa thật, ví dụ './MyGame.ipa'
ADMIN_USER_ID = 123456789                 # ← Thay bằng User ID của bạn (lấy từ @userinfobot trên Telegram)
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    keyboard = [
        [InlineKeyboardButton("📲 Nhận file .ipa", callback_data='send_ipa')],
        [InlineKeyboardButton("📤 Gửi file cho bot", callback_data='guide_upload')],
        [InlineKeyboardButton("🔄 Update code bot (Admin)", callback_data='admin_update')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        '🤖 Chào mừng bạn đến với bot!\n\n'
        'Chọn chức năng bằng nút bên dưới:\n'
        '• Nhận file .ipa cài app\n'
        '• Gửi file bất kỳ cho bot lưu\n'
        '• Echo tin nhắn văn bản (gõ trực tiếp)\n\n'
        'Bot đang chạy ổn định trên Render.com 🚀',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()

    if query.data == 'send_ipa':
        if not os.path.exists(IPA_FILE_PATH):
            await query.edit_message_text('❌ File .ipa chưa được upload lên server. Vui lòng thử lại sau.')
            return
        
        await query.edit_message_text('📲 Đang gửi file .ipa...')
        try:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=open(IPA_FILE_PATH, 'rb'),
                caption='🔥 Tên App Của Bạn\nPhiên bản: Latest\nCài đặt bằng AltStore, Sideloadly hoặc TrollStore nhé!'
            )
            await query.delete_message()  # Xóa thông báo "Đang gửi"