from typing import List, Union, Tuple
from aiohttp_retry import RetryClient
from translation_tower.logger import logger
from translation_tower.format_traceback import format_traceback
from translation_tower.translate.error import TranslatorError


async def deepl_translate(
    texts: List[str],
    source_language: str,
    target_language: str,
    html_mode: bool,
    api_key: str,
    retry_client: RetryClient,
) -> List[str]:
    try:
        url = 'https://api.deepl.com/v2/translate'

        params = list()
        params.append(('auth_key', api_key))
        params.append(('source_lang', source_language))
        params.append(("target_lang", target_language))
        params.append(("split_sentences", "0"))

        if html_mode:
            params.append(("tag_handling", "xml"))

        for text in texts:
            params.append(("text", text))

        response = await retry_client.post(
            url,
            params=params,
        )
        if response.status == 200:
            data = await response.json()
            translations = [t['text'] for t in data["translations"]]
            return translations
        else:
            m = f'HTTP Error {response.status} from deepl translator'
            logger.warning(m)
            raise TranslatorError(m)

    except Exception as e:
        logger.warning(format_traceback(e))
        raise TranslatorError(str(e))

    finally:
        await retry_client.close()




# import logging
# import sys
# import traceback
#
# import aiohttp
#
# from app.helpers import language_code_transformers
# from app.translation_filters.taghandling import DeepLTagHandler
# from app.translators.Translator import Translator
# from app.enums import MT
# from app.trans_unit import TransUnitList
#
# #Deepl api reference: https://www.deepl.com/docs-api/translating-text/in-text-markup/
# #ToDo refactor: if more options than apply_hashtag_filter are needed, use better solution than if elses
# from app.constants import KEEP_RUNNING_AFTER_EXCEPTION
#
#
# class DeeplTranslator(Translator):
#     RESP_TRANSLATIONS = "translations"
#     RESP_TRANSLATION = "text"
#
#     MT_TYPE = MT.DEEPL
#
#     def __init__(self, api_key, apply_hashtag_filter=False):
#         self._deepl_key = api_key
#         self._url = 'https://api.deepl.com/v2/translate'
#         self._apply_hashtag_filter = apply_hashtag_filter
#
#         if self._apply_hashtag_filter:
#             self._tag_handler = DeepLTagHandler()
#
#     async def translate(self, trans_units: TransUnitList) -> (int, str):
#         src_lang = language_code_transformers.get_deepL_source_language_code(trans_units.src_lang)
#         tgt_lang = language_code_transformers.get_deepL_target_language_code(trans_units.tgt_lang)
#
#         params = []
#         params.append(('auth_key', self._deepl_key))
#         params.append(('source_lang', src_lang))
#         params.append(("target_lang", tgt_lang))
#         params.append(("split_sentences", "0"))
#
#         if self._apply_hashtag_filter:
#             params.append(("tag_handling", "xml"))
#             params.append(("ignore_tags", "ignore"))
#
#         for t in trans_units:
#             text = t.src
#             if self._apply_hashtag_filter:
#                 text = self._tag_handler.add_no_translate_tags(text)
#             params.append(("text", text))
#
#         async with aiohttp.ClientSession() as session:
#             try:
#                 async with session.post(self._url, params=params) as resp:
#                     if resp.status == 200:
#                         data = await resp.json()
#                         translations = data[self.RESP_TRANSLATIONS]
#                         if len(translations) != len(trans_units):
#                             warning_text = "DEV WARNING from deepL translator. \n\t" \
#                                            "The list of translations returned by deepL is of different length than the" \
#                                            "list passed to it. This should never happen. Please investigate. " \
#                                            f"\n\tDeepL translations: {translations}\n\tOriginal tsvs: {trans_units}"
#                             logging.error(warning_text)
#                             return (-1, warning_text)
#                         for tu, translation in zip(trans_units, translations):
#                             tgt = translation[self.RESP_TRANSLATION]
#                             if self._apply_hashtag_filter:
#                                 translation_with_tags = tgt
#                                 tgt = self._tag_handler.remove_no_translate_tags(translation_with_tags)
#                             tu.tgt = tgt
#                         return resp.status, ""
#                     else:
#                         payload = await resp.text()
#                         return resp.status, payload
#             except Exception as e:
#                 exc_type, exc_value, exc_traceback = sys.exc_info()
#                 exc_info = "ERROR caught in DeeplTranslator.translate: " + \
#                            "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
#                 logging.exception(exc_info)
#                 if KEEP_RUNNING_AFTER_EXCEPTION:
#                     return -1, exc_info
#                 else:
#                     raise e




