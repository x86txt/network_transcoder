from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import os
from werkzeug.utils import secure_filename

# disable internal tls warning
requests.packages.urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['uploaded_file'] = filepath
        return jsonify({'filename': filename})
    return 'No file uploaded', 400

@app.route('/options')
def options():
    filename = request.args.get('filename')
    return render_template('options.html', filename=filename)

@app.route('/transcode', methods=['POST'])
def transcode():
    video_format = request.form['video_format']
    audio_format = request.form['audio_format']
    video_bitrate = request.form['video_bitrate']
    audio_bitrate = request.form['audio_bitrate']
    resolution = request.form['resolution']
    gpu_or_cpu = request.form['gpu_or_cpu']
    video_codec = request.form['video_codec']
    filepath = session.get('uploaded_file')

    if filepath:
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f, 'application/octet-stream')}
            data = {
                'video_format': video_format,
                'audio_format': audio_format,
                'video_bitrate': video_bitrate,
                'audio_bitrate': audio_bitrate,
                'resolution': resolution,
                'gpu_or_cpu': gpu_or_cpu,
                'video_codec': video_codec
            }
            response = requests.post('https://localhost:5002/upload', files=files, data=data, verify=False)
            return response.text
    return 'No file uploaded', 400

if __name__ == '__main__':
    app.run(debug=True, port=5003, ssl_context="adhoc")
