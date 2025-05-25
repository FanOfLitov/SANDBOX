FROM php:7.2-apache

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    unzip wget mariadb-client libzip-dev libpng-dev zip \
    && docker-php-ext-install pdo pdo_mysql zip gd

# Включение mod_rewrite
RUN a2enmod rewrite

# Скачиваем и распаковываем официальный релиз Drupal 8.6.5
WORKDIR /var/www/html
RUN wget -q https://ftp.drupal.org/files/projects/drupal-8.6.5.tar.gz && \
    tar -xzf drupal-8.6.5.tar.gz && \
    rm drupal-8.6.5.tar.gz && \
    mv drupal-8.6.5 drupal

# Копируем Apache конфиг
COPY .docker/vhost.conf /etc/apache2/sites-available/000-default.conf

# Права
RUN chown -R www-data:www-data /var/www/html/drupal && \
    chmod -R 755 /var/www/html/drupal

EXPOSE 80
CMD ["apache2-foreground"]
