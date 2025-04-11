from flask import Flask, render_template, request, jsonify, session
import docker
import webbrowser
from threading import Timer
import random
import string
import os
import json
from flask import redirect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

USERS_FILE = 'users.json'

# Функции работы с пользователями
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Конфигурация уязвимых образов
VULNERABLE_IMAGES = {
    'dvwa': {
        'image': 'vulnerables/web-dvwa',
        'description': 'Damn Vulnerable Web App',
        'port': 80,
        'vulns': ['SQL Injection', 'XSS', 'CSRF', 'File Inclusion'],
        'flags': {
            'sqli': 'FLAG{SQl1_3xpl01t3d_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'xss': 'FLAG{XSS_3xpl01t3d_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'csrf': 'FLAG{CSRF_3xpl01t3d_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}'
        }
    },
    'bwapp': {
        'image': 'raesene/bwapp',
        'description': 'Buggy Web Application',
        'port': 80,
        'vulns': ['SQL Injection', 'XSS', 'Command Injection'],
        'flags': {
            'sqli': 'FLAG{BWAPP_SQL1_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'xss': 'FLAG{BWAPP_XSS_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'cmd': 'FLAG{BWAPP_CMD_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}'
        }
    },
    'juiceshop': {
        'image': 'bkimminich/juice-shop',
        'description': 'OWASP Juice Shop',
        'port': 3000,
        'vulns': ['NoSQL Injection', 'XSS', 'Broken Authentication'],
        'flags': {
            'nosqli': 'FLAG{NoSQL1_Juice_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'xss': 'FLAG{Juice_XSS_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'auth': 'FLAG{Juice_Auth_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}'
        }
    },
    'webgoat': {
        'image': 'webgoat/webgoat-8.0',
        'description': 'OWASP WebGoat',
        'port': 8080,
        'vulns': ['SQL Injection', 'XXE', 'JWT Vulnerabilities'],
        'flags': {
            'sqli': 'FLAG{WebGoat_SQL1_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'xxe': 'FLAG{WebGoat_XXE_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'jwt': 'FLAG{WebGoat_JWT_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}'
        }
    },
    'mutillidae': {
        'image': 'citizenstig/nowasp',
        'description': 'OWASP Mutillidae II',
        'port': 80,
        'vulns': ['SQL Injection', 'XSS', 'LFI'],
        'flags': {
            'sqli': 'FLAG{Mutillidae_SQL1_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'xss': 'FLAG{Mutillidae_XSS_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'lfi': 'FLAG{Mutillidae_LFI_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}'
        }
    },
    'vulnerable_wordpress': {
        'image': 'wpscanteam/vulnerablewordpress',
        'description': 'Vulnerable WordPress',
        'port': 80,
        'vulns': ['XML-RPC Abuse', 'User Enumeration', 'Plugin Vulnerabilities'],
        'flags': {
            'xmlrpc': 'FLAG{WP_XMLRPC_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'enum': 'FLAG{WP_Enum_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'plugin': 'FLAG{WP_Plugin_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}'
        }
    },
    'vulnerable_joomla': {
        'image': 'greggm/vulnerable-joomla',
        'description': 'Vulnerable Joomla',
        'port': 80,
        'vulns': ['SQL Injection', 'Template Vulnerabilities', 'Component Vulnerabilities'],
        'flags': {
            'sqli': 'FLAG{Joomla_SQL1_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'template': 'FLAG{Joomla_Template_' + ''.join(
                random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'component': 'FLAG{Joomla_Component_' + ''.join(
                random.choices(string.ascii_letters + string.digits, k=8)) + '}'
        }
    },
    'hackazon': {
        'image': 'citizenstig/hackazon',
        'description': 'Hackazon',
        'port': 80,
        'vulns': ['SQL Injection', 'XSS', 'CSRF'],
        'flags': {
            'sqli': 'FLAG{Hackazon_SQL1_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'xss': 'FLAG{Hackazon_XSS_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}',
            'csrf': 'FLAG{Hackazon_CSRF_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '}'
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html', images=VULNERABLE_IMAGES, username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()
        if username in users:
            return jsonify({'status': 'error', 'message': 'Пользователь уже существует'}), 400

        users[username] = generate_password_hash(password)
        save_users(users)

        return jsonify({'status': 'success', 'message': 'Регистрация успешна!'})
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    users = load_users()
    if username not in users or not check_password_hash(users[username], password):
        return jsonify({'status': 'error', 'message': 'Неверные учетные данные'}), 401

    session['username'] = username
    return jsonify({'status': 'success', 'message': 'Вход выполнен'})


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/create', methods=['POST'])
def create_instance():
    if 'username' not in session:
        return jsonify({'error': 'Вы не авторизованы'}), 403

    image_id = request.form.get('image')
    if image_id not in VULNERABLE_IMAGES:
        return jsonify({'error': 'Invalid image'}), 400

    image_config = VULNERABLE_IMAGES[image_id]

    try:
        client = docker.from_env()

        # Генерируем случайные флаги для сессии
        session['flags'] = image_config['flags']

        # Запускаем контейнер
        container = client.containers.run(
            image_config['image'],
            detach=True,
            ports={f"{image_config['port']}/tcp": ('127.0.0.1', 0)},
            environment={
                'PHPIDS_ENABLED': 'false' if image_id == 'dvwa' else None
            }
        )

        # Получаем назначенный порт
        container.reload()
        port = container.ports[f"{image_config['port']}/tcp"][0]['HostPort']
        url = f"http://localhost:{port}"

        # Открываем в браузере через 5 секунд
        Timer(5, open_browser, args=(url,)).start()

        return jsonify({
            'status': 'success',
            'url': url,
            'port': port
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_flag', methods=['POST'])
def check_flag():
    user_flag = request.form.get('flag', '').strip()
    flags = session.get('flags', {})

    for key, flag in flags.items():
        if user_flag == flag:
            return jsonify({'status': 'success', 'message': f'Флаг верный! Уязвимость {key} подтверждена.'})

    return jsonify({'status': 'error', 'message': 'Неверный флаг'}), 400

def open_browser(url):
    webbrowser.open_new_tab(url)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
