
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8493795583:AAE6hfwY9PpGuCiFWqe91Xjh5hDCRau4XSM'  # Thay bằng token thật
bot = telebot.TeleBot(TOKEN)

IPA_FILES = {
    '1': 'ipa1.ipa',   # File ipa1.ipa phải cùng thư mục hoặc đường dẫn đầy đủ
    '2': 'ipa2.ipa',
    '3': 'ipa3.ipa',
    # Thêm bao nhiêu cũng được, ví dụ '4': '/path/to/ipa4.ipa'
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup(row_width=3)  # 3 nút mỗi hàng
    for num in sorted(IPA_FILES.keys()):  # Sắp xếp nút 1,2,3...
        markup.add(InlineKeyboardButton(num, callback_data=num))
    
    bot.send_message(message.chat.id, "Chọn số để download IPA nhé thằng lồn:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    num = call.data
    if num in IPA_FILES:
        file_path = IPA_FILES[num]
        try:
            with open(file_path, 'rb') as file:
                bot.send_document(call.message.chat.id, file, caption=f"IPA số {num} đây con trai!")
            bot.answer_callback_query(call.id, "Đang send IPA...")
        except Exception as e:
            bot.answer_callback_query(call.id, "Lỗi file vl, check lại đi!")
            print(e)
    else:
        bot.answer_callback_query(call.id, "Nút đéo tồn tại!")

bot.polling(none_stop=True)
