
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8493795583:AAE6hfwY9PpGuCiFWqe91Xjh5hDCRau4XSM'  # Thay bằng token thật
bot = telebot.TeleBot(TOKEN)

IPA_FILES = {}

# Biến đếm số IPA
ipa_counter = 0

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup(row_width=3)
    for num in sorted(IPA_FILES.keys(), key=int):
        markup.add(InlineKeyboardButton(num, callback_data=num))
    
    if IPA_FILES:
        bot.send_message(message.chat.id, "Chọn số để download IPA nhé thằng lồn:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Chưa có IPA nào, send file .ipa cho tao nhận đi con trai!")

# Nhận file .ipa từ chat
@bot.message_handler(content_types=['document'])
def handle_document(message):
    global ipa_counter
    if message.document.file_name.lower().endswith('.ipa'):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Lưu file tạm trên Render
        file_name = f"ipa_{ipa_counter + 1}.ipa"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        ipa_counter += 1
        IPA_FILES[str(ipa_counter)] = file_name
        
        bot.reply_to(message, f"Nhận IPA ngon lành! Giờ nút {ipa_counter} sẽ send file này.")
    else:
        bot.reply_to(message, "Send file .ipa thôi thằng lồn, cái khác tao đéo nhận!")

# Khi nhấn nút
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    num = call.data
    if num in IPA_FILES:
        file_path = IPA_FILES[num]
        with open(file_path, 'rb') as file:
            bot.send_document(call.message.chat.id, file, caption=f"IPA số {num} đây thằng lồn!")
        bot.answer_callback_query(call.id, "Sending IPA...")
    else:
        bot.answer_callback_query(call.id, "Chưa có IPA này!")

bot.polling(none_stop=True)
