import base64
from typing import BinaryIO
from aiohttp import ClientSession
from aiohttp import FormData
import pyaes
from hashlib import sha256


class TGFiles:
    def __init__(self, bot_token: str) -> None:
        self.bot_token: str = bot_token

    async def _api_call(self, method: str, parameters: dict | None = None) -> dict:
        api_endpoint = f"https://api.telegram.org/bot{self.bot_token}/{method}"
        async with ClientSession() as session:
            async with session.post(api_endpoint, data=parameters) as resp:
                response: dict = await resp.json()

        if response.get("ok"):
            return response.get("result")
        else:
            raise Exception(response)

    async def upload(self, channel_id: int, file: BinaryIO, file_name) -> str:
        upload_payload = FormData()
        upload_payload.add_field("chat_id", str(channel_id))
        upload_payload.add_field("disable_content_type_detection", "true")
        upload_payload.add_field("document", value=file, filename=file_name)
        upload_message = await self._api_call("sendDocument", upload_payload)

        message_id = upload_message["message_id"]
        file_id = upload_message["document"]["file_id"]
        url_key = self._encode_file_id(file_id)
        caption = (
            f"chat_id: {channel_id}\n\n"
            + f"message_id: {message_id}\n\n"
            + f"file_id: {file_id}\n\n"
            + f"url_key: {url_key}"
        )

        edit_payload = {
            "chat_id": channel_id,
            "message_id": upload_message["message_id"],
            "caption": caption,
        }

        await self._api_call("editMessageCaption", edit_payload)
        return url_key

    async def get_file_data(self, file_id: str) -> dict:
        file = await self._api_call("getFile", {"file_id": file_id})
        file["url"] = f"https://api.telegram.org/file/bot{self.bot_token}/{file['file_path']}"
        return file

    def _encode_file_id(self, file_id) -> str:
        aes = pyaes.AESModeOfOperationCTR(sha256(self.bot_token.encode()).digest())
        file_id_encoded = aes.encrypt(file_id)
        return base64.urlsafe_b64encode(file_id_encoded).decode()

    def _decode_file_id(self, file_id_encoded) -> str:
        aes = pyaes.AESModeOfOperationCTR(sha256(self.bot_token.encode()).digest())
        file_id = aes.decrypt(base64.urlsafe_b64decode(file_id_encoded)).decode()
        return file_id
