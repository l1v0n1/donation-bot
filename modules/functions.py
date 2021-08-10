import sqlite3
from bot import wallet_p2p

connection = sqlite3.connect('data.db')
q = connection.cursor()

async def first(chat_id):
	q.execute(f"SELECT * FROM users WHERE user_id = {chat_id}")
	result = q.fetchall()
	if len(result) == 0:
			q.execute(f"INSERT INTO users (user_id, bd)"
						f"VALUES ('{chat_id}', '0')")
			connection.commit()

async def pay(chat_id, cost):
	invoice = wallet_p2p.create_invoice(value=cost)
	link = invoice['payUrl'] 
	bid = invoice['billId']
	sql = "UPDATE users SET bd = ? WHERE user_id = ?"
	data = (bid, chat_id)
	q.execute(sql, data)
	connection.commit()
	return link

