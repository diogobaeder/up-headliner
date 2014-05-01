#!/usr/bin/env python
import argparse

from celery import Celery
from celery.bin.beat import beat
from celery import maybe_patch_concurrency

from up.headliner.utils import __read_config_file, setup_basic_logger
from up.headliner import Application


def get_scheduler_config():
    """
    Read configuration from multiple places and start an aggregator scheduler.
    Configuration is obtain with the following priority:

    default config path > specified json config > up.headliner.settings
    """
    parser = argparse.ArgumentParser(description="Headliner Scheduler is a program that sends tasks periodically. Tasks are configured in headliner's configuration file.")
    parser.add_argument("--config", metavar="config", type=str, help="Specify a json configuration file", default=None)
    options = parser.parse_args()
    config = __read_config_file(options)

    return config


config = get_scheduler_config()
app = Application.instance(config)
aggregator = Celery("headliner", broker=app.message_broker_url, backend=app.task_results_backend_url)


def main():
    setup_basic_logger()
    aggregator.config_from_object(app.config.scheduler)
    maybe_patch_concurrency()
    beat(aggregator).execute_from_commandline()


if __name__ == "__main__":
    main()
