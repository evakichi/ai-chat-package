from fastapi import FastAPI,File,Form,UploadFile
from fastapi.responses import FileResponse
import glob
import os

app = FastAPI()

files = [f for f in glob.glob('/uploads/**',recursive=True) if f.lower().endswith('.pdf')]

# フロントエンドのアップロードページ（HTML）を提供
@app.get("/")
def index():
    return len(files)

@app.get('/filename/{item}')
async def summarize(item:str):
    num = int(item)
    file_path = files[num]
    return os.path.basename(file_path)

@app.get('/distribute/{item}')
async def summarize(item:str):
    num = int(item)
    file_path = files[num]

    return FileResponse(
        path=file_path, 
        filename=os.path.basename(file_path), 
        media_type="application/pdf"
    )

@app.get('/download/{item}')
async def download(item:str):
    file_path = f"/uploads/{item}"
    return FileResponse(
        path=file_path, 
        filename=os.path.basename(file_path), 
        media_type="application/pdf"
    )

if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG

    uvicorn.run(app, host="0.0.0.0", port=8863)
