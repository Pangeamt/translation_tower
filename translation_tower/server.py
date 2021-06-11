from aiohttp import web
from translation_tower.translation_app_name import TRANSLATION_APP_NAME
from translation_tower.server_config import ServerConfig
from translation_tower.translation_app import TranslationApp
from translation_tower.server_handler.translate import translate
from rororo import OperationTableDef, setup_openapi


class Server:
    def __init__(self, config: ServerConfig, web_application: web.Application, site: web.TCPSite):
        self._config = config
        self._web_application = web_application
        self._site = site

    @property
    def site(self):
        return self._site

    @property
    def config(self):
        return self._config

    @staticmethod
    async def create(config: ServerConfig, app: TranslationApp) -> "Server":
        # Server
        web_application = web.Application(client_max_size=config.client_max_size)

        # Inject app in web application
        web_application[TRANSLATION_APP_NAME] = app

        # Register startup and shutdown handler
        web_application.on_startup.append(Server.on_startup)
        web_application.on_shutdown.append(Server.on_shutdown)

        # OpenAPI
        operations = OperationTableDef()
        operations.register(translate)

        # Register OpenAPI schema
        web_application = setup_openapi(
            web_application,
            config.openapi,
            operations
        )

        # Site
        runner = web.AppRunner(web_application)
        await runner.setup()
        site = web.TCPSite(runner, config.host, config.port)

        # Create server
        return Server(config, web_application, site)

    @staticmethod
    async def on_startup(web_application: web.Application):
        # Startup app
        await web_application[TRANSLATION_APP_NAME].start()

    @staticmethod
    async def on_shutdown(web_application: web.Application):
        # Shutdown app
        await web_application[TRANSLATION_APP_NAME].stop()
