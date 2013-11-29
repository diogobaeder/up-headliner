#!/usr/bin/env python
from up.headliner import Application
from up.headliner.utils import get_aggregator_config
from celery.bin.beat import main as beat_main
from celery import maybe_patch_concurrency


def main():
    config = get_aggregator_config()
    app = Application.instance(config)
    maybe_patch_concurrency()
    beat_main("up.headliner.tasks.aggregator")

if __name__ == "__main__":
    main()
