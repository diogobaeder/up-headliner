from celery import Celery
from up.headliner.utils import get_aggregator_config
from up.headliner import Application

config = get_aggregator_config()
app = Application.instance(config)

aggregator = Celery("headliner", broker=app.message_broker_url)
