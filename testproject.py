import telebot
import requests
import traceback
import json

TOKEN = "6044513246:AAGbwmHCGJrtrCsnt3yWtdwCvGv7zPMh1Gs"

keys = {
    'доллар': 'USD',
    'евро': 'EUR',
    'рубль': 'RUB',
}


class Convertor:
    @staticmethod
    def get_price(base, sym, amount):
        try:
            base_key = keys[base.lower()]
        except KeyError:
            raise APIException(f"Валюта {base} не найдена!")

        try:
            sym_key = keys[sym.lower()]
        except KeyError:
            raise APIException(f"Валюта {sym} не найдена!")

        if base_key == sym_key:
            raise APIException(f'Невозможно перевести одинаковые валюты {base}!')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}!')
        r = requests.request(f"https://api.exchangeratesapi.io/latest?base={base_key}&symbols={sym_key}")
        resp = json.loads(r.content)
        new_price = resp['rates'][sym_key] * amount
        new_price = round(new_price, 3)
        message = f"Цена {amount} {base} в {sym} : {new_price}"
        return message


class APIException(Exception):
    pass


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     f"Привет, {message.chat.username}, чтобы воспользоваться ботом напишите:\n <имя валюты, цену которой Вы хотите узнать> <имя валюты, в которой надо узнать цену первой валюты> <количество первой валюты>\n Чтобы увидеть список доступных валют, введите /values")


@bot.message_handler(commands=['values'])
def send_values(message):
    bot.send_message(message.chat.id, f'USD\nEUR\nRUB')


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    values = message.text.split(' ')
    try:
        if len(values) != 3:
            raise APIException('Неверное количество параметров')

        answer = Convertor.get_price(*values)
    except APIException as e:
        bot.reply_to(message, f"Ошибка в команде:\n{e}")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        bot.reply_to(message, f"Неизвестная ошибка:\n{e}")
    else:
        bot.reply_to(message, answer)


bot.polling()
