FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libssl-dev \
    pkg-config \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

EXPOSE 8000

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

# RUN apk add --no-cache \
#     gcc \
#     musl-dev \
#     mariadb-connector-c-dev \
#     libffi-dev \
#     openssl-dev \
#     python3-dev \
#     build-base



#  celery -A base_config worker -l info -P solo

#  celery -A base_config beat -l info --scheduler celery.beat.PersistentScheduler
# docker run -p 5000:80 -p 1025:25 rnwood/smtp4dev