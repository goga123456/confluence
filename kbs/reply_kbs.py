from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_start_and_back_kb() -> ReplyKeyboardMarkup:
    kmain = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('🔙')
    b2 = KeyboardButton('/start')
    kmain.add(b1, b2)
    return kmain


def get_start_kb() -> ReplyKeyboardMarkup:
    kmain2 = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('/start')
    kmain2.add(b1)
    return kmain2

def admin_menu() -> ReplyKeyboardMarkup:
    kadmin = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('Проверить баллы')
    b2 = KeyboardButton('Добавить баллы')
    b3 = KeyboardButton('/start')
    kadmin.add(b1, b2).add(b3)
    return kadmin

def create_and_check() -> ReplyKeyboardMarkup:
    kuser = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('Создать заявку')
    b2 = KeyboardButton('Проверить баллы')
    b3 = KeyboardButton('Админ панель')
    kuser.add(b1, b2).add(b3)
    return kuser