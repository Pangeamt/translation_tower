import asyncio
from asyncio import Event
from typing import List, Dict
from pathlib import Path
from collections import Counter
from asyncio.queues import Queue
from translation_tower.translation_cache import TranslationCache
from translation_tower.translation_cache_config import TranslationCacheConfig
from translation_tower.secret_config import SecretConfig
from translation_tower.translation_job import TranslationJob
from translation_tower.translation_app_config import TranslationAppConfig
from translation_tower.logger import logger
from translation_tower.annotated_text_to_html import (
    annotated_text_to_html,
    html_to_annotated_text,
)
from translation_tower.language import Language
from translation_tower.translator import Translator, translator_to_string
from translation_tower.translate.create_retry_client import create_retry_client
from translation_tower.translate.bing_translate import bing_translate
from translation_tower.translate.deepl_translate import deepl_translate
from translation_tower.translate.fake_translate import fake_translate
from translation_tower.format_traceback import format_traceback
from translation_tower.annotation import annotation_from_dict
from itertools import zip_longest
import rororo
from dkpro_cassis_tools import load_cas_from_zip_file, dump_cas_to_zip_file
from translation_tower.deep_texts_to_cas import cas_to_deep_texts, deep_texts_to_cas
from web_anno_tsv import open_web_anno_tsv


class TranslationApp:
    def __init__(
        self,
        cache_config: Path,
        translation_app_config: Path,
        language_config: Path,
        secret_config: Path,
    ):
        self._cache = TranslationCache(TranslationCacheConfig.load(cache_config))
        self._config = TranslationAppConfig.load(translation_app_config)
        self._secret_config = SecretConfig.load(secret_config)
        self._language = Language(language_config)
        self._request_id = 0
        self._batch_id = 0

        self._translation_queues = dict()
        self._translation_queue_readers = dict()

        self._max_concurrent_requests_by_translator = dict(
            bing=asyncio.BoundedSemaphore(self._config.bing_limit_concurrent_request),
            deepl=asyncio.BoundedSemaphore(self._config.deepl_limit_concurrent_request),
        )

    def create_jobs_from_json(self, texts, request_id: str):
        jobs = [
            self.create_job_from_json(request_id, i, t) for i, t in enumerate(texts)
        ]
        return jobs

    def create_job_from_json(
        self,
        request_id,
        index,
        text_item: Dict,
    ):
        try:
            text = text_item.get("text")
            translator = text_item.get("translator")
            translator_html_mode = text_item.get("translator_html_mode")
            translator_fake_mode = text_item.get("translator_fake_mode")
            source_language = self.language.get(
                text_item.get("source_lang"), translator
            )
            target_language = self.language.get(
                text_item.get("target_lang"), translator, for_translation=True
            )
            annotations = text_item.get("annotations", None)
            if annotations:
                annotations = list(map(lambda a: annotation_from_dict(a), annotations))
                for annotation in annotations:
                    if not 0 <= annotation.start < annotation.stop <= len(text):
                        raise ValueError(f"Invalid annotation offsets at item {index}")

            use_cache = text_item.get("use_cache")

            job = TranslationJob(request_id, index)
            job.source.text = text
            job.source.language = source_language
            job.source.annotations = annotations
            job.target.language = target_language
            job.translator.name = translator
            job.translator.html_mode = translator_html_mode
            job.translator.fake_mode = translator_fake_mode
            job.use_cache = use_cache
            return job

        except Exception as e:
            logger.error(format_traceback(e))
            raise rororo.openapi.BadRequest(message=str(e))

    def create_request_id(self) -> str:
        self._request_id += 1
        return str(self._request_id)

    def create_batch_id(self) -> str:
        self._batch_id += 1
        return str(self._batch_id)

    @property
    def language(self) -> Language:
        return self._language

    @property
    def cache(self):
        return self._cache

    async def start(self):
        pass

    async def stop(self):
        for key in self._translation_queue_readers:
            self._translation_queue_readers[key].cancel()

    @staticmethod
    def translation_queue_key(
        text_language: str,
        translation_language: str,
        translator: Translator,
    ):
        """
        Create a unique key for translations queues
        :param text_language:
        :param translation_language:
        :param translator:
        :return:
        """
        return (
            f"{translator_to_string(translator)}/{text_language}/{translation_language}"
        )

    def get_translation_queue(
        self,
        source_language: str,
        target_language: str,
        translator: Translator,
    ):
        key = self.translation_queue_key(source_language, target_language, translator)
        if key in self._translation_queues:
            return self._translation_queues[key]
        else:
            self._translation_queues[key] = Queue(maxsize=20)
            self._translation_queue_readers[key] = asyncio.create_task(
                self.translate_from_queue(
                    queue=self._translation_queues[key],
                    translator=translator,
                )
            )
            return self._translation_queues[key]

    async def translate_jobs(self, jobs: List[TranslationJob]):
        """
        Step 1: called from server handler to process the request

        :param jobs:
        :return:
        """
        try:
            for i, job in enumerate(jobs):
                job.to_translator = job.source.text
                annotations = job.source.annotations

                if annotations:
                    html, rebuild = annotated_text_to_html(
                        job.to_translator, annotations
                    )
                    job.to_translator = html
                    job.annotation_rebuild = rebuild
                    job.translator.html_mode = True

                cached_translation = (
                    self.cache.get(
                        text=job.to_translator,
                        source_language=job.source.language,
                        target_language=job.target.language,
                        translator=job.translator,
                    )
                    if job.use_cache
                    else None
                )

                if cached_translation:
                    job.from_cache = True
                    job.from_translator = cached_translation.translation
                else:
                    job.done = Event()
                    queue = self.get_translation_queue(
                        job.source.language, job.target.language, job.translator
                    )
                    await queue.put(job)

            # Non cached jobs
            not_cached = list(filter(lambda j: j.from_cache is False, jobs))

            # Wait
            await asyncio.gather(*list(map(lambda j: j.done.wait(), not_cached)))

            for job in jobs:
                if not job.error:
                    if not job.source.annotations:
                        job.target.text = job.from_translator
                    else:
                        text, annotations = html_to_annotated_text(
                            job.from_translator, job.annotation_rebuild
                        )
                        job.target.text = text
                        job.target.annotations = annotations

            # Return translated job
            return jobs

        except asyncio.CancelledError:
            processing_jobs = list(filter(lambda j: j.done is not None, jobs))
            logger.info(
                f"Translation request nº{jobs[0].request_id} "
                f"interrupted at {round(len(processing_jobs)*100/len(jobs), 2)}%"
            )
            raise

    async def translate_from_queue(self, queue: asyncio.Queue, translator: Translator):

        jobs = []
        length = 0

        if translator.name == "bing":
            limit_texts_per_request = self._config.bing_limit_texts_per_request
            limit_chars_per_request = self._config.bing_limit_chars_per_request
        elif translator.name == "deepl":
            limit_texts_per_request = self._config.deepl_limit_texts_per_request
            limit_chars_per_request = self._config.deepl_limit_chars_per_request
        else:
            raise ValueError(f"Invalid translator {translator.name}")
        while True:
            try:
                job = await asyncio.wait_for(queue.get(), 1.0)
                if (
                    len(jobs) + 1 > limit_texts_per_request
                    or length + len(job.to_translator) > limit_chars_per_request
                ):
                    if jobs:
                        await self.create_translation_task(
                            jobs=jobs,
                        )
                    # todo
                    jobs = [job]
                    length = len(job.to_translator)

                else:
                    jobs.append(job)
                    length += len(job.to_translator)
            except asyncio.exceptions.TimeoutError:
                if jobs:
                    await self.create_translation_task(
                        jobs=jobs,
                    )
                    jobs = list()
                    length = 0
            except Exception as e:
                # TODO
                print("ERROR:", e)
                ...

    async def create_translation_task(
        self,
        jobs: List[TranslationJob],
    ):

        semaphore = self._max_concurrent_requests_by_translator[jobs[0].translator.name]
        await semaphore.acquire()

        asyncio.create_task(
            self.send_to_translator(
                jobs,
                semaphore,
            )
        )

    async def send_to_translator(
        self,
        jobs: List[TranslationJob],
        semaphore: asyncio.Semaphore,
    ):
        try:
            # batch Id
            batch_id = self.create_batch_id()

            # Extract relevant data from first job
            first_job = jobs[0]
            source_language = first_job.source.language
            target_language = first_job.target.language
            translator = first_job.translator

            # Extracts texts
            texts = [job.to_translator for job in jobs]

            # logging
            requests = Counter(list(map(lambda j: j.request_id, jobs)))
            request_info = ", ".join([f"{k}: {v} text(s)" for k, v in requests.items()])
            logger.info(
                f"Send batch nº {batch_id} to {translator_to_string(translator)} "
                f"{source_language}->{target_language} "
                f"with {len(jobs)} text(s) "
                f"proceeding from request {request_info}"
            )

            retry_client = create_retry_client(batch_id=batch_id)

            if translator.fake_mode:
                translations = await fake_translate(
                    texts,
                    source_language,
                    target_language,
                    retry_client,
                )

            # Bing
            elif translator.name == "bing":
                translations = await bing_translate(
                    texts,
                    self._language.get(source_language, "bing"),
                    self._language.get(target_language, "bing", for_translation=True),
                    translator.html_mode,
                    self._secret_config.bing_apikey,
                    retry_client,
                )

            # Deepl
            elif translator.name == "deepl":
                translations = await deepl_translate(
                    texts,
                    self._language.get(source_language, "deepl"),
                    self._language.get(target_language, "deepl", for_translation=True),
                    translator.html_mode,
                    self._secret_config.deepl_apikey,
                    retry_client,
                )

            for job, translation in zip_longest(jobs, translations):
                job.from_translator = translation
                if job.use_cache:
                    self._cache.set(
                        text=job.to_translator,
                        translation=job.from_translator,
                        source_language=job.source.language,
                        target_language=job.target.language,
                        translator=job.translator,
                    )

        except Exception as e:
            for job in jobs:
                job.error = True
                job.error_message = str(e)

        finally:
            semaphore.release()
            for job in jobs:
                job.done.set()

    async def translate_xmi_file(
        self,
        xmi: str,
        translated_xmi: str,
        source_lang: str,
        target_lang: str,
        translator: str,
        translator_fake_mode: True,
        use_cache=True,
    ):
        request_id = self.create_request_id()

        # Extract text and annotations from xmi
        with open(xmi, 'rb') as f:
            cas = load_cas_from_zip_file(f)

        # Type system
        cas_type_system = cas.typesystem

        # Create jobs
        jobs = list()
        deep_texts = cas_to_deep_texts(cas)
        for i, deep_text in enumerate(deep_texts):
            deep_text.language = source_lang
            job = TranslationJob(request_id=request_id, index=i, source=deep_text)
            job.target.language = target_lang
            job.translator.name = translator
            job.translator.fake_mode = translator_fake_mode
            job.use_cache = use_cache
            jobs.append(job)

        await self.translate_jobs(jobs)

        for job in jobs:
            if job.error:
                raise ValueError(str(job.error_message))

        new_cas = deep_texts_to_cas([j.target for j in jobs], cas_type_system)
        with open(translated_xmi, 'wb') as f:
            dump_cas_to_zip_file(new_cas, f)



