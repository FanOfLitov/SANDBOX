from flask import Flask, render_template, request, jsonify
import docker
import webbrowser
from threading import Timer

app = Flask(__name__)

# Конфигурация уязвимых образов
VULNERABLE_IMAGES = {
    'wordpress_4.7': {
        'image': 'vulnerables/web-dvwa',  # Используем готовый уязвимый образ
        'description': 'Damn Vulnerable Web App (DVWA)',
        'port': 80,
        'vulns': ['SQL Injection', 'XSS', 'CSRF']
    },
    'wordpress_5.0': {
        'image': 'wordpress:5.0',
        'description': 'WordPress 5.0 - Уязвимость в редакторе Gutenberg',
        'port': 80,
        'vulns': ['CVE-2019-9787']
    }
}

# Глобальная переменная для хранения URL запущенного контейнера
current_instance_url = None


def open_browser(url):
    webbrowser.open_new_tab(url)


@app.route('/')
def index():
    return render_template('index.html', images=VULNERABLE_IMAGES)


@app.route('/create', methods=['POST'])
def create_instance():
    global current_instance_url

    image_id = request.form.get('image')
    if image_id not in VULNERABLE_IMAGES:
        return jsonify({'error': 'Invalid image'}), 400

    image_config = VULNERABLE_IMAGES[image_id]

    try:
        client = docker.from_env()

        # Запускаем контейнер
        container = client.containers.run(
            image_config['image'],
            detach=True,
            ports={f"{image_config['port']}/tcp": ('127.0.0.1', 0)},  # Случайный порт
            environment={
                'PHPIDS_ENABLED': 'false'  # Для DVWA отключаем защиту
            }
        )

        # Получаем назначенный порт
        container.reload()
        port = container.ports[f"{image_config['port']}/tcp"][0]['HostPort']
        url = f"http://localhost:{port}"
        current_instance_url = url

        # Открываем в браузере через 3 секунды (даем контейнеру время запуститься)
        Timer(3, open_browser, args=(url,)).start()

        return jsonify({
            'status': 'success',
            'url': url,
            'port': port
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)


