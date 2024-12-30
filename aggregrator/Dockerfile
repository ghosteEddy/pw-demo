FROM python:3.12.8-bookworm


RUN apt-get update && apt-get install -y cron

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

COPY crontab /etc/cron.d/my-crontab
RUN chmod 0644 /etc/cron.d/my-crontab && crontab /etc/cron.d/my-crontab

ENTRYPOINT ["sh", "-c", "printenv > /etc/environment && cron -f"]