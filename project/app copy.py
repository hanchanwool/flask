from flask import Flask, request, render_template
import os
import requests
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Clova Speech API 정보
CLOVA_SPEECH_SECRET_KEY = 'e08cbd4747b44587b1e55f220a0ad166'
CLOVA_SPEECH_INVOKE_URL = 'https://clovaspeech-gw.ncloud.com/external/v1/7211/f3b6e36916e7c22c5b8799ca67d17b0a4f6c81ebc7e4a8cb18a0abafcf135bcf'

def convert_speech_to_file(file_path):
    with open(file_path, 'rb') as f:
        files = {'media': f}
        params = {
            'language': 'ko-KR',
            'completion': 'sync',
            'wordAlignment': True,
            'fullText': True,
            'speakerDiarization': True  # 화자 구분 활성화
        }
        headers = {'X-CLOVASPEECH-API-KEY': CLOVA_SPEECH_SECRET_KEY}
        response = requests.post(f'{CLOVA_SPEECH_INVOKE_URL}/recognizer/upload', headers=headers, files=files, data={'params': json.dumps(params)})
        return response.json()  # 전체 응답을 반환하여 화자 구분 정보 포함

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        voice_file = request.files.get('voice_file')
        if voice_file and voice_file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], voice_file.filename)
            voice_file.save(filepath)
            response_json = convert_speech_to_file(filepath)
            
            # 디버깅용 로그 추가
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
            
            speaker_segments = []
            for segment in response_json.get('segments', []):
                speaker = segment.get('speaker', 'unknown')
                text = segment.get('text', '')
                if isinstance(speaker, dict):  # speaker가 dict인 경우 처리
                    speaker = speaker.get('name', 'unknown')
                speaker_segments.append({'speaker': speaker, 'text': text})

            return render_template('result.html', speaker_segments=speaker_segments)
        else:
            return '음성 파일이 제공되지 않았습니다.', 400
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)