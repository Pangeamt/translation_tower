from typing import List, Dict
import asyncio
from aiohttp import web
from rororo import openapi_context
from translation_tower.translation_app_name import TRANSLATION_APP_NAME
from translation_tower.translation_app import TranslationApp
from translation_tower.annotation import (
    annotation_from_dict,
    annotation_to_dict,
)
from translation_tower.translation_job import TranslationJob
from translation_tower.logger import logger
from translation_tower.format_traceback import format_traceback
import rororo


async def translate(request: web.Request) -> web.Response:
    try:
        # Translation app
        app: TranslationApp = request.app[TRANSLATION_APP_NAME]

        # Request id
        request_id = app.create_request_id()

        # Info
        logger.info(f"Handle translation request nº{request_id}")

        # Read request params and create jobs
        with openapi_context(request) as context:
            texts = context.data.texts
        jobs = app.create_jobs_from_json(texts, request_id)

        # Translate jobs
        await app.translate_jobs(jobs)

        # Check error
        for job in jobs:
            if job.error:
                raise rororo.openapi.ServerError(message=job.error_message)

        logger.info(f"Finish translation request nº{request_id}")

        # Response
        return web.json_response(
            {
                "translations": _jobs_to_translations(jobs)
            }
        )

    except asyncio.CancelledError:
        raise


def _jobs_to_translations(jobs):
    has_annotations = True if list(filter(lambda j: j.source.annotations is not None, jobs)) else False

    translations = list()
    for job in jobs:
        d = dict()
        d["text"] = job.source.text
        d["translation"] = job.target.text
        d["source_lang"] = job.source.language
        d["target_lang"] = job.target.language
        if has_annotations:
            if job.source.annotations is None:
                d["source_annotations"] = []
            else:
                d["source_annotations"] = list(
                    map(annotation_to_dict, job.source.annotations)
                )
            if job.target.annotations is None:
                d["target_annotations"] = []
            else:
                d["target_annotations"] = list(
                    map(annotation_to_dict, job.target.annotations)
                )
        d["translate"] = job.translator.name
        d["from_cache"] = job.from_cache
        translations.append(d)
    return translations
