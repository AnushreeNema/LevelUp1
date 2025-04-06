'''imports'''
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from google import genai
from openai import OpenAI
import threading
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import time
import os
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
final_notes=''
user_input=''
memory=[]
end=False
'''function for recording audio'''
def record_audio():
    second = 3
    fs = 16000
    
    myrecording = sd.rec(int(second * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    write('out.wav', fs, myrecording)
    a = myrecording.flatten()
    return a
'''function for transcribing audio'''
def transcribe(value1):
    model = WhisperModel('base', compute_type="int8")
    parts, info = model.transcribe(value1)  
    return parts

'''function for answering user questions'''
def openai_chat_response():
    
    learned_info=' '.join(memory)
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4o",
        input=f"you are a teacher and also solves doubts of students. The {learned_info} is from a lecture or a conversation and you will use it in your responses. When a user asks something {user_input}, answer it using the {learned_info} and also your own knowledge. If a user asks something first check if it is present in the {learned_info}, if present there then combine {learned_info} and your knowledge about it and reply. And also keep your answers structured and well-formatted. "
    )


    return response.output_text
    

    
'''function for generating notes'''
def gemini_notes():
    learned_notes=' '.join(memory)
    client=genai.Client(api_key="--API--KEY")
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"kindly generate notes on the basis of {learned_notes}. Generate detailed and well-formatted notes",
)

    return response.text

'''flask route function for user query'''
@app.route('/question', methods=['POST'])
def ask():
    
    global user_input, end
    data = request.get_json()
    user_input = data.get("question", "")
    if user_input == 'start':
            threading.Thread(target=main, daemon=True).start()
            end=False
    if user_input=='quit':
            #c=gemini_notes()
            end=True
            c=gemini_notes()
            print('hope you have a great day!')
            print(memory)
            
            return jsonify({"answer": " Goodbye, have a great day!", "C": c})
            
    while end==False:
        if user_input!='quit':
            
            
            answer = openai_chat_response()
            return jsonify({"answer": answer})
'''main work function'''
def main():
    global user_input, final_notes
    while True:
        
        result1 = record_audio()
        result2 = transcribe(result1)
        

        if end is False:
            for segment in result2:
                
                memory.append(segment.text)
                
            if user_input:
                openai_chat_response()
                user_input = ""
                time.sleep(0.5)
                
                
        else:
             final_notes = gemini_notes()
             print("Hope you have a great day :)")
             print(final_notes)
             break
'''flask route function for printing notes'''
@app.route("/notes", methods=["GET"])
def get_notes():
    return jsonify({"notes": final_notes})
            

'''thread for running the main working function all time'''
threading.Thread(target=main, daemon=True).start()

    

if __name__ == '__main__':
    app.run(debug=True)



