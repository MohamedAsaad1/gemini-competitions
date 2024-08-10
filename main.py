from flask import Flask, request, jsonify, send_file, render_template
import PyPDF2
import os
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv
import tempfile
import uuid
from threading import Thread


load_dotenv()


genai.configure(api_key=os.environ["API_KEY"])
generation_config = {
    "temperature": 1,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="translator",
)

app = Flask(__name__)

# In-memory progress tracking
progress = {}
file_paths = {}

def extract_text_from_pdf(file_path: str):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def translate_text(text: str, task_id: str):
    progress[task_id] = {'status': 'Translating', 'percentage': 0}
    response = model.generate_content(f"translate to arabic {text}", stream=False)
    translated_text = "".join(res.text for res in response)
    progress[task_id]['status'] = 'Translating Complete'
    progress[task_id]['percentage'] = 50
    print(f"Translation completed for task {task_id}")
    return translated_text.replace("#","").replace("*","")

def text_to_speech(text: str, task_id: str) -> str:
    progress[task_id] = {'status': 'Converting to Speech', 'percentage': 50}
    tts = gTTS(text, lang='ar')
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(audio_file.name)
    final_audio_path = f"/tmp/{task_id}.mp3"
    os.rename(audio_file.name, final_audio_path)
    print(f"Final audio file path: {final_audio_path}")
    progress[task_id]['status'] = 'Completed'
    progress[task_id]['percentage'] = 100
    file_paths[task_id] = final_audio_path
    return final_audio_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        task_id = str(uuid.uuid4())
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            file.save(temp_pdf.name)

        text = extract_text_from_pdf(temp_pdf.name)
        os.remove(temp_pdf.name)  # Clean up temporary PDF file

        def process():
            try:
                translated_text = translate_text(text, task_id)
                audio_file_path = text_to_speech(translated_text, task_id)
                print(f"Processing completed for task {task_id}")
            except Exception as e:
                print(f"Error during processing: {e}")
                progress[task_id] = {'status': 'Failed', 'percentage': 0}

        Thread(target=process).start()
        return jsonify({"task_id": task_id}), 202

@app.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    if task_id in progress:
        return jsonify(progress[task_id])
    return jsonify({"status": "Not Found"}), 404

@app.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    if task_id in file_paths and os.path.exists(file_paths[task_id]):
        return send_file(file_paths[task_id], as_attachment=True, download_name="translated_audio.mp3")
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(port=8000,debug=True)
