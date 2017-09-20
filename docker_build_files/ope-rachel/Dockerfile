
FROM php:5.6-apache
RUN apt-get update \
&& apt-get -y install nano git sqlite3 libsqlite3-dev \
libfreetype6-dev \
        libjpeg62-turbo-dev \
        libmcrypt-dev \
        libpng12-dev \
    && docker-php-ext-install -j$(nproc) iconv mcrypt \
    && docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ \
    && docker-php-ext-install -j$(nproc) gd
RUN docker-php-source extract \
&& pecl install stem \
&& docker-php-source delete
LABEL rebuild=6
RUN git clone https://github.com/rachelproject/contentshell.git /var/www/html 
# Patch to move Admin database to external docker volume 'modules'
RUN sed -i "s/\/admin.sqlite/\/..\/modules\/admin.sqlite/" /var/www/html/admin/common.php
RUN echo "<?php echo phpinfo(); ?>" > /var/www/html/php_about.php
RUN chown -R www-data:www-data /var/www/html
COPY reset_pw.php /reset_pw.php
COPY start.sh /start.sh
RUN chmod +x /start.sh
#RUN mkdir /var/www/data; chown -R  www-data:www-data /var/www/data
VOLUME ["/var/www/html/modules"]

CMD "/start.sh"
