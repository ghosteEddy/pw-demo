FROM python:3.12.8-slim-bookworm

WORKDIR /webserver

# this is just for easy healthcheck demonstration
RUN apt-get -y update; apt-get -y install curl


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .



EXPOSE 8000
ENTRYPOINT ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]