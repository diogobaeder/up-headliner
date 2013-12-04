__import__('pkg_resources').declare_namespace(__name__)
import redis
from up.headliner import settings

DEFAULT_CONFIG_FILEPATH = "/etc/up/headliner.json"

class Application(object):
    def __init__(self, config):
        self.config = config
        self._redis_pool = redis.ConnectionPool(
                host=config.redis["host"],
                port=config.redis["port"],
                db=config.redis["database"],
                password=config.redis["password"],
                max_connections=config.redis["max_connections"],
        )

        if not hasattr(Application, "_instance"):
            Application._instance = self

    def get_redis_connection(self):
        return redis.Redis(connection_pool=self._pool)

    @property
    def storage_url(self):
        if self.config.redis.get("password"):
            url = "redis://{password}@{host}:{port}/{database}".format(**self.config.redis)
        else:
            url = "redis://{host}:{port}/{database}".format(**self.config.redis)
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
        return self.config.providers

    @classmethod
    def instance(cls, config=None):
        if hasattr(Application, "_instance"):
            return Application._instance
        else:
            return Application(config)
