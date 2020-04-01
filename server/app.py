from logging import Logger
from flask import Flask, send_from_directory, request, after_this_request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from youtube_dl import YoutubeDL
import hashlib
import shutil
from os import listdir, getenv
from os.path import isfile, join

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per day", "50 per hour"]
)


@app.route('/')
def index():
    try:
        url = request.args.get('url')
        if url is None:
            return response_with_cors(Response("Hawi wos is?")), 400

        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        directory = "tmp/" + m.hexdigest()

        @after_this_request
        def remove_file(response_to_return):
            shutil.rmtree(directory)
            return response_to_return

        logger = CustomLogger("youtube-dl logger")

        ydl = YoutubeDL({
            "outtmpl": directory + "/%(title)s.%(ext)s",
            "max_filesize": 50000000,
            "logger": logger
        })

        with ydl:
            ydl.download([url])

        files = [f for f in listdir(directory) if isfile(join(directory, f))]

        messages = logger.getMessages()
        if len(messages) > 0 and "File is larger than max-filesize" in messages[-1]:
            raise Exception("Max file-size exceeded.")

        if len(files) == 0:
            raise Exception("No files were downloaded?")

        filename = files[0]
        file_path = directory

        return response_with_cors(send_from_directory(file_path, filename, as_attachment=True))
    except Exception as e:
        app.logger.error(e)
        return response_with_cors(Response(str(e))), 400


class CustomLogger(Logger):
    def __init__(self, name: str):
        super().__init__(name)
        self.messages = []

    def handle(self, record):
        self.messages.append(record.msg)

    def getMessages(self):
        return self.messages


def response_with_cors(response):
    response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
    response.headers['Access-Control-Allow-Origin'] = getenv("FRONTEND_URL")
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
