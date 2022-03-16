from aiohttp import web
import requests
import redis
import json

# Подключение к хранилищу данных Redis
r = redis.Redis(host='localhost', port=6379)

# Создание приложения
app = web.Application()
# Таблица маршрутов
routes = web.RouteTableDef()

### Обработка запросов ###

# Домашнаяя страница
@routes.get("/")
def hello(request):
    return web.Response(text="Converter")

# Обработка запроса на установку данных по валютам
@routes.get("/database")
def database(request):
    merge_db = request.query['merge']
    try:
        # Если merge==0, то все курсы валют инвалидируются
        if merge_db=='0':
            # Полная очистка хранилища Redis
            r.flushdb()
            # Запись курсов валют относительно Российского рубля с сайта ЦБ РФ в словарь valute_dict
            valute_dict = requests.get('https://www.cbr-xml-daily.ru/latest.js').json()['rates']
            # Добавляем в словарь коэффициент перевода RUR --> RUR, потому что изначально там нет ключа RUR
            valute_dict.update({'RUR': 1.0})
            # Добавляем последовательно все курсы в хранилище Redis
            for valute_from in valute_dict:
                for valute_to in valute_dict:
                    # Ключи вида RURUSD = RUR + USD, то есть Российские рубли переводим в доллары США
                    key = valute_from + valute_to
                    # Если конвертируем Российские рубли во что-то, то коэффициент напрямую переносится из словаря курсов валют
                    if valute_from=='RUR':    
                        r.set(key, valute_dict.get(valute_to))
                    # Если конвертируем что-то в Российские рубли, то будет использоваться обратный коэффициент перевода
                    elif valute_to=='RUR':
                        r.set(key, str(1/valute_dict.get(valute_from)))
                    # Если конвертируются иные валюты, то используем частное коэффициентов (все переводы проходят через Российские рубли)
                    else:
                        r.set(key, str(valute_dict.get(valute_to)/valute_dict.get(valute_from)))
            # Выводим результат в формате Json
            response_obj = {'status': 'succes', 'msg': 'data was invalidate'}
            return web.Response(text=json.dumps(response_obj), status=200)
        # Если merge==1, то нужно обновить лишь изменившиеся курсы относительно старых данных
        elif merge_db=='1':
            # Запись курсов валют относительно Российского рубля с сайта ЦБ РФ в словарь valute_dict
            valute_dict = requests.get('https://www.cbr-xml-daily.ru/latest.js').json()['rates']
            # Добавляем в словарь коэффициент перевода RUR --> RUR, потому что изначально там нет ключа RUR
            valute_dict.update({'RUR': 1.0})
            # Если данные из обновленного словаря валют разнятся с данными из нашего хранилища Redis, то обновляем данные значения
            for valute_from in valute_dict:
                for valute_to in valute_dict:
                    key = valute_from + valute_to
                    # Если конвертируем Российские рубли во что-то, то коэффициент напрямую переносится из словаря курсов валют
                    if valute_from=='RUR':    
                        if valute_dict.get(valute_to)!=float(r.get(key)):
                            r.set(key, valute_dict.get(valute_to))
                    # Если конвертируем что-то в Российские рубли, то будет использоваться обратный коэффициент перевода
                    elif valute_to=='RUR':
                        if (1/valute_dict.get(valute_from))!=float(r.get(key)):
                            r.set(key, str(1/valute_dict.get(valute_from)))
                    # Если конвертируются иные валюты, то используем частное коэффициентов (все переводы проходят через Российские рубли)
                    else:
                        if (valute_dict.get(valute_to)/valute_dict.get(valute_from))!=float(r.get(key)):
                            r.set(key, str(valute_dict.get(valute_to)/valute_dict.get(valute_from)))
            # Выводим результат в формате Json
            response_obj = {'status': 'succes', 'msg': 'data was update'}
            return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        # Вывод ошибки в формате Json, если таковая произошла
        response_obj = {'status':'failed', 'reason':str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)

# Асинхронная обработка запроса на конвертацию Российских рублей в иную валюту
@routes.get("/convert")
async def convert(request):
    try:
        conv_from = request.query['from']
        conv_to = request.query['to']
        amount = request.query['amount']
        key = conv_from + conv_to
        # Результат конвертации
        result = str(float(amount)*float(r.get(key).decode('ASCII')))
        # Выводим результат в формате Json
        response_obj = {'status':'succes', 'from':conv_from, 'to':conv_to, 'amount':amount, 'cost': r.get(key).decode('ASCII'), 'result':result}
        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        # Вывод ошибки в формате Json, если таковая произошла
        response_obj = {'status':'failed', 'reason':str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)

### Конец обработки запросов ###

# Добавление таблицы маршрутов в приложение
app.add_routes(routes)
# Запуск приложения
web.run_app(app, host='0.0.0.0', port=9000)
