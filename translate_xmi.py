import asyncio
import logging
import translation_tower as tt
from translation_tower.logger import logger_default_policy
from pathlib import Path

# Logger
logger = logging.getLogger()
logger_default_policy(logger, file="data/log.log")


async def main():
    # Start translation app (Internally, the app use a translation cache)
    app = tt.App(
        cache_config=Path("data/config/cache.yaml"),
        translation_app_config=Path("data/config/translation_app.yaml"),
        language_config=Path("data/config/languages.csv"),
        secret_config=Path("data/config/secret.yaml"),
    )
    await app.start()

    await app.translate_xmi_file(
        xmi="webanno6958664086768861001export.zip",  # the xmi file to translate
        translated_xmi="webanno6958664086768861001export_translated.zip",  # the path of the translated xmi file
        source_lang="bg",
        target_lang="en",
        translator="bing",  # or bing
        translator_fake_mode=True,  # any real call do deepl is made. so you can test your code
    )

    # Stop translation app
    await app.stop()

asyncio.get_event_loop().run_until_complete(main())




