FROM alpine:latest
MAINTAINER Paul Ganster <paul@ganster.dev>

WORKDIR /home/app

# Packages
RUN apk add python3 py3-pip ffmpeg && \
    pip3 install --upgrade pip && \
    pip3 install flask youtube-dl gunicorn flask-limiter

# Copy server source
COPY app.py /home/app/app.py

# Expose & start server
EXPOSE 80
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]

