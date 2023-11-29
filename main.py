from aiohttp import ClientSession

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import pyaes
from hashlib import sha256

import config
from tgfiles import tgFiles


app = FastAPI(
    title="TGFiles",
    redoc_url=None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
storage = tgFiles(config.TG_BOT_TOKEN)


@app.post("/upload", response_class=JSONResponse, tags=["Functions"])
async def upload_file(file: UploadFile, request: Request):
    if file.size > 50 * 1024 * 1024:
        raise HTTPException(413)

    file_id = await storage.upload(config.TG_CHANNEL_ID, file.file, file.filename)
    await file.close()
    url = f"{config.URL}/file/{encode_file_id(config.TG_CHANNEL_ID, file_id)}"

    if request.headers.get("hx-request") == "true":
        return HTMLResponse(f'<a href="{url}" target="_blank" class="uploaded-url">{url}</a>')
    else:
        return {"url": url}


@app.get("/file/{id}", response_class=StreamingResponse, tags=["Functions"])
async def download_file(id: str):
    try:
        file_id = decode_file_id(id)
        file_data = await storage.get_file_data(**file_id)
    except:
        raise HTTPException(404)

    headers = {
        "Content-Disposition": f'inline; filename="{file_data["file_name"]}"',
        "Content-Type": file_data["mime_type"],
        "Content-Length": str(file_data["file_size"]),
    }

    return StreamingResponse(file_stream(file_data["url"]), headers=headers)


app.mount("/", StaticFiles(directory="static", html=True))


async def file_stream(url: str):
    async with ClientSession() as session:
        async with session.get(url) as resp:
            async for chunk in resp.content.iter_any():
                yield chunk


def encode_file_id(channel_id: int, message_id: int) -> str:
    file_id_str = f"{channel_id}/{message_id}"
    aes = pyaes.AESModeOfOperationCTR(sha256(config.TG_BOT_TOKEN.encode()).digest())
    file_id_encoded = aes.encrypt(file_id_str).hex()
    return file_id_encoded


def decode_file_id(file_id_encoded) -> dict:
    aes = pyaes.AESModeOfOperationCTR(sha256(config.TG_BOT_TOKEN.encode()).digest())
    file_id_str = aes.decrypt(bytes.fromhex(file_id_encoded)).decode()
    channel_id, message_id = file_id_str.split("/")
    return {"channel_id": channel_id, "message_id": message_id}
