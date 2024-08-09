import google.generativeai as genai
from dotenv import load_dotenv
import os
import asyncio
from gtts import gTTS

load_dotenv()


async def main():
    genai.configure(api_key=os.environ["API_KEY"])
    generation_config = {
                        "temperature": 1,
                        # "top_p": 0.95,
                        # "top_k": 64,
                        # "max_output_tokens": 8192,
                        "response_mime_type": "text/plain",
                        }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="translator",
        )
    count = 0
    file = open("temp.txt")
    arr = []
    for row in file.readlines():
        count +=1
        if count > 30:
            break
        row = row.strip()
        arr.append(row)
    print(*arr)
    res = model.generate_content(f"translate to arabic {"".join(arr)} ")
    print(res.text)
        


async def tts(text):
    tts = gTTS(text, lang='ar')
    audio_filename = f'audio.mp3'
    tts.save(audio_filename)
    print(f"Saved translated speech as {audio_filename}")

if __name__ == "__main__":
    asyncio.run(main())

        
