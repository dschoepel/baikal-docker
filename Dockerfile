# Baïkal on nginx + PHP-FPM.
# Adapted from ckulka/baikal-docker's nginx.dockerfile (MIT, Copyright (c) 2015 Cyrill Kulka).
# Upgrade Baïkal: change BAIKAL_VERSION. Upgrade PHP: change PHP_VERSION / MIN_PHP_VERSION.

ARG BAIKAL_VERSION=0.13.0

# Stage 1: download and unpack the Baïkal release zip
FROM alpine:3 AS builder
ARG BAIKAL_VERSION
ADD https://github.com/sabre-io/Baikal/releases/download/${BAIKAL_VERSION}/baikal-${BAIKAL_VERSION}.zip /tmp/baikal.zip
RUN apk add --no-cache unzip && unzip -q /tmp/baikal.zip -d /

# Stage 2: final image (same base and runtime user as ckulka/baikal:nginx)
FROM nginx:1
ARG BAIKAL_VERSION
ARG PHP_VERSION=8.4
# Build fails if the PHP package repo hands us anything older than this
ARG MIN_PHP_VERSION=8.4.27

# PHP from the Sury repo (same source ckulka uses), plus SQLite and msmtp
RUN set -eux; \
  curl -fsSL -o /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg; \
  . /etc/os-release; \
  echo "deb https://packages.sury.org/php/ ${VERSION_CODENAME} main" > /etc/apt/sources.list.d/php.list; \
  apt-get update; \
  apt-get upgrade -y; \
  apt-get install -y --no-install-recommends \
    php${PHP_VERSION}-curl \
    php${PHP_VERSION}-fpm \
    php${PHP_VERSION}-mbstring \
    php${PHP_VERSION}-mysql \
    php${PHP_VERSION}-pgsql \
    php${PHP_VERSION}-sqlite3 \
    php${PHP_VERSION}-xml \
    sqlite3 \
    msmtp msmtp-mta; \
  rm -rf /var/lib/apt/lists/*; \
  sed -i 's/www-data/nginx/' /etc/php/${PHP_VERSION}/fpm/pool.d/www.conf; \
  sed -i 's/^listen = .*/listen = \/var\/run\/php-fpm.sock/' /etc/php/${PHP_VERSION}/fpm/pool.d/www.conf; \
  php -r "exit(version_compare(PHP_VERSION, '${MIN_PHP_VERSION}', '>=') ? 0 : 1);" \
    || { echo "PHP $(php -r 'echo PHP_VERSION;') is older than required ${MIN_PHP_VERSION}"; exit 1; }; \
  php -v

# Startup scripts, Baïkal and nginx site config
COPY --chmod=755 files/docker-entrypoint.d/*.sh /docker-entrypoint.d/
COPY --from=builder --chown=nginx:nginx /baikal /var/www/baikal
COPY files/nginx.conf /etc/nginx/conf.d/default.conf

VOLUME /var/www/baikal/config
VOLUME /var/www/baikal/Specific

LABEL org.opencontainers.image.title="Baikal" \
      org.opencontainers.image.description="Baïkal CalDAV/CardDAV server on nginx + PHP ${PHP_VERSION}" \
      org.opencontainers.image.source="https://github.com/dschoepel/baikal-docker" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${BAIKAL_VERSION}"
