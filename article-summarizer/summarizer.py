from typing import Annotated
from fastapi import FastAPI,File,Form,UploadFile
from fastapi.responses import HTMLResponse
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import shutil
from tika import parser
from pathlib import Path
import os

model_name = []
tokenizer = []
model = []

model_name.append("google/pegasus-xsum")
model_name.append("facebook/bart-large-cnn")

for num in range(len(model_name)): 
    tokenizer.append(AutoTokenizer.from_pretrained(model_name[num]))
    model.append(AutoModelForSeq2SeqLM.from_pretrained(model_name[num]))

print('Phase 1')
app = FastAPI()
UPLOAD_DIR = Path("./tmp")

app = FastAPI()

# アップロードファイルの保存先ディレクトリ
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def get_html_content(num,filename,summary):
        content = f"""
        <HTML>
        <HEAD><TITLE>{filename}</TITLE></HEAD>
        <BODY><H1>{model_name[num]}</H1><H2>{filename}</H2><HR>{summary}<HR>
        <A HREF="http://{os.getenv('DOMAIN_NAME')}:8861/">Return</A>
        </BODY>
        </HTML>
        """
        return HTMLResponse(content=content,status_code=200)


# フロントエンドのアップロードページ（HTML）を提供
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
    <head><title>ファイルアップロード</title></head>
    <body>
        <h1>ファイルアップロード</h1>
        <P>google/pegasus-xsum:
        <form action="/summarize/html?q=pegasus-xsum" enctype="multipart/form-data" method="post">
            <input name="file" type="file">
            <input type="submit" value="アップロード">
        </form>
        </P>
        <p>faceboof/bart-large-cnn:
        <form action="/summarize/html?q=bart-large-cnn" enctype="multipart/form-data" method="post">
            <input name="file" type="file">
            <input type="submit" value="アップロード">
        </form>
        </P>
    </body>
    </html>
    """

def get_summarized_string(num,text_content):
    if num == 0:
        inputs = tokenizer[0](text_content, truncation=True, padding="longest", return_tensors="pt")
        outputs = model[0].generate(**inputs, num_beams=4, max_length=50, early_stopping = True)
        return tokenizer[0].decode(outputs[0], skip_special_tokens=True)
    elif num == 1:
        inputs = tokenizer[1](text_content, truncation=True, max_length=1024,padding="max_length", return_tensors="pt")
        outputs = model[1].generate(**inputs, min_length=30, max_length=130, do_sample = False)
        return tokenizer[1].decode(outputs[0], skip_special_tokens=True)

@app.post('/summarize/{item}')
async def summarize(item:str,q: str | None = None,file: UploadFile = File(...)):
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        save_path = UPLOAD_DIR / file.filename

        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_data = parser.from_file(str(save_path))
        # 抽出結果を変数に格納
        text_content = file_data['content']
        text_metadata = file_data['metadata']

        if q == 'pegasus-xsum':
            num = 0
        elif q == 'bart-large-cnn':
            num = 1
        
        summarized_string = get_summarized_string(num,text_content)

        if item == "json":
            return {"filename":file.filename,"summary":summarized_string}
        elif item == "html":
            return get_html_content(num,file.filename,summarized_string)
    finally:
        file.file.close()

if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG

    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s"

    uvicorn.run(app, host="0.0.0.0", port=8861,log_config=LOGGING_CONFIG)
