FROM nginx:alpine
MAINTAINER Paul Ganster <paul@ganster.dev>

WORKDIR /home/app
RUN apk add npm
COPY package.json /home/app/package.json
COPY package-lock.json /home/app/package-lock.json
RUN npm ci

COPY . /home/app

RUN npm run build
RUN rm -rf /usr/share/nginx/html
RUN mv build /usr/share/nginx/html

