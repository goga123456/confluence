from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_p_or_v_kb() -> InlineKeyboardMarkup:
    kb2 = InlineKeyboardMarkup(resize_keyboard=True)
    b1 = InlineKeyboardButton('Фото', callback_data='btn_photo')
    b2 = InlineKeyboardButton('Видео', callback_data='btn_video')
    b3 = InlineKeyboardButton('Ни то ни другое', callback_data='btn_nothing')
    b4 = InlineKeyboardButton('Назад', callback_data='Назад')
    kb2.add(b1, b2).add(b3).add(b4)
    return kb2


