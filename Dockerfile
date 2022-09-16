FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN ["mkdir", "app"]

COPY ["requirements.txt", "/app"]
COPY ["main.py", "/app"]
COPY ["./common", "/app"]

WORKDIR /app

ENV APP_PORT=9118
EXPOSE ${APP_PORT}

RUN ["pip", "install", "-r", "/requirements.txt"]

RUN python main.py --jackett_host $JACKET_HOST $JACKETT_PROTOCOL $JACKETT_API_KEY $UTIL_PORT $MIN_SEEDS  \
    $MIN_SIZE_OF_TORRENT $MAX_SIZE_OF_TORRENT