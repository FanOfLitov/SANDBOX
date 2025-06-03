import argparse
from flask import Flask, request, redirect, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return '''
<center>
<h1> Предыстория </h1>
<br><p>
<b>
<h3>
"VN" (Ванаккам Нанба) — так все ласково называют злодея. В день, когда был удалён его первый YouTube-канал "Jtechcode", он начал ежегодно похищать одного ребёнка и приносить его в жертву. И в этом году он снова похитил мальчика по имени Flag и запер его в мощной крепости. Он всегда убивает жертву через два дня после похищения, так что у тебя есть только 2 дня, чтобы спасти его!
<br><br>
<h2> Осталось 2 дня!! </h2>
<br><br>
Сначала иди на /first. Там будет первая стена крепости. Преодолей все уровни защиты, чтобы попасть к VN и спасти флаг! Удачи!
</h3>
</b>
</center>
'''

@app.route("/first", methods=["GET", "PUT", "POST"])
def welcome():
    if request.method == "GET":
        return "<center><h1>Вход в крепость VN</h1><br><br><h2>🚫 ДОСТУП ЗАПРЕЩЁН 🚫<br><br>🚫 ПОПРОБУЙ С ДРУГОГО МЕТОДА 🚫</h2></center>"
    if request.method == "PUT":
        return redirect("/second_wall", code=302)
    if request.method == "POST":
        return "<center><h1>🚫 ХОРОШАЯ ПОПЫТКА 🚫<br><br>НО ЭТА СТЕНА ЗАЩИЩЕНА<br>🚫 ПРОЙТИ НЕЛЕГКО 🚫</h1></center>"

@app.route("/second_wall")
def second_wall():
    return render_template("kidnap.html")

@app.route("/msgfromflag")
def msg():
    return '<center><h1>Привет! Я — флаг</h1><p>Мне страшно, здесь темно. Пожалуйста, помоги мне! Меня похитил хакер в маске. Он говорит, что взломал NASA. Поспеши!</p><a href="/next_step">Далее -></a></center>'

@app.route("/next_step")
def next_step():
    return render_template("login.html")

@app.route("/login.js")
def script():
    return render_template("login.js")

@app.route("/puzzle")
def puzzle():
    return '''<center><h1>🎉 Ты прошёл Вторую Стену 🎉</h1>
<h2>Собери слово из букв:</h2>
<h3>С, Е, Т, Ь, И, К, О</h3>
<form action="/validate" method="post">
<label>Введите слово:</label><br>
<input type=text name=word><br>
<input type=submit value=Отправить>
</form></center>'''

@app.route("/validate", methods=["POST"])
def validate():
    word = request.form.get("word")
    if word.upper() == "СЕТЬЮИК":  # Желаемое слово можно заменить
        return redirect("/alert")
    return redirect("/puzzle")

@app.route("/alert")
def alert():
    return '''<center><h1>🎉 Ты прошёл Третью Стену 🎉</h1>
<p>Здесь есть только один бот. Он спит и не различает входящих и выходящих.<br>Разбуди его фразой: <b>"Allow Me Inside"</b></p>
<form action="/check" method="post">
<input type=text name=value><br>
<input type=submit value="Разбудить">
</form></center>'''

@app.route("/check", methods=["POST"])
def check():
    val = request.form.get("value")
    if "<" in val:
        return "<center><h1>🚨 XSS ОБНАРУЖЕН 🚨</h1></center>"
    elif val == "%3Cscript%3Ealert%28%27Allow+Me+Inside%27%29%3C%2Fscript%3E":
        return redirect("/final")
    return "<center><h1>Бот не проснулся. Попробуй лучше.</h1></center>"

@app.route("/final")
def final():
    return '''<script>alert('Бот впустил тебя!')</script>
<center><h1>🎉 Последняя Стена Пройдена 🎉</h1>
<h2>Кто может убить VN?</h2>
<form action="/kill" method="post">
<input type=text name=name><br>
<input type=submit value="Убить VN">
</form></center>'''

@app.route("/kill", methods=["POST"])
def kill():
    name = request.form.get("name")
    if name == "127.0.0.1":
        return redirect("/flag")
    return redirect("/final")

@app.route("/flag")
def flag():
    return render_template("final.html")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9005)
    args = parser.parse_args()
    app.run(port=args.port)
