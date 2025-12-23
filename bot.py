import telebot
import os

# Token từ env Render (an toàn vcl, đéo lộ)
TOKEN = os.getenv('8493795583:AAE6hfwY9PpGuCiFWqe91Xjh5hDCRau4XSM')
# ID của mày - chỉ mày upload được (set trên Render Environment)
MY_ID = int(os.getenv('961574571', '0'))

bot = telebot.TeleBot(TOKEN)

# Chỉ 2 slot thôi, nút 1 và 2
IPA_FILES = {'1': None, '2': None}
ipa_counter = 0  # Đếm file upload (nếu muốn đặt tên ipa_1.ipa, ipa_2.ipa...)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("1")
    btn2 = telebot.types.KeyboardButton("2")
    markup.add(btn1, btn2)  # Chỉ 2 nút thôi con lồn ơi
    bot.send_message(message.chat.id, "Chọn số để download IPA nhé thằng lồn:", reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # CHỈ MÀY MỚI UPLOAD ĐƯỢC, THẰNG KHÁC SEND GÌ CŨNG IM RE
    if message.from_user.id != MY_ID:
        return
    
    # Chỉ nhận file .ipa thôi
    if not message.document.file_name.lower().endswith('.ipa'):
        bot.reply_to(message, "Send file .ipa thôi thằng điên, đéo nhận cái khác!")
        return
    
    global ipa_counter
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Đặt tên file mới kiểu ipa_1.ipa, ipa_2.ipa... (dễ quản lý)
    ipa_counter += 1
    file_name = f"ipa_{ipa_counter}.ipa"
    
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    bot.reply_to(message, f"Nhận IPA ngon lành chủ nhân! File lưu thành {file_name}\n"
                          f"Giờ reply tin này kèm số 1 hoặc 2 để assign nhé (vd: 1)")

@bot.message_handler(func=lambda message: message.text in ['1', '2'] and message.reply_to_message)
def assign_slot(message):
    # Chỉ chủ nhân assign (an toàn)
    if message.from_user.id != MY_ID:
        return
    
    num = message.text
    # Lấy file_name từ tin nh
