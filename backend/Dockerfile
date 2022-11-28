FROM python:3.7-slim

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait ./wait

RUN chmod +x ./wait

CMD ./wait && ./run_gunicorn.sh
