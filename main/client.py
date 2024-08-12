from flask import Flask, request, send_from_directory, session, jsonify
import os
import ffmpeg
from threading import Thread

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management

def save_file(file, input_path):
    file.save(input_path)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    input_path = '/tmp/' + file.filename

    if os.path.exists(input_path):
        os.remove(input_path)

    # Save file in the background
    thread = Thread(target=save_file, args=(file, input_path))
    thread.start()

    return jsonify({"message": "File is being uploaded", "filename": file.filename}), 200

@app.route('/transcode', methods=['POST'])
def transcode_file():
    filename = request.form.get('filename')
    if not filename:
        return 'No filename provided', 400

    input_path = '/tmp/' + filename
    if not os.path.exists(input_path):
        return 'File not found', 400

    video_format = request.form.get('video_format', 'mp4')
    audio_format = request.form.get('audio_format', 'aac')
    video_bitrate = request.form.get('video_bitrate', '1000k')
    audio_bitrate = request.form.get('audio_bitrate', '128k')
    resolution = request.form.get('resolution', '1080p')
    gpu_or_cpu = request.form.get('gpu_or_cpu', 'cpu')
    video_codec = request.form.get('video_codec', 'libx264')

    resolution_map = {
        '720p': '1280x720',
        '1080p': '1920x1080',
        '2160p': '3840x2160'
    }
    scale = resolution_map.get(resolution, '1920x1080')

    output_path = f'./transcoded_{os.path.splitext(filename)[0]}.{video_format}'
    download_path = f'./downloads/transcoded_{os.path.splitext(filename)[0]}.{video_format}'

    if os.path.exists(output_path):
        os.remove(output_path)

    try:
        if gpu_or_cpu == 'cuda':
            if video_codec not in ['h264_nvenc', 'hevc_nvenc']:
                return 'Invalid codec for GPU', 400
            ffmpeg.input(input_path).output(output_path, vf=f'scale={scale}', vcodec=video_codec, acodec=audio_format, video_bitrate=video_bitrate, audio_bitrate=audio_bitrate, metadata='encoding_program=josie, version=1.0').run()
        else:
            if video_codec not in ['libx264', 'libx265']:
                return 'Invalid codec for CPU', 400
            ffmpeg.input(input_path).output(output_path, vf=f'scale={scale}', vcodec=video_codec, acodec=audio_format, video_bitrate=video_bitrate, audio_bitrate=audio_bitrate, metadata='encoding_program=josie, version=1.0').run()
    except ffmpeg.Error as e:
        return f"Error transcoding file: {e.stderr.decode('utf8')}", 500

    # Move the transcoded file to the downloads directory
    os.makedirs('./downloads', exist_ok=True)
    os.rename(output_path, download_path)

    return f'File received and transcoded. <a href="{download_path}">Download here</a>', 200

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory('./downloads', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5002, ssl_context="adhoc")
