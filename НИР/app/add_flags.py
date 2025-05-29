import pymysql
import psycopg2
from utils import load_flags
from utils import generate_and_save_flags, FlagsRecord, LABS, FLAG_TYPES

# Параметры подключения к DVWA (MySQL)
DVWA_DB_CONFIG = {
    "host": "dvwa_db",  # имя хоста контейнера или IP
    "port": 8080,
    "user": "dvwa_user",
    "password": "dvwa_password",
    "database": "dvwa"
}

# Параметры подключения к Juice Fruit (PostgreSQL)
JUICE_DB_CONFIG = {
    "host": "juice_db",
    "port": 3000,
    "user": "juice_user",
    "password": "juice_password",
    "database": "juice"
}
WORDPRESS_DB_CONFIG = {
    "host": "wp_db",
    "port": 3306,
    "user": "wp_user",
    "password": "wp_password",
    "database": "wordpress"
}

def insert_flag_mysql(config, flag: str, flag_type: str):
    conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        charset="utf8mb4"
    )
    try:
        with conn.cursor() as cur:
            # Создаём таблицу flags, если нет
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flags (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    flag VARCHAR(128) NOT NULL,
                    flag_type VARCHAR(32)
                )
            """)
            # Вставляем флаг
            cur.execute("INSERT INTO flags (flag, flag_type) VALUES (%s, %s)", (flag, flag_type))
            conn.commit()
            print(f"MySQL: Вставлен флаг {flag} с типом {flag_type}")
    finally:
        conn.close()

def insert_flag_postgres(config, flag: str, flag_type: str):
    conn = psycopg2.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        dbname=config["database"]
    )
    try:
        with conn.cursor() as cur:
            # Создаём таблицу flags, если нет
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flags (
                    id SERIAL PRIMARY KEY,
                    flag VARCHAR(128) NOT NULL,
                    flag_type VARCHAR(32)
                )
            """)
            # Вставляем флаг
            cur.execute("INSERT INTO flags (flag, flag_type) VALUES (%s, %s)", (flag, flag_type))
            conn.commit()
            print(f"PostgreSQL: Вставлен флаг {flag} с типом {flag_type}")
    finally:
        conn.close()

def insert_flag_wordpress(config, flag: str, flag_type: str):
    conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        charset="utf8mb4"
    )
    try:
        with conn.cursor() as cur:
            # Добавим как пост в WordPress
            cur.execute("""
                INSERT INTO wp_posts (post_author, post_date, post_content, post_title,
                                      post_status, comment_status, ping_status, post_type)
                VALUES (1, NOW(), %s, %s, 'publish', 'closed', 'closed', 'post')
            """, (f"Флаг: {flag}", f"{flag_type.title()} флаг"))
            conn.commit()
            print(f"WordPress: Вставлен флаг {flag} в виде поста")
    finally:
        conn.close()

def save_flag_to_file(path: str, flag: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(flag)


def export_dvwa_easy_flag():
    flags = load_flags()
    easy_flag = next((f for f in flags if f.service == "dvwa" and f.flag_type == "easy"), None)
    if easy_flag:
        with open("flags/dvwa_easy.txt", "w", encoding="utf-8") as f:
            f.write(easy_flag.flag)
        print(f"Флаг записан: {easy_flag.flag}")
    else:
        print("Флаг не найден.")
def main():
    # Генерируем флаги и сохраняем в файл
    flags = generate_and_save_flags()

    # Фильтруем флаги для DVWA и Juice Fruit
    dvwa_flags = [f for f in flags if f.service == "dvwa"]
    juice_flags = [f for f in flags if f.service == "juice"]
    wp_flags = [f for f in flags if f.service == "wordpress"]

    for flag_rec in wp_flags:
        insert_flag_wordpress(WORDPRESS_DB_CONFIG, flag_rec.flag, flag_rec.flag_type)

    # Вставляем флаги в DVWA (MySQL)
    for flag_rec in dvwa_flags:
        insert_flag_mysql(DVWA_DB_CONFIG, flag_rec.flag, flag_rec.flag_type)

    # Вставляем флаги в Juice Fruit (PostgreSQL)
    for flag_rec in juice_flags:
        insert_flag_postgres(JUICE_DB_CONFIG, flag_rec.flag, flag_rec.flag_type)



if __name__ == "__main__":
    main()
    export_dvwa_easy_flag()
