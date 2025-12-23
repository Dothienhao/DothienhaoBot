import telebot
import os

# Dùng env variable cho token (an toàn vcl, đéo lộ nữa)
TOKEN = os.getenv('8493795583:AAE6hfwY9PpGuCiFWqe91Xjh5hDCRau4XSM')  # Trên Render đã set rồi

# DÁN USER ID CỦA MÀY VÀO ĐÂY (chỉ mày upload được)
MY_ID = 123456789  # Thay bằng ID thật của mày nhé con

bot = telebot.TeleBot(TOKEN)

# Dictionary lưu file tạm theo số (1,2,3)
files = {'1': None, '2': None, '3': None}

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("1")
    btn2 = telebot.types.KeyboardButton("2")
    btn3 = telebot.types.KeyboardButton("3")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Chọn số để download IPA nhé thằng lồn:", reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # CHỈ MÀY MỚI UPLOAD ĐƯỢC, THẰNG KHÁC SEND FILE THÌ IGNORE
    if message.from_user.id != MY_ID:
        return  # Im re, đéo reply gì cả
    
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Lưu tạm vào thư mục hiện tại (Render có /app)
    file_path = message.document.file_name
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    bot.reply_to(message, f"File {file_path} upload ngon lành! Giờ chọn số 1/2/3 để assign nó nhé chủ nhân 😏")

@bot.message_handler(func=lambda message: message.text in ['1', '2', '3'])
def send_file(message):
    num = message.text
    if files[num]:
        with open(files[num], 'rb') as f:
            bot.send_document(message.chat.id, f, caption="IPA ngon lành đây!")
    else:
        bot.reply_to(message, "Chưa có file nào ở số này đâu thằng điên! Upload trước đi.")

# Thêm lệnh assign file cho số (sau khi upload)
@bot.message_handler(commands=['assign'])
def assign_file(message):
    # Chỉ mày assign được
    if message.from_user.id != MY_ID:
        return
    # Ví dụ: /assign 1 tenfile.ipa
    try:
        _, num, filename = message.text.split()
        if num in files and os.path.exists(filename):
            files[num] = filename
            bot.reply_to(message, f"Đã assign {filename} cho nút {num}!")
        else:
            bot.reply_to(message, "File đéo tồn tại hoặc số sai!")
    except:
        bot.reply_to(message, "Dùng: /assign <số> <tên file> nhé chủ nhân")

print("Bot chạy, chỉ nghe upload từ chủ nhân...")
bot.infinity_polling()
