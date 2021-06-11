import aiohttp
from aiohttp_retry import ListRetry, RetryClient
from types import SimpleNamespace
from aiohttp import TraceConfig, TraceRequestStartParams
from translation_tower.logger import logger
from functools import partial


async def before_translator_send_request(
    session: aiohttp.ClientSession,
    trace_config_ctx: SimpleNamespace,
    params: TraceRequestStartParams,
    batch_id: str,
) -> None:
    current_attempt = trace_config_ctx.trace_request_ctx["current_attempt"]
    if current_attempt > 1:
        logger.warning(f"Retry to send batch {batch_id}")


def create_retry_client(batch_id) -> RetryClient:
    retry_options = ListRetry(
        timeouts=[0.05, 1.0, 3.0, 10.0],
        statuses={429, 500},
        exceptions={aiohttp.ClientConnectorError},
    )

    trace_config = TraceConfig()
    fn = partial(before_translator_send_request, batch_id=batch_id)
    trace_config.on_request_start.append(fn)
    retry_client = RetryClient(
        retry_options=retry_options, trace_configs=[trace_config]
    )

    return retry_client
