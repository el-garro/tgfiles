from typing import AsyncGenerator
from aiohttp import ClientSession

from fastapi import FastAPI, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from tgfiles import TGFiles
from urllib.parse import quote


app = FastAPI(
    title="TGFiles",
    redoc_url=None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
storage = TGFiles(config.TG_BOT_TOKEN)


@app.post("/upload", response_class=JSONResponse, tags=["Functions"])
async def upload_file(file: UploadFile, request: Request):
    if file.size > 20 * 1024 * 1024:
        raise HTTPException(413)

    url_key = await storage.upload(config.TG_CHANNEL_ID, file.file, file.filename)
    url = f"{config.URL}/file/{quote(file.filename)}?key={url_key}"
    await file.close()
    if request.headers.get("hx-request") == "true":
        return HTMLResponse(f'<a href="{url}" target="_blank" class="uploaded-url">{url}</a>')
    else:
        return {"url": url}


@app.get("/file/{file_name}", response_class=StreamingResponse, tags=["Functions"])
async def download_file(file_name: str, key: str = Query()):
    try:
        file_id = storage._decode_file_id(key)
        file_data = await storage.get_file_data(file_id)
    except:
        raise HTTPException(404)

    headers = {
        "Content-Disposition": f'inline; filename="{file_name}"',
        "Content-Length": str(file_data["file_size"]),
    }

    return StreamingResponse(file_stream(file_data["url"]), headers=headers)


app.mount("/", StaticFiles(directory="static", html=True))


async def file_stream(url: str) -> AsyncGenerator:
    async with ClientSession() as session:
        async with session.get(url) as resp:
            async for chunk in resp.content.iter_any():
                yield chunk
