from aiogram.dispatcher.filters.state import StatesGroup, State


class ProfileStatesGroup(StatesGroup):
    create_or_check = State()
    send_text = State()
    send_name = State()
    send_photo_video = State()
    photo = State()
    video = State()
    check = State()

class AdminStatesGroup(StatesGroup):
    admin_panel = State()
    add_ball = State()
    user_id = State()
    input_ball = State()
    check_ball = State()
