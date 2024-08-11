from flask import Flask, request
import ffmpeg
import os

output_path = '/tmp/output.mp4'
gpu_or_cpu = 'cuda'  # Change this to 'cpu' if you want to use the CPU

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    input_path = '/tmp/' + file.filename
    output_path = '/tmp/transcoded_' + os.path.splitext(file.filename)[0] + '.mp4'

    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_path):
        os.remove(output_path)

    file.save(input_path)
    
   # Transcode the file to 1080p MP4 format using ffmpeg-python
    try:
        if gpu_or_cpu == 'cuda':
            ffmpeg.input(input_path).output(output_path, vf='scale=1920:1080', vcodec='h264_nvenc', acodec='aac').run()
        else:
            ffmpeg.input(input_path).output(output_path, vf='scale=1920:1080', vcodec='libx264', acodec='aac').run()
    except ffmpeg.Error as e:
        return f"Error transcoding file: {e.stderr.decode('utf8')}", 500
    
    return f'File received and transcoded to {output_path}', 200

if __name__ == '__main__':
    app.run(debug=True, port=5002, ssl_context="adhoc")
