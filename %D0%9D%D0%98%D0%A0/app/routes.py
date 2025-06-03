from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import os

from .models import FlagFound
from . import db
from .utils import lookup_flag, total_flags

bp = Blueprint("main", __name__)

# Автоматическое подключение CTF-сервисов из services/
BASE_PORT = 9000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_DIR = os.path.join(BASE_DIR, "services")

LABS_INFO = [
    {
        "name": "dvwa",
        "description": "Damn Vulnerable Web Application — учебный сервис с уязвимостями.",
        "url": "http://localhost:8081",
        "port": 8081,
        "instruction": """
            <p>DVWA — это учебный сервис для практики веб-уязвимостей.</p>
            <ul>
              <li>Вход: admin/password</li>
              <li>Цель: найти флаги, используя SQLi, XSS и др.</li>
            </ul>
        """,
    },
    {
        "name": "juice-shop",
        "description": "OWASP Juice Shop — современный уязвимый веб-магазин.",
        "url": "http://localhost:3000",
        "port": 3000,
        "instruction": """
            <p>Juice Shop — тренажёр с множеством уязвимостей.</p>
            <ul>
              <li>Вход: нет обязательной регистрации</li>
              <li>Цель: найти и сдать флаги через форму.</li>
            </ul>
        """,
    },
    {
        "name": "wordpress:5.0",
        "description": "",
        "url": "http://localhost:8080",
        "port": 8080,
        "instruction": """
            <p>bwapp</p>
            <ul>
              <li>Вход: нет обязательной регистрации</li>
              <li>Цель: найти и сдать флаги через форму.</li>
            </ul>
        """,
    },
    {
        "name": "Reflective-xss-cookie-steal-ctf",
        "description": "Рефлексивная XSS-уязвимость, крадущая cookie.",
        "instruction": """
                <p>В этом задании реализована рефлексивная XSS-уязвимость.</p>
                <ul>
                  <li>Передавайте имя в URL через параметр <code>?name=</code>.</li>
                  <li>Попробуйте вставить: <code>&lt;script&gt;alert(1)&lt;/script&gt;</code></li>
                  <li>Задача: отобразить флаг на странице через внедрение JavaScript.</li>
                </ul>
            """,
        "url": "http://localhost:9000",
        "port": 9000
    },
    {
        "name": "cors-exploit-ctf",
        "description": "Уязвимость CORS и кража данных через межсайтовые запросы.",
        "instruction": """
                <p>Данный сервис демонстрирует опасность неправильной настройки CORS.</p>
                <ul>
                  <li>Создайте HTML-страницу, которая отправляет <code>fetch()</code> POST-запрос на <code>/steal</code>.</li>
                  <li>В теле запроса передайте cookie или другие приватные данные.</li>
                  <li>Флаг будет передан в этих данных</li>
                </ul>
            """,
        "url": "http://localhost:9001",
        "port": 9001
    },
    {
        "name": "sqli_ctf",
        "description": "SQL-инъекция на странице входа.",
        "instruction": """
                <p>На странице входа реализована уязвимость SQL-инъекции.</p>
                <ul>
                  <li>Попробуйте ввести в поле логина: <code>' OR 1=1 --</code></li>
                  <li>Пароль можно оставить пустым или любой.</li>
                  <li>После успешной инъекции вы попадёте на страницу с флагом.</li>
                </ul>
            """,
        "url": "http://localhost:9002",
        "port": 9002
    },
    {
        "name": "ss_ctf",
        "description": "Доступ к файлам через предсказуемые URL.",
        "instruction": """
                <p>Сервис предоставляет доступ к файлам по пути в URL.</p>
                <ul>
                  <li>Попробуйте открыть: <code>/challenge/folder/flag.txt</code></li>
                  <li>Или переберите директории вручную.</li>
                  <li>Флаг хранится в одном из текстовых файлов.</li>
                </ul>
            """,
        "url": "http://localhost:9003",
        "port": 9003
    },
    {
        "name": "ssti-flask-ctf",
        "description": "Уязвимость SSTI в шаблонизаторе Jinja2.",
        "instruction": """
                <p>На сайте используется Jinja-шаблонизация с прямым вводом данных.</p>
                <ul>
                  <li>Попробуйте вставить шаблонный код: <code>{{7*7}}</code></li>
                  <li>Цель: выполнить SSTI (Server Side Template Injection) и получить флаг</li>
                  <li>Флаг находится в переменной окружения или шаблоне</li>
                </ul>
            """,
        "url": "http://localhost:9004",
        "port": 9004
    },
    {
        "name": "vn-break-fort-ctf",
        "description": "Скрытые маршруты и задания на внимательность.",
        "instruction": """
                <p>Вам предстоит пройти по страницам сайта в поисках подсказок.</p>
                <ul>
                  <li>Ищите скрытые ссылки, элементы, закодированные строки.</li>
                  <li>Флаг спрятан в одном из финальных шагов цепочки переходов.</li>
                  <li>Можно использовать инструменты разработчика для анализа DOM.</li>
                </ul>
            """,
        "url": "http://localhost:9005",
        "port": 9005
    },
    {
        "name": "web-treasure-hunt-ctf",
        "description": "Пошаговая охота за флагом в веб-интерфейсе.",
        "instruction": """
                <p>Вам предстоит пройти квест из нескольких страниц, чтобы найти флаг.</p>
                <ul>
                  <li>Переходите по страницам, находите ключи, решайте загадки.</li>
                  <li>Флаг будет выдан на финальной странице цепочки.</li>
                </ul>
            """,
        "url": "http://localhost:9006",
        "port": 9006
    },


]

# Автоматически добавляем кастомные CTF-сервисы из app/services
# for idx, dirname in enumerate(sorted(os.listdir(SERVICES_DIR))):
#     full_path = os.path.join(SERVICES_DIR, dirname)
#     if not os.path.isdir(full_path):
#         continue
#     port = BASE_PORT + idx
#     LABS_INFO.append({
#         "name": dirname,
#         "description": f"CTF-сервис {dirname}",
#         "url": f"http://localhost:{port}",
#         "port": port,
#         "instruction": f"<p>CTF {dirname} — autogenerated.</p>",
#     })


@bp.route("/quests")
@login_required
def quests():
    return render_template("quest.html", labs=LABS_INFO)

@bp.route("/instructions")
@login_required
def instructions():
    return render_template("instructions.html", labs=LABS_INFO)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/dashboard")
@login_required
def dashboard():
    flags = current_user.flags
    progress = current_user.progress(total_flags())
    total = total_flags()
    return render_template("dashboard.html", flags=flags, progress=progress, total_flags=total)

@bp.route("/submit_flag", methods=["POST"])
@login_required
def submit_flag():
    flag_text = request.form.get("flag", "").strip()
    if not flag_text:
        return jsonify(status="error", message="Флаг пустой"), 400

    found = lookup_flag(flag_text)
    if not found:
        return jsonify(status="error", message="Неверный флаг"), 400

    if FlagFound.query.filter_by(user_id=current_user.id, flag=flag_text).first():
        return jsonify(status="error", message="Уже засчитан"), 400

    ff = FlagFound(user_id=current_user.id,
                   flag=found.flag,
                   lab_name=found.service,
                   flag_type=found.flag_type)
    db.session.add(ff)
    db.session.commit()

    return jsonify(status="success", message=f"Принято: {found.service}/{found.flag_type}")
