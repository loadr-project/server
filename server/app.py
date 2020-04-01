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
    default_limits=["200 per day", "50 per hour"]
)
max_filesize = 128000000


@app.route('/')
def index():
    try:
        url = request.args.get('url')
        if url is None:
            raise Exception("Hawi wos is")
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        directory = "tmp/" + m.hexdigest()
        ydl = YoutubeDL({
            "outtmpl": directory + "/%(title)s.%(ext)s",
            "max_filesize": 100
        })
        with ydl:
            result = ydl.extract_info(url, download=True)

        download_size = None
        format_id = result.get('format_id')
        for format in result.get('formats'):
            if format.get('format_id') == format_id:
                download_size = format.get('filesize')

        requested_formats = result.get('requested_formats')
        download_size = sum(format.get('filesize') for format in requested_formats)

        if download_size > max_filesize:
            raise Exception("Downloaded video exceeds maximum filesize!")

        with ydl:
            ydl.download([url])

        # TODO: "none object is not iterable: https://v.redd.it/l1wukgfxuxp41"
        # https://stackoverflow.com/a/3207973/2306363
        files = [f for f in listdir(directory) if isfile(join(directory, f))]

        if len(files) == 0:
            raise Exception("No files were downloaded?")

        filename = files[0]
        file_path = directory

        @after_this_request
        def remove_file(response_to_return):
            shutil.rmtree(directory)
            return response_to_return

        return response_with_cors(send_from_directory(file_path, filename, as_attachment=True))
    except Exception as e:
        app.logger.error(e)
        return response_with_cors(Response(str(e))), 400


def response_with_cors(response):
    response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
    response.headers['Access-Control-Allow-Origin'] = getenv("FRONTEND_URL")
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
