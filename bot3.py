import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from google import genai

# --- KALITLAR ---
# O'zingizning Telegram Bot va Google AI Studio kalitlaringizni shu yerga qo'ying
BOT_TOKEN = "8669567287:AAHjkGwbf7tnJqgmzsOxa93Kfk7fceHPoFo"
GEMINI_API_KEY = "AQ.Ab8RN6JL4WGXsabrglBQokHltKcJaRmn0NZNoYnnvscFzmbccA"

# Yangi rasmiy Google GenAI mijozini yaratish
client = genai.Client(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

# --- DAVLATLAR RO'YXATI ---
DAVLATLAR = [
    "🇺🇿 O'zbekiston",
    "🇷🇺 Rossiya",
    "🇺🇸 AQSh (Amerika)",
    "🇰🇷 Janubiy Koreya",
    "🇰🇿 Qozog'iston",
    "🇰🇬 Qirg'iziston",
    "🇹🇲 Turkmaniston",
    "🇹🇯 Tojikiston"
]

# --- TILLAR BO'YICHA MATNLAR (FAQAT 3 TA TIL) ---
TEXTS = {
    "uz": {
        "ask_os": "Telefoningiz qaysi operatsion tizimda ishlaydi?",
        "ask_model": "Telefon modelini yozing (Masalan: Galaxy S24 Ultra yoki iPhone 15 Pro):",
        "ask_memory": "Telefon xotirasini tanlang yoki yozing (Masalan: 128GB, 256GB, 512GB):",
        "ask_battery": "iPhone batareya holatini (ёмкость) foizda kiriting (Faqat son yozing, masalan: 85):",
        "battery_error": "Iltimos, faqat to'g'ri son kiriting (0 dan 100 gacha):",
        "ask_state": "Telefonning umumiy tashqi holati qanday? (Masalan: Yangidek, ozroq qirilgan):",
        "ask_has_fault": "Telefonning biron-bir aybi yoki nuqsoni bormi?",
        "btn_yes": "Bor 🔴", "btn_no": "Yo'q 🟢",
        "write_fault": "Telefonning barcha ayblarini batafsil yozib qoldiring:",
        "calculating": "AI ma'lumotlarni internet orqali tahlil qilmoqda, iltimos kuting... ⏳",
        "prompt": "Siz professional smartfon bozori ekspertisiz. Telefonni ko'rsatilgan davlat bozori narxlarida, mahalliy valyutada va AQSh dollarida baholang."
    },
    "ru": {
        "ask_os": "На какой операционной системе работает ваш телефон?",
        "ask_model": "Введите модель телефона (Например: Galaxy S24 Ultra или iPhone 15 Pro):",
        "ask_memory": "Выберите или введите объем памяти (Например: 128GB, 256GB, 512GB):",
        "ask_battery": "Введите емкость батареи iPhone в процентах (Только число, например: 85):",
        "battery_error": "Пожалуйста, введите корректное число (от 0 до 100):",
        "ask_state": "Каково общее внешнее состояние телефона?",
        "ask_has_fault": "Есть ли у телефона какие-либо дефекты или неисправности?",
        "btn_yes": "Есть 🔴", "btn_no": "Нет 🟢",
        "write_fault": "Подробно опишите все дефекты:",
        "calculating": "ИИ анализирует данные через интернет, пожалуйста, подождите... ⏳",
        "prompt": "Вы профессиональный эксперт рынка. Оцените телефон по ценам рынка указанной страны в местной валюте и в долларах."
    },
    "en": {
        "ask_os": "Which operating system does your phone use?",
        "ask_model": "Enter the phone model (e.g., Galaxy S24 Ultra or iPhone 15 Pro):",
        "ask_memory": "Select or enter the memory size (e.g., 128GB, 256GB, 512GB):",
        "ask_battery": "Enter iPhone battery health percentage (Numbers only, e.g., 85):",
        "battery_error": "Please enter a valid number (0 to 100):",
        "ask_state": "What is the overall physical condition of the phone?",
        "ask_has_fault": "Does the phone have any defects or issues?",
        "btn_yes": "Yes 🔴", "btn_no": "No 🟢",
        "write_fault": "Describe all defects in detail:",
        "calculating": "AI is analyzing data online, please wait... ⏳",
        "prompt": "You are a professional smartphone market expert. Estimate the price based on the selected country's market in local currency and USD."
    }
}

# --- 1. START: DAVLATNI TANLASH ---
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*[KeyboardButton(d) for d in DAVLATLAR])
    bot.send_message(chat_id, "🌍 Davlatingizni tanlang / Выберите страну / Select your country:", reply_markup=markup)

# --- 2. TILNI TANLASH (3 TA DOIMIY TIL TUGMASI) ---
@bot.message_handler(func=lambda message: message.text in DAVLATLAR)
def choose_language(message):
    chat_id = message.chat.id
    user_data[chat_id]['davlat'] = message.text
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(KeyboardButton("O'zbek tili 🇺🇿"), KeyboardButton("Русский язык 🇷🇺"), KeyboardButton("English 🇺🇸"))
    bot.send_message(chat_id, "🌐 Bot tilini tanlang / Выберите язык бота / Select bot language:", reply_markup=markup)

# --- 3. OPERATSION TIZIM ---
@bot.message_handler(func=lambda message: message.text in ["O'zbek tili 🇺🇿", "Русский язык 🇷🇺", "English 🇺🇸"])
def ask_os(message):
    chat_id = message.chat.id
    
    if "O'zbek" in message.text: lang = "uz"
    elif "Русский" in message.text: lang = "ru"
    else: lang = "en"
    
    user_data[chat_id]['til'] = lang
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Android 🤖"), KeyboardButton("iOS (iPhone) 🍏"))
    bot.send_message(chat_id, TEXTS[lang]['ask_os'], reply_markup=markup)

# --- 4. MODEL ---
@bot.message_handler(func=lambda message: message.text in ["Android 🤖", "iOS (iPhone) 🍏"])
def ask_model(message):
    chat_id = message.chat.id
    user_data[chat_id]['os'] = "iOS" if "iOS" in message.text else "Android"
    lang = user_data[chat_id]['til']
    
    bot.send_message(chat_id, TEXTS[lang]['ask_model'], reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_model)

# --- 5. XOTIRA ---
def get_model(message):
    chat_id = message.chat.id
    user_data[chat_id]['model'] = message.text
    lang = user_data[chat_id]['til']
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(KeyboardButton("128 GB"), KeyboardButton("256 GB"), KeyboardButton("512 GB"))
    bot.send_message(chat_id, TEXTS[lang]['ask_memory'], reply_markup=markup)
    bot.register_next_step_handler(message, get_memory)

# --- 6. BATAREYA YOKI HOLAT ---
def get_memory(message):
    chat_id = message.chat.id
    user_data[chat_id]['xotira'] = message.text
    lang = user_data[chat_id]['til']
    
    if user_data[chat_id]['os'] == "iOS":
        bot.send_message(chat_id, TEXTS[lang]['ask_battery'], reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_battery)
    else:
        user_data[chat_id]['battery'] = "Android"
        bot.send_message(chat_id, TEXTS[lang]['ask_state'], reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_state)

def get_battery(message):
    chat_id = message.chat.id
    lang = user_data[chat_id]['til']
    text = message.text.strip()
    
    if not text.isdigit() or not (0 <= int(text) <= 100):
        bot.send_message(chat_id, TEXTS[lang]['battery_error'])
        bot.register_next_step_handler(message, get_battery)
        return
        
    user_data[chat_id]['battery'] = f"{text}%"
    bot.send_message(chat_id, TEXTS[lang]['ask_state'])
    bot.register_next_step_handler(message, get_state)

# --- 7. AYBI BOR/YO'QLIGI ---
def get_state(message):
    chat_id = message.chat.id
    user_data[chat_id]['holati'] = message.text
    lang = user_data[chat_id]['til']
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton(TEXTS[lang]['btn_yes']), KeyboardButton(TEXTS[lang]['btn_no']))
    bot.send_message(chat_id, TEXTS[lang]['ask_has_fault'], reply_markup=markup)

@bot.message_handler(func=lambda message: any(message.text == TEXTS[l][b] for l in TEXTS for b in ['btn_yes', 'btn_no']))
def process_fault_decision(message):
    chat_id = message.chat.id
    lang = user_data[chat_id]['til']
    
    if message.text == TEXTS[lang]['btn_yes']:
        bot.send_message(chat_id, TEXTS[lang]['write_fault'], reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, calculate_final_price)
    else:
        user_data[chat_id]['ayblari'] = "No defects" if lang == "en" else "Hech qanday aybi yo'q."
        calculate_final_price(message, auto=True)

# --- 8. YAKUNIY BAHOLASH ---
def calculate_final_price(message, auto=False):
    chat_id = message.chat.id
    lang = user_data[chat_id]['til']
    
    if not auto:
        user_data[chat_id]['ayblari'] = message.text
        
    data = user_data[chat_id]
    bot.send_message(chat_id, TEXTS[lang]['calculating'], reply_markup=ReplyKeyboardRemove())
    
    prompt = f"""
    {TEXTS[lang]['prompt']}
    
    Tanlangan bozor (Davlat): {data['davlat']}
    - Model: {data['model']}
    - Memory: {data['xotira']}
    - OS: {data['os']}
    - Battery Health: {data['battery']}
    - Body Condition: {data['holati']}
    - Defects: {data['ayblari']}
    
    Vazifangiz:
    1. Ko'rsatilgan davlat bozoridagi hozirgi ikkinchi qo'l (b/u) real o'rtacha narxni aniqlang.
    2. Nuqsonlarni tuzatish xarajatlarini va usta haqini shu davlat valyutasida hisoblang.
    3. Yakuniy adolatli narxni mahalliy valyutada va dollarda ($) chiqarib bering.
    
    Javobni foydalanuvchi tanlagan tilda ({lang}) chiroyli formatda bering.
    """

    try:
        # Xatolikni bartaraf etish uchun model 'gemini-3.8-flash' ga almashtirildi
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt
        )
        bot.send_message(chat_id, response.text)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")

print("Bot yangi gemini-3.8-flash modeli bilan muvaffaqiyatli ishga tushdi...")
bot.polling(none_stop=True)
