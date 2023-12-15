from datetime import datetime
from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from aiogram.utils.executor import start_webhook
import states
from config import TOKEN_API
from kbs.inline_kbs import get_p_or_v_kb
from kbs.reply_kbs import get_start_kb, get_start_and_back_kb, admin_menu, create_and_check
from states import ProfileStatesGroup, AdminStatesGroup

storage = MemoryStorage()
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot,
                storage=storage)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)



#Google sheets
spreadsheet_id = '1KogJCohAesdZjWGWZJNzNk7rs0Dm48SM9TwWh3Cxyp8'
RANGE_NAME_1 = 'Баллы'
credentials = Credentials.from_service_account_file('beelinc-19f9d07341fe.json')
service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
#Google sheets



#Google sheets

async def select(user_id):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME_1
    ).execute()
    values = result.get('values', [])
    for row in values:
        if str(row[0]) == str(user_id):
            return True
    return False


async def append_people(item1, item2, item3):
    values = [
        [item1, item2, item3],
    ]
    request = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME_1,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': values}
    )
    request.execute()

async def select_score(user_id):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME_1
    ).execute()
    values = result.get('values', [])
    for row in values:
        if row[0] == user_id:
            return row[1]
    return None

async def select_all_scores():
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME_1
    ).execute()
    values = result.get('values', [])
    for row in values:
        user_id = row[0]
        ball = row[1]
        f_name = row[2]
        response = f"User ID: {user_id}, Баллы: {ball}, Имя и Фамилия: {f_name}"


async def add_score(user_id, new_score):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME_1
    ).execute()
    values = result.get('values', [])
    for row in values:
        if row[0] == user_id:
            row[1] = str(int(row[1]) + int(new_score))
            break

    body = {
        'values': values
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME_1,
        valueInputOption='RAW',
        body=body
    ).execute()





#Google sheets

@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text="Выберите действие",
                           reply_markup=create_and_check())
    if state is None:
        return
    await state.finish()

@dp.message_handler()
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    if message.text == "Создать заявку":
        await bot.send_message(chat_id=message.from_user.id,
                               text="Опишите что вы нашли за баг ,неточность или ошибку в Confluence",
                               reply_markup=get_start_kb())
        await ProfileStatesGroup.send_text.set()

    if message.text == "Проверить баллы":
        ball = await select_score(str(message.from_user.id))
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"У вас {ball} баллов",
                               reply_markup=get_start_kb())
        await state.finish()
    if message.text == "Админ панель":
        if message.from_user.id == 94766813 or message.from_user.id == 733475703 or message.from_user.id == 624811234:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Выберите действие", reply_markup=admin_menu())
            await AdminStatesGroup.admin_panel.set()
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Вы не администратор")

@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.send_text)
async def check_info(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Это не текст")


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.send_text)
async def oborudovaniye_table_number(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['desc'] = message.text
        await bot.send_message(message.chat.id, text="Напишите свой логин", reply_markup=get_start_and_back_kb())
        await ProfileStatesGroup.send_name.set()


@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.send_name)
async def check_info(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Это не текст")

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.send_name)
async def oborudovaniye_table_number(message: types.Message, state: FSMContext) -> None:
    if message.text == "🔙":
        async with state.proxy() as data:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Опишите что вы нашли за баг ,неточность или ошибку",
                                   reply_markup=get_start_kb())
            await ProfileStatesGroup.send_text.set()
    else:
        async with state.proxy() as data:
            data['name_surname'] = message.text
            await bot.send_message(message.chat.id, text="Что вы хотите отправить фото или видео?",
                                   reply_markup=get_p_or_v_kb())
            await ProfileStatesGroup.send_photo_video.set()




@dp.message_handler(content_types=[*types.ContentTypes.PHOTO, *types.ContentTypes.TEXT],
                    state=ProfileStatesGroup.photo)
async def load_photo(message: types.Message, state: FSMContext) -> None:
    if message.text == "🔙":
        async with state.proxy() as data:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Что вы хотите отправить фото или видео?",
                                   reply_markup=get_p_or_v_kb())
            await ProfileStatesGroup.send_photo_video.set()
    if message.photo:
        async with state.proxy() as data:
            data['it_photo'] = message.photo[0].file_id
            now = datetime.now()
            user_id = message.from_user.id
            response_date = now.strftime("%d.%m.%Y %H:%M:%S")
            await bot.send_photo(chat_id="-1001998156279",
                                 photo=data['it_photo'],
                                 caption=f"Дата и время отклика: {response_date}\n\n"
                                         f"Описание: {data['desc']}\n"
                                         f"Имя и Фамилия: {data['name_surname']}\n"
                                         f"User_id: {user_id}")

            if not await select(user_id):
                await append_people(user_id, "0", data['name_surname'])

            await bot.send_message(chat_id=message.from_user.id, text="Если ваше предложение будет полезным , мы начислим вам баллы", reply_markup=get_start_kb())
            await state.finish()

@dp.message_handler(content_types=[*types.ContentTypes.VIDEO, *types.ContentTypes.TEXT],
                    state=ProfileStatesGroup.video)
async def load_video(message: types.Message, state: FSMContext) -> None:
    if message.text == "🔙":
        async with state.proxy() as data:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Что вы хотите отправить фото или видео?",
                                   reply_markup=get_p_or_v_kb())
            await ProfileStatesGroup.send_photo_video.set()
    if message.video:
        async with state.proxy() as data:
            data['it_video'] = message.video.file_id
            now = datetime.now()
            response_date = now.strftime("%d.%m.%Y %H:%M:%S")
            user_id = message.from_user.id
            # -952509631
            await bot.send_video(chat_id="-1001998156279",
                                 video=data['it_video'],
                                 caption=f"Дата и время отклика: {response_date}\n\n"
                                         f"Описание: {data['desc']}\n"
                                         f"Имя и Фамилия: {data['name_surname']}\n"
                                         f"User_id: {user_id}")

            if not await select(user_id):
                await append_people(user_id, "0", data['name_surname'])

            await bot.send_message(chat_id=message.from_user.id, text="Если ваше предложение будет полезным , мы начислим вам баллы", reply_markup=get_start_kb())
            await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'btn_photo', state=ProfileStatesGroup.send_photo_video)
async def process_callback_photo(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id,
                           text="Отправьте фото вашей проблемы", reply_markup=get_start_and_back_kb())
    await callback_query.message.delete()

    await ProfileStatesGroup.photo.set()


@dp.callback_query_handler(lambda c: c.data == 'btn_video', state=ProfileStatesGroup.send_photo_video)
async def process_callback_video(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id,
                           text="Отправьте видео вашей проблемы", reply_markup=get_start_and_back_kb())
    await callback_query.message.delete()
    await ProfileStatesGroup.video.set()


@dp.callback_query_handler(lambda c: c.data == 'Назад', state=ProfileStatesGroup.send_photo_video)
async def process_callback_video(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await bot.send_message(callback_query.from_user.id, text="Опишите что вы нашли за баг ,неточность или ошибку",
                               reply_markup=get_start_kb())
        await callback_query.message.delete()
        await ProfileStatesGroup.send_text.set()


@dp.callback_query_handler(lambda c: c.data == 'btn_nothing', state=ProfileStatesGroup.send_photo_video)
async def process_callback_nothing(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        now = datetime.now()
        response_date = now.strftime("%d.%m.%Y %H:%M:%S")
        user_id = callback_query.from_user.id
        await bot.send_message(chat_id="-1001998156279",
                               text=f"Дата и время отклика: {response_date}\n\n"
                                    f"Описание: {data['desc']}\n"
                                    f"Имя и Фамилия: {data['name_surname']}\n"
                                    f"User_id: {user_id}")
        if not await select(user_id):
            await append_people(user_id, "0", data['name_surname'])


        await bot.send_message(chat_id=callback_query.from_user.id, text="Если ваше предложение будет полезным , мы начислим вам баллы", reply_markup=get_start_kb())
    await callback_query.message.delete()
    await state.finish()





@dp.message_handler(content_types=['text'], state=AdminStatesGroup.admin_panel)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    if message.text == "Проверить баллы":
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=RANGE_NAME_1
        ).execute()
        values = result.get('values', [])
        response = ""
        for row in values:
            user_id = row[0]
            ball = row[1]
            f_name = row[2]
            response += f"{user_id}|{ball}|{f_name}\n"

        await message.reply(response)

    if message.text == "Добавить баллы":
        await bot.send_message(chat_id=message.from_user.id,
                               text="Введите chat_id", reply_markup=get_start_and_back_kb())
        await AdminStatesGroup.user_id.set()


@dp.message_handler(state=AdminStatesGroup.user_id)
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    if message.text == "🔙":
        async with state.proxy() as data:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Выберите действие", reply_markup=admin_menu())
            await AdminStatesGroup.admin_panel.set()
    else:
        async with state.proxy() as data:
            data['chat_id'] = message.text
            if await select(data['chat_id']):
                await bot.send_message(chat_id=message.from_user.id,
                                       text="Введите количество баллов, которое хотите добавить", reply_markup=get_start_kb())
                await AdminStatesGroup.input_ball.set()

            else:
                await bot.send_message(chat_id=message.from_user.id,
                                       text="Нет такого chat_id")



@dp.message_handler(state=AdminStatesGroup.input_ball)
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['add_ball'] = message.text
        if message.text.isdigit():
            await add_score(data['chat_id'], data['add_ball'])
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Баллы добавлены", reply_markup=get_start_kb())
            await AdminStatesGroup.admin_panel.set()
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Это не число")

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True, max_connections=100)

async def on_shutdown(dispatcher):
    await bot.delete_webhook()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
