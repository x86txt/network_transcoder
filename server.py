from flask import Flask, request
import requests
import os
import ffmpeg

app = Flask(__name__)

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
    file.save(input_path)

    # Number of chunks specified in the request
    num_chunks = int(request.form.get('num_chunks', 1))
    
    # Split the video into chunks
    chunk_paths = split_video_into_chunks(input_path, num_chunks)
    
    # Send each chunk to a different client
    for i, chunk_path in enumerate(chunk_paths):
        client_url = f'https://localhost:500{i+1}/upload'
        if send_file_to_client(chunk_path, client_url):
            os.remove(chunk_path)
    
    return 'File uploaded and chunks sent to clients', 200
    
def split_video_into_chunks(input_path, num_chunks):
    chunk_paths = []
    duration = float(ffmpeg.probe(input_path)['format']['duration'])
    chunk_duration = duration / num_chunks
    
    for i in range(num_chunks):
        start_time = i * chunk_duration
        chunk_path = f'/tmp/chunk_{i}.mp4'
        if os.path.exists(chunk_path):
            os.remove(chunk_path)
        ffmpeg.input(input_path, ss=start_time, t=chunk_duration).output(chunk_path).run()
        chunk_paths.append(chunk_path)
    
    return chunk_paths
    return 'File uploaded and sent to client', 200

def send_file_to_client(file_path, client_url):
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post(client_url, files=files, verify=False)
        if response.status_code != 200:
            print(f"Failed to send file to client: {response.status_code}")

if __name__ == '__main__':
    app.run(debug=True, port=5000, ssl_context="adhoc")
