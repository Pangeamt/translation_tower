from typing import List, Union, Tuple
import uuid
from aiohttp_retry import RetryClient
from translation_tower.logger import logger
from translation_tower.format_traceback import format_traceback
from translation_tower.translate.error import TranslatorError


async def bing_translate(
    texts: List[str],
    source_language: str,
    target_language: str,
    html_mode: bool,
    api_key: str,
    retry_client: RetryClient,
) -> List[str]:
    try:
        url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"

        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Content-type": "application/json",
            'Ocp-Apim-Subscription-Region': "westeurope",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        params = list()
        params.append(("from", source_language))
        params.append(("to", target_language))
        if html_mode:
            params.append(("textType", "html"))
        body = list(map(lambda t: {"text": t}, texts))

        response = await retry_client.post(
            url,
            params=params,
            headers=headers,
            json=body,
        )
        if response.status == 200:
            data = await response.json()
            translations = list(map(lambda r: r["translations"][0]["text"], data))
            return translations
        else:
            m = f'HTTP Error {response.status} from bing translator'
            logger.warning(m)
            raise TranslatorError(m)

    except Exception as e:
        logger.warning(format_traceback(e))
        raise TranslatorError(str(e))

    finally:
        await retry_client.close()
