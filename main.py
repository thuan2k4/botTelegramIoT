from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram import types, F
import requests
import json
import socket

# Khởi tạo Bot và Dispatcher
API_Key = '7106176859:AAHKvfQt-2DcMNf8HxY3_QdzuOHh1nEilNM'
bot = Bot(token=API_Key)
dp = Dispatcher()

url_host = f'http://{str(socket.gethostbyname(socket.gethostname()))}:5000'

#Menu section
commands = [
    BotCommand(command="start", description="Bắt đầu sử dụng bot")
]

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.delete()
    txt = ''
    with open('welcome.txt', 'r', encoding='utf-8') as file:
        txt = ''.join(file.readlines())
        
        
    btn_weather = InlineKeyboardButton(text = 'Nhiệt Độ/ Độ Ẩm', callback_data='weather')
    btn_mqt = InlineKeyboardButton(text = 'Giá trị chất lượng không khí', callback_data='mqt135')
    btn_pir = InlineKeyboardButton(text = 'Lịch sử phát hiện chuyển động', callback_data='pir')
    btn_toggle = InlineKeyboardButton(text = "Bật/Tắt Đèn", callback_data='toggle')
    
    btn = InlineKeyboardMarkup(inline_keyboard=[[btn_weather, btn_mqt ], [btn_pir, btn_toggle]])
    
    await message.answer(txt, reply_markup=btn)
    

@router.callback_query(lambda x : x.data in ['weather', 'mqt135', 'pir', 'home'])
async def handle_inline_button(callback : types.CallbackQuery):

    if callback.data == 'weather':
        url = url_host + '/api/weather'
        response = requests.get(url=url)
        data_weather = response.json()
        response.close()
        msg = f"Nhiệt Độ Hiện Tại là: {data_weather.get('temperature')}℃\nĐộ Ẩm Hiện Tại là: {data_weather.get('humidity')}%"
        await callback.message.answer(msg)
        
    elif callback.data == 'mqt135':
        url = url_host + '/api/mqt135'
        response = requests.get(url=url)
        data_mqt = response.json()
        response.close()
        msg = f"Chỉ số chất lượng không khí hiện tại là: {data_mqt.get('value')} ppm"
        await callback.message.answer(msg)
    
    elif callback.data == 'pir':
        url = url_host + '/data_pir'
        response = requests.get(url=url)
        history = response.json()
        response.close()
        
        for item in history['data']:
            times = item['time']
            areas = item['area']
        
        msg = ''
        for time, area in zip(times,areas):
            msg += f"Thời gian: {time}, Khu Vực: {area}\n"
        
        await callback.message.answer(msg)
    
    else:
        callback.message.delete()
        await start_handler(callback.message)
        
    await callback.answer()
    
@router.callback_query(F.data == 'toggle')
async def toggle_led(callback: types.CallbackQuery):

    btn_led_main = InlineKeyboardButton(text = 'Led0', callback_data='led_main')
    btn_led_d7 = InlineKeyboardButton(text = 'Led1', callback_data='led_d7')
    btn_led_d8 = InlineKeyboardButton(text = 'Led2', callback_data='led_d8')
    btn_back = InlineKeyboardButton(text = 'Quay về Home', callback_data='home')
    
    btn = InlineKeyboardMarkup(inline_keyboard=[[btn_led_main, btn_led_d7 ], [btn_led_d8, btn_back]])

    try:
        await callback.message.edit_text(
            "Chọn một đèn hoặc quay về Home:",
            reply_markup=btn
        )
    except Exception as e:
        print(f"Error: {e}")
    
    await callback.answer()

@router.callback_query(F.data == 'Home')
async def go_home(callback: types.CallbackQuery):
    await toggle_led(callback)
    await callback.answer()

@router.callback_query(F.data == 'led_main')
async def led_main(callback: types.CallbackQuery):
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Turn On", callback_data="turn_on_main"), InlineKeyboardButton(text="Turn Off", callback_data="turn_off_main")],
            [InlineKeyboardButton(text="Back", callback_data="Home")]
        ]
    )
    
    url = url_host + '/api/change_status_led'
    response = requests.get(url=url)
    data = response.json().get('Led_Main')
    response.close()

    status = "On" if data == 0 else 'Off'
        
    try:
        await bot.send_message(callback.from_user.id, f"Bật tắt Led0\n Trạng thái: {status}", reply_markup=keyboard)
        await callback.message.delete()
    except Exception as e:
        print(f"Error: {e}")
        
    await callback.answer()
    
@router.callback_query(F.data.in_(['turn_on_main', 'turn_off_main']))
async def handle_led0(callback : types.CallbackQuery):
    
    url = url_host + '/api/change_status_led/Led_Main/'
    
    if callback.data == 'turn_on_main':
        
        url += 'On'
    
    else:
        
        url += 'Off'
    
    try:
        response = requests.put(url=url)
        print(response.text)
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        
    finally:
        response.close()
    

    
    await led_main(callback)
    await callback.answer()


@router.callback_query(F.data == 'led_d7')
async def led_d7(callback: types.CallbackQuery):
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Turn On", callback_data="turn_on_d7"), InlineKeyboardButton(text="Turn Off", callback_data="turn_off_d7")],
            [InlineKeyboardButton(text="Back", callback_data="Home")]
        ]
    )
    
    url = url_host + '/api/change_status_led'
    response = requests.get(url=url)
    data = response.json().get('Led_D7')
    response.close()

    status = "On" if data == 1023 else 'Off'
    try:
        await bot.send_message(callback.from_user.id, f"Bật tắt Led1\n Trạng thái: {status}", reply_markup=keyboard)
        await callback.message.delete()
    except Exception as e:
        print(f"Error: {e}")
        
    await callback.answer()

@router.callback_query(F.data.in_(['turn_on_d7', 'turn_off_d7']))
async def handle_led1(callback : types.CallbackQuery):
    
    url = url_host + '/api/change_status_led/Led_D7/'
    
    if callback.data == 'turn_on_d7':
        url += 'On'

    else:
        url += 'Off'

    
    try:
        response = requests.put(url=url)
        print(response.text)
        
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        
    finally:
        response.close()
    
    await led_d7(callback)
    await callback.answer()

@router.callback_query(F.data == 'led_d8')
async def led_d8(callback: types.CallbackQuery):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Turn On", callback_data="turn_on_d8"), InlineKeyboardButton(text="Turn Off", callback_data="turn_off_d8")],
            [InlineKeyboardButton(text="Back", callback_data="Home")]
        ]
    )
    url = url_host + '/api/change_status_led'
    response = requests.get(url=url)
    data = response.json().get('Led_D8')
    response.close()

    status = "On" if data == 1023 else 'Off'
    
    try:
        await bot.send_message(callback.from_user.id, f"Bật tắt Led2\n Trạng thái: {status}", reply_markup=keyboard)
        await callback.message.delete()
    except Exception as e:
        print(f"Error: {e}")
        
    await callback.answer()

@router.callback_query(F.data.in_(['turn_on_d8', 'turn_off_d8']))
async def handle_led2(callback : types.CallbackQuery):
    
    url = url_host + '/api/change_status_led/Led_D8/'
    
    if callback.data == 'turn_on_d8':
        url += 'On'
    else:
        url += 'Off'
    
    try:
        response = requests.put(url=url)
        print(response.text)
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        
    finally:
        
        response.close()
    
    await led_d8(callback)
    await callback.answer()
    

if __name__ == "__main__":

    print(f'Stream On')
    dp.include_router(router)
    dp.run_polling(bot)
