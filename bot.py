import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import API_TOKEN, number, QIWI_SEC_TOKEN, admin, admin_name
import modules.keyboard as kb
import modules.functions as fc

import sqlite3
from qiwipyapi import Wallet

storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

connection = sqlite3.connect('data.db')
q = connection.cursor()
q.execute(
	'CREATE TABLE IF NOT EXISTS users (user_id integer, bd text, donated int, name text);')
connection.commit()

wallet_p2p = Wallet(number, p2p_sec_key=QIWI_SEC_TOKEN)

class don(StatesGroup):
	name = State()
	cost = State()
	anon = State()
	rasst = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
	await fc.first(message.from_user.id)
	if message.from_user.id == admin:
		await message.answer("Привет, это бот для того, чтобы вы могли задонатить тс'у\nМой исходный код - https://github.com/l1v0n1/donation-bot-telegram\n\nДля входа в админку введите: /admin", reply_markup=kb.menu)
	else:
		await message.answer("Привет, это бот для того, чтобы вы могли задонатить тс'у\nМой исходный код - https://github.com/l1v0n1/donation-bot-telegram", reply_markup=kb.menu)

@dp.message_handler(commands=['admin'])
async def adminstration(message: types.Message):
	if message.from_user.id == admin:
		await message.answer('Добро пожаловать в админ панель.', reply_markup=kb.apanel)
	else:
		await message.answer('Черт! Ты меня взломал :(')

@dp.message_handler(content_types=['text'], text='🤑 Топ донатеров')
async def donatorstop(message: types.Message):
	q.execute(f"SELECT user_id, donated, name FROM users order by donated desc")
	response = q.fetchall()
	top_list = []
	for id, amount, name in response:
		if name != None:
			donator = f"[{name}](tg://user?id={id})"
		else:
			donator = 'Аноним'
		if amount != None:
			top_list.append("--------------\nДонатер: {}\nЗадонатил: {}₽".format(donator, amount))
		else:
			pass
	msg = '\n'.join(top_list)
	await message.answer('Топ донатеров:\n{}'.format(msg), parse_mode='Markdown')

@dp.message_handler(content_types=['text'], text='💸 Задонатить')
async def donation(message: types.Message, state: FSMContext):
	await message.answer('Желаете как-то назваться? Если да, то напишите мне как вас звать...\nЕсли же желаете остаться анонимным, то нажмите соответсвующую кнопку', reply_markup=kb.choice)
	await don.name.set()

@dp.message_handler(state=don.name)
async def donation_name(message: types.Message, state: FSMContext):
	if message.text == 'Отмена':
		await message.answer('Отмена! Возвращаю назад.', reply_markup=kb.menu)
		await state.finish()
	elif message.text == 'Анонимный донат':
		await message.answer('Хорошо, вы останетесь анонимным.\nВведите сумму, которую хотите задонатить..', reply_markup=kb.back)
		await don.anon.set()
	else:
		res = q.execute("SELECT name FROM users WHERE lower(name) LIKE lower(?)", [message.text.lower()]).fetchall()
		if len(res) == 0:
			if len(message.text) <= 20:
				if not message.text.startswith('/'):
					q.execute('UPDATE users SET name = ? WHERE user_id = ?', (message.text.lower(), message.from_user.id))
					connection.commit()
					await message.answer('Хорошо, теперь введите сумму, которую хотите задонатить..', reply_markup=kb.back)
					await don.cost.set()
				else:
					await message.answer('Вы используете запрещенные символы, введите другое имя')
			else:
				await message.answer('Придумайте имя короче, до 20 символов..')
		else:
			await message.answer('Данное имя уже занято, попробуйте другое.')



@dp.message_handler(state=don.anon)
async def donation_anonimous(message: types.Message, state: FSMContext):
	if message.text == 'Отмена':
		await message.answer('Отмена! Возвращаю назад.', reply_markup=kb.menu)
		await state.finish()
	else:
		if message.text.isdigit():
			link = await fc.pay(message.from_user.id, message.text)
			keyboard = await kb.buy(link)
			await message.answer('...', reply_markup=kb.menu)
			await message.answer(f'Счет для оплаты выставлен, перейдите по ссылке для оплаты', reply_markup=keyboard)
			await state.finish()
		else:
			await message.answer('Вы ввели не число! Введите сумму, которую хотите задонатить.')

@dp.message_handler(state=don.cost)
async def donation_process(message: types.Message, state: FSMContext):
	if message.text == 'Отмена':
		await message.answer('Отмена! Возвращаю назад.', reply_markup=kb.menu)
		await state.finish()
	else:
		if message.text.isdigit():
			link = await fc.pay(message.from_user.id, message.text)
			keyboard = await kb.buy(link)
			await message.answer('...', reply_markup=kb.menu)
			await message.answer(f'Счет для оплаты выставлен, перейдите по ссылке для оплаты', reply_markup=keyboard)
			await state.finish()
		else:
			await message.answer('Вы ввели не число! Введите сумму, которую хотите задонатить.')

@dp.callback_query_handler(lambda call: call.data == 'check')
async def checkpay(call):
	try:
		re = q.execute(f"SELECT bd FROM users WHERE user_id = ?", (call.message.from_user.id, )).fetchone()
		status = wallet_p2p.invoice_status(bill_id=re[0])
		a = status['status']['value']
		am = status['amount']['value']
		amount = int(float(am))
		if a == 'WAITING':
			await call.message.answer('Ошибка! Платёж не найден.')
		elif a == 'PAID':
			q.execute('UPDATE users SET bd = 0 WHERE user_id = ?', (call.message.from_user.id, ))
			connection.commit()
			q.execute('UPDATE users SET donated = ? WHERE user_id = ?', (amount, call.message.from_user.id))
			connection.commit()
			await call.message.answer('Оплата успешно найдена, благодарим вас за поддержку!\nВы будете занесены в топ донатеров.')
			await bot.send_message(admin, 'Новый донат!\nДонатер: {}\nID: {}\nСумма: {}₽\n'.format(call.message.from_user.mention, call.message.from_user.id, amount))
		elif a == 'EXPIRED':
			q.execute(f'UPDATE users SET bd = 0 WHERE user_id = ?', (call.message.from_user.id, ))
			connection.commit()
			await call.message.answer('Время жизни счета истекло. Счет не оплачен', reply_markup=kb.menu)
		elif a == 'REJECTED':
			q.execute(f'UPDATE users SET bd = 0 WHERE user_id = ?', (call.message.from_user.id, ))
			connection.commit()
			await call.message.answer('Счет отклонен', reply_markup=kb.menu)
		elif a == 'UNPAID':
			q.execute(f'UPDATE users SET bd = 0 WHERE user_id = ?', (call.message.from_user.id, ))
			connection.commit()
			await call.message.answer('Ошибка при проведении оплаты. Счет не оплачен', reply_markup=kb.menu)
	except Exception as err:
		await call.message.answer('Ошибка!')

@dp.callback_query_handler(lambda call: call.data == 'cancel')
async def back(call):
	try:
		billid = q.execute('SELECT bd FROM users WHERE user_id = ?', (call.message.from_user.id, )).fetchone()
		connection.commit()
		wallet_p2p.cancel_invoice(bill_id=billid[0])
		q.execute('UPDATE users SET bd = 0 WHERE user_id = ?', (call.message.from_user.id, ))
		connection.commit()
		await call.message.answer('Хорошо, выставленные счета отклонены...', reply_markup=kb.menu)
	except Exception as err:
		await call.message.answer('Ошибка!')

@dp.callback_query_handler(lambda call: call.data == 'rass')    
async def usender(call):
	await call.message.answer('Введите текст для рассылки.\n\nДля отмены нажмите кнопку ниже 👇', reply_markup=kb.back)
	await don.rasst.set()

@dp.message_handler(state=don.rasst)
async def process_sedning(message: types.Message, state: FSMContext):
	q.execute(f'SELECT user_id FROM users')
	row = q.fetchall()
	connection.commit()
	if message.text == 'Отмена':
		await message.answer('Отмена! Возвращаю в главное меню.', reply_markup=kb.menu)
		await state.finish()
	else:
		info = row
		await message.answer('Начинаю рассылку...')
		for i in range(len(info)):
			try:
				await bot.send_message(info[i][0], str(message.text))
			except:
				pass
		await message.answer('Рассылка завершена.', reply_markup=kb.menu)
		await state.finish()

@dp.callback_query_handler(lambda call: call.data =='stats')
async def statistics(call):
	re = q.execute(f'SELECT * FROM users').fetchall()
	kol = len(re)
	connection.commit()
	await call.message.answer(f'Всего пользователей: {kol}')

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)