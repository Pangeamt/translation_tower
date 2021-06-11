from typing import List, Union, Dict
import aiohttp
import asyncio
from translation_tower.deep_text import DeepText


class Client:
    def __init__(self, base_url: str, api_version):
        self._base_url = base_url
        self._api_version = api_version

    def get_base_url(self) -> str:
        return self._base_url

    base_url = property(get_base_url)

    async def translate(
        self,
        data: Dict,
        timeout: int = 300,
    ):
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                async with session.post(
                    f"{self._base_url}/api/{self._api_version}/translate",
                    json=data,
                ) as response:
                    if response.status == 200:
                        content = await response.json()
                        return True, content

                    else:
                        content = await response.json()
                        detail = content["detail"]
                        return False, f"Error {response.status}: {detail}"

        except asyncio.TimeoutError:
            return False, "Timeout error"
        except Exception as e:
            return False, str(e)
