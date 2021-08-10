from aiogram import Bot, Dispatcher, executor, types

menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(types.KeyboardButton('💸 Задонатить'))
menu.add(types.KeyboardButton('🤑 Топ донатеров'))

back = types.ReplyKeyboardMarkup(resize_keyboard=True)
back.add(types.KeyboardButton('Отмена'))

apanel = types.InlineKeyboardMarkup(row_width=3)
apanel.add(
	types.InlineKeyboardButton(text='Рассылка', callback_data='rass'),
	types.InlineKeyboardButton(text='Статистика', callback_data='stats')
    )

choice = types.ReplyKeyboardMarkup(resize_keyboard=True)
choice.add(
	types.KeyboardButton('Анонимный донат'),
	types.KeyboardButton('Отмена')
	)

async def buy(url):
	pay = types.InlineKeyboardMarkup(row_width=3)
	pay.add(
		types.InlineKeyboardButton(text='Оплатить', url=url),
		types.InlineKeyboardButton(text='Проверить оплату', callback_data='check'),
		types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
		)
	return pay