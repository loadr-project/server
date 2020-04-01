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
max_filesize_in_bytes = 128000000
max_duration_in_seconds = 1800


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
            "max_filesize": 128000000
        })
        with ydl:
            result = ydl.extract_info(url, download=False)

        has_filesize = True
        filesize = 0
        requested_formats = result.get('requested_formats')
        if requested_formats is None:
            has_filesize = False
        else:
            for format in result.get('requested_formats'):
                format_filesize = format.get('filesize')
                if format_filesize is None:
                    has_filesize = False
                    break
                filesize += format_filesize

        if has_filesize:
            if filesize > max_filesize_in_bytes:
                raise Exception("Downloaded video exceeds maximum filesize of %d bytes" % max_filesize_in_bytes)
        elif False:
            # TODO neither requested_formats, nor filesize, nor duration exists on reddit videos?
            # filesize can't be read from formats, so we fallback to limiting the duration
            app.logger.info("No requested format found: " + url)
            duration_in_seconds = result.get('duration')
            if duration_in_seconds > max_duration_in_seconds:
                raise Exception("Downloaded video exceeds maximum duration of %d seconds" % max_duration_in_seconds)

        with ydl:
            ydl.download([url])

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
