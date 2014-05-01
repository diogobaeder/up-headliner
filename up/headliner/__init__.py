__import__('pkg_resources').declare_namespace(__name__)

import redis

from up.headliner.data import ArticleStore


__VERSION__ = "0.5"
DEFAULT_CONFIG_FILEPATH = "/etc/headliner/webserver.json"


class Application(object):
    def __init__(self, config):
        self.config = config
        self._redis_pool = redis.ConnectionPool(
            host=config.redis["host"],
            port=config.redis["port"],
            db=config.redis["database"],
            password=config.redis["password"],
        )
        self._providers = {}
        for name, config_details in config.providers.iteritems():
            pieces = config_details["api_class"].split(".")
            class_name = pieces[-1]
            module_name = ".".join(pieces[:-1])

            module = __import__(module_name, fromlist=[class_name])
            self._providers[name] = getattr(module, class_name)(config_details)

        self.article_store = ArticleStore(self._redis_pool)

        if not hasattr(Application, "_instance"):
            Application._instance = self

    @property
    def storage_url(self):
        if self.config.redis.get("password"):
            url = "redis://{password}@{host}:{port}/{database}".format(**self.config.redis)
        else:
            url = "redis://{host}:{port}/{database}".format(**self.config.redis)
        return url

    @property
    def task_results_backend_url(self):
        if self.config.task_results_backend.get("password"):
            url = "{type}://{password}@{host}:{port}/{database}".format(**self.config.task_results_backend)
        else:
            url = "{type}://{host}:{port}/{database}".format(**self.config.task_results_backend)
        return url

    @property
    def message_broker_url(self):
        if self.config.message_broker.get("password"):
            url = "{type}://{password}@{host}:{port}/{database}".format(**self.config.message_broker)
        else:
            url = "{type}://{host}:{port}/{database}".format(**self.config.message_broker)
        return url

    @property
    def providers(self):
        return self._providers

    @property
    def provider_configs(self):
        return self.config.providers

    @classmethod
    def instance(cls, config=None):
        if hasattr(Application, "_instance") and config is None:
            return Application._instance
        else:
            return Application(config)
