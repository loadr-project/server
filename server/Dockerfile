FROM alpine:latest
MAINTAINER Paul Ganster <paul@ganster.dev>
WORKDIR /home/app

RUN apk add python3
RUN apk add py3-pip
RUN apk add ffmpeg
RUN pip3 install --upgrade pip
RUN pip3 install flask youtube-dl gunicorn flask-limiter

COPY . /home/app

EXPOSE 80
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]

