import argparse
import os

from flask import Flask, request, redirect
from os import system

app = Flask(__name__)

@app.route("/")
def wel():
  return '''
<center><u><h1>Добро пожаловать в Веб-Квест по поиску сокровищ</h1></u></center><br><br>
<p>
<center>
<h3>Подсказка для первого пути</h3><br>
<b><u>Подсказка 1:</u><br><br>
Кто первым просыпается — это first_word<br>
Кто отдаст жизнь за нас — это second_word<br><br><br>
<b><u>Подсказка 2:</u></b><br><br>
Для всех одна и та же подсказка — Подсказка 1
</b>
</center>
<marquee><h4>Пусть твой путь будет тернистым</h4></marquee>
<!-- 🤔 Всё ещё не нашёл? Не возвращайся сюда -->
'''

@app.route("/vn")
def sss():
  return '''
<center>
<h2><u>Молодец! Ты прошёл на второй уровень</u></h2><br>
<h3>Подсказка для следующего пути</h3><br>
<b><u>Подсказка:</u><br><br>
Кто-то закидывает меня СМС-бомбами. Какой номер я должен отправить, чтобы быть в безопасности? 🤔
</b>
</center>
'''

@app.route("/429")
def bomb():
  return '''
<html>
<head><title>404 Не найдено</title></head>
<body>
<h1>Не найдено</h1>
<p>Запрашиваемый URL не найден на сервере. Проверьте правильность адреса.</p>
</body>
<!-- Это не фейковая страница, реально 404! Но ты уже близко, попробуй /yagf -->
</html>
'''

@app.route("/yagf")
def login():
  return '''
<center><h1>Вход администратора</h1></center><br><br>
<center>
<form action="/validate" method="post">
Имя пользователя<br><br>
<input type=text name=usr><br><br>
Пароль<br><br>
<input type=password name=pwd><br><br><br>
<input type=submit>
</form>
</center>
<!-- Где найти логин? Мой друг знает. Поищи в base64: aHR0cDovL3RyYW5zZmVyLnNoLzFsZ0dibGMvbG9naW4udHh0 -->
'''

@app.route("/validate", methods=["GET", "POST"])
def check():
  if request.method == "GET":
    return "<h1>Доступ запрещён</h1>"
  if request.method == "POST":
    form_data = request.form
    usr = form_data['usr']
    pwd = form_data['pwd']

    if usr == 'vn_daan_vararu' and pwd == 'flag_find_panna_poraru':
      return redirect("/finalpath", code=302)
    else:
      return "<h1>Неверные учётные данные. Попробуй снова на /yagf</h1>"

@app.route("/finalpath")
def last():
  return '''
<center><h1>Поздравляем! Ты добрался до последней страницы CTF</h1></center><br><br><br>
<center>
<form action="/redirect" method="post">
<input type=text name=cmd>
</form>
</center>
<!-- Комментарии здесь бесполезны -->
'''

@app.route("/redirect", methods=["GET", "POST"])
def cmcheck():
  if request.method == 'GET':
    return "<h1>403 Запрещено</h1>"
  if request.method == 'POST':
    form_data = request.form
    if form_data['cmd'] in ['ls', 'cat flagpath', 'cat flag', 'cat flag.txt']:
      system('{} > res.txt'.format(form_data['cmd']))
      a = open('res.txt', 'r').read()
      return f"<h3>{a}</h3>"
    else:
      return redirect("/finalpath", code=302)

@app.route("/dshgfayiurhaejkhbdsajvn")
def winner():
  return "<h2>Перейди по адресу /dshgfayiurhaejkhbdsajvn/{ВАШЕ_ИМЯ}</h2>"

@app.route("/dshgfayiurhaejkhbdsajvn/<name>")
def winnerfirst(name):
  name = name.upper()
  return f'''
<center><h2>🎉ПОЗДРАВЛЯЕМ {name} 🎉 ТЫ СДЕЛАЛ ЭТО!</h2></center><br><br><br>
<center>
<b><h3>ФИНАЛЬНЫЙ ФЛАГ = NeXt_Vn_NeEnGa_DaAn</h3></b><br><br>
<p><b>СКОПИРУЙ ФЛАГ И СДЕЛАЙ СКРИНШОТ ЭТОЙ СТРАНИЦЫ, ОТПРАВЬ В WHATSAPP ЛИЧНО</b></p>
</center><br><br><br><marquee>🥳🥳🥳🥳🥳🥳🥳🥳🥳🥳</marquee>
'''

@app.route("/hall-of-fame")
def hall():
  return "<h1>Зал славы пока пуст...</h1>"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9006)
    args = parser.parse_args()
    app.run(port=args.port)
