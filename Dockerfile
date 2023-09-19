FROM python:3.10.7-alpine as base

#  Настраиваем Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#  Обозначаем рабочие папки для проекта и приложения
ENV HOME=/opt/star-burger/
ENV APP_HOME=/opt/star-burger/app

#  Создаём диркетории для проекта (внутри контейнера)
RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/staticfiles
RUN mkdir -p $APP_HOME/media

#  Копируем данные git репозитория в контейнер
WORKDIR $HOME
COPY .git ./.git

#  Копируем файл с зависимостями
WORKDIR $APP_HOME
COPY ./requirements.txt .

#  Устанавливаем необходимые пакеты linux
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev git

#  Устанавливаем зависимости для Python
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

#  Копируем файлы приложения
COPY assets ./assets
COPY foodcartapp ./foodcartapp
COPY locations ./locations
COPY restaurateur ./restaurateur
COPY star_burger ./star_burger
COPY templates ./templates
COPY manage.py ./

RUN git config --global -add safe.directory $HOME

EXPOSE 8000
