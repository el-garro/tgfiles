import json
from random import randbytes
from typing import BinaryIO
from aiohttp import ClientSession
from aiohttp import FormData


class tgFiles:
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

    async def get_message(self, channel_id: int, message_id: int):
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": f"{channel_id}:{message_id}",
                        "callback_data": randbytes(8).hex(),
                    },
                ]
            ]
        }

        payload = {
            "chat_id": channel_id,
            "message_id": message_id,
            "reply_markup": json.dumps(reply_markup),
        }

        return await self._api_call("editMessageReplyMarkup", payload)

    async def upload(self, channel_id: int, file: BinaryIO, filename) -> int:
        upload_payload = FormData()
        upload_payload.add_field("chat_id", str(channel_id))
        upload_payload.add_field("caption", filename)
        upload_payload.add_field("disable_content_type_detection", "true")
        upload_payload.add_field("document", value=file, filename=filename)
        upload_message = await self._api_call("sendDocument", upload_payload)

        upload_message_id = upload_message["message_id"]
        final_message = await self.get_message(channel_id, upload_message_id)
        return final_message["message_id"]

    async def get_file_data(self, channel_id: int, message_id: int):
        message = await self.get_message(channel_id, message_id)
        file_id = message["document"]["file_id"]
        file_name = message["document"]["file_name"]
        mime_type = message["document"].get("mime_type", "application/octet-stream")
        file_size = message["document"]["file_size"]

        file = await self._api_call("getFile", {"file_id": file_id})
        file_path = file["file_path"]
        response = {
            "file_name": file_name,
            "mime_type": mime_type,
            "file_size": file_size,
            "url": f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}",
        }
        return response
