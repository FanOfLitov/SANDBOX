from flask import Flask, render_template, request, jsonify
import docker
import subprocess
import os
import random
import string

app = Flask(__name__)
docker_client = docker.from_env()

# Конфигурация доступных уязвимых образов
VULNERABLE_IMAGES = {
    'wordpress_4.7': {
        'image': 'wordpress:4.7',
        'description': 'WordPress 4.7 - Уязвимость REST API',
        'port': 80,
        'vulns': ['CVE-2017-1001000']
    },
    'wordpress_5.0': {
        'image': 'wordpress:5.0',
        'description': 'WordPress 5.0 - Уязвимость в редакторе Gutenberg',
        'port': 80,
        'vulns': ['CVE-2019-9787']
    }
}


# Генерация случайных идентификаторов
def generate_id(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


@app.route('/')
def index():
    return render_template('index.html', images=VULNERABLE_IMAGES)


@app.route('/create', methods=['POST'])
def create_instance():
    image_id = request.form.get('image')
    if image_id not in VULNERABLE_IMAGES:
        return jsonify({'error': 'Invalid image'}), 400

    instance_id = generate_id()
    image_config = VULNERABLE_IMAGES[image_id]

    try:
        # Запускаем контейнер
        container = docker_client.containers.run(
            image_config['image'],
            detach=True,
            name=f"vulnlab_{instance_id}",
            ports={f"{image_config['port']}/tcp": None},
            environment={
                'WORDPRESS_DB_HOST': 'db',
                'WORDPRESS_DB_USER': 'wordpress',
                'WORDPRESS_DB_PASSWORD': 'wordpress',
                'WORDPRESS_DB_NAME': 'wordpress'
            }
        )

        # Получаем назначенный порт
        container.reload()
        host_port = container.ports[f"{image_config['port']}/tcp"][0]['HostPort']

        return jsonify({
            'id': instance_id,
            'url': f"http://localhost:{host_port}",
            'port': host_port,
            'image': image_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/destroy/<instance_id>', methods=['POST'])
def destroy_instance(instance_id):
    try:
        container = docker_client.containers.get(f"vulnlab_{instance_id}")
        container.stop()
        container.remove()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
