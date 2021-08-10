# donation-bot
Bot for donations // Donate Bot Telegram
<h1>Бот для донатов Telegram,  написан на библиотеке aiogram</h1>

<p align="center">Для корректной работы бота установите самую последнюю версию python.
  
```
Донат бот телеграм, с топом донатеров.
Платежная система QIWI P2P
```
### Установка:
```sh
git clone https://github.com/l1v0n1/donation-bot.git

cd donation-bot

pip install -r requirements.txt
```
### Настройка(config.py):

```python
API_TOKEN = '123' # токен от вашего бота в телеграме (взять тут t.me/botfather)
number = '79993331122' # номер киви кошелька
QIWI_SEC_TOKEN = '123=' # секретный ключ p2p https://p2p.qiwi.com
admin = 123 # id админа, узнать тут t.me/userinfobot
admin_name = 'durov' # username админа, без @
```

### Запускаем
```sh
python bot.py
```
