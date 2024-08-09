import PyPDF2
import asyncio

async def extract_text_from_pdf(file_path: str):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                yield text
            

async def main():
    async for text in extract_text_from_pdf():
        with open("temp.txt", "a") as file:
            print(text)
            file.write(text + "\n") 

if __name__ == "__main__":
    asyncio.run(main())
