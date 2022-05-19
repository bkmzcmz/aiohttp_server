# aiohttp_server

Само задание находится в файле task.pdf.

Так как код вышел небольшой, я решил все делать в одном файле main.py, просто тщательно комментируя все свои действия.

Данные курсов валют я брал с сайта РБК по данным ЦБ РФ. Единственный недостаток - при получении JSON файла с курсами валют, все цены указаны относительно Российского рубля, то есть используя лишь эти данные нельзя напрямую перевести, например, тенге в доллары. Но я воспользовался тем, то у ЦБ РФ отсутствует разница между покупкой и продажей валюты, а значит коэффициентами перевода можно "играть" как хочется.

Например, чтобы перевести тенге в доллары, я сначала переводил тенге в рубли, а потом полученную сумму рублей в доллары. В программе это реализуется так: тенге я делю на коэффициент перевода рублей в тенге, а потом полученную сумму умножаю на коэффициент перевода рублей в доллары. То есть коэффициент перевода тенге в доллары равен (коэф. перевода рублей в доллары)/(коэф. перевода рублей в тенге). Именно так я заполняю хранилище данных коэффициентами всеми видами перевода, а потом просто напрямую использую полученные коэффициенты перевода. 

В файле server_test.pdf находятся скрины теста работоспособности данного back-end`а.
