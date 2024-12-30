FROM python:3.12.8-slim-bookworm

WORKDIR /receiver

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]