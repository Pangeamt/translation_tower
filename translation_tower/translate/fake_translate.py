from random import choices
from typing import List, Union, Tuple
from aiohttp_retry import RetryClient
from translation_tower.logger import logger
from translation_tower.format_traceback import format_traceback
from translation_tower.translate.error import TranslatorError


def get_random_urls():
    choice = choices(['success', 'success_with_retry', 'error'], [0.8, 0.1, 0.1])[0]
    if choice == 'success':
        return ["https://httpstat.us/200"]
    elif choice == 'success_with_retry':
        return ["https://httpstat.us/429", "https://httpstat.us/200"]
    else:
        return ["https://httpstat.us/500"]


async def fake_translate(
    texts: List[str],
    source_language: str,
    target_language: str,
    retry_client: RetryClient,
) -> List[str]:

    urls = [

    ]
    try:
        response = await retry_client.get(
            get_random_urls(),
            ssl=False,
        )
        if response.status == 200:
            return [
                f"[Fake {source_language}->{target_language}] {text}" for text in texts
            ]
        else:
            m = f'HTTP Error {response.status} from fake translator'
            logger.warning(m)
            raise TranslatorError(m)

    except Exception as e:
        logger.warning(format_traceback(e))
        raise TranslatorError(str(e))

    finally:
        await retry_client.close()

