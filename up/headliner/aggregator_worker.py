#!/usr/bin/env python
import argparse

from celery import Celery
from celery.bin.worker import worker
from celery import maybe_patch_concurrency

from up.headliner.utils import read_config_file, setup_basic_logger
from up.headliner import Application


def get_worker_config():
    """
    Read configuration from multiple places and start an aggregator worker.
    Configuration is obtain with the following priority:

    default config path > specified json config > up.headliner.settings
    """
    parser = argparse.ArgumentParser(description="Headliner Worker is a program that executes tasks sent through the message broker.")
    parser.add_argument("--config", metavar="config", type=str, help="Specify a json configuration file", default=None)
    options = parser.parse_args()
    config = read_config_file(options)

    return config


config = get_worker_config()
app = Application.instance(config)
aggregator = Celery("headliner", broker=app.message_broker_url, backend=app.task_results_backend_url)


# import the configured tasks
for module_name in config.tasks:
    __import__(module_name)


def main():
    setup_basic_logger()
    aggregator.config_from_object(app.config.scheduler)
    maybe_patch_concurrency()
    worker(aggregator).execute_from_commandline()


if __name__ == "__main__":
    main()
