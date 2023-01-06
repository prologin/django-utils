# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

import logging

import structlog
from celery import Celery, signals
from django.conf import settings
from django_structlog.celery.steps import DjangoStructLogInitStep

app = Celery(settings.PROJECT_NAME)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.steps["worker"].add(DjangoStructLogInitStep)

app.autodiscover_tasks()

app.conf.beat_scheduler = "django_celery_beat.schedulers.DatabaseScheduler"

app.conf.beat_schedule = {
    "send-queued-mail": {
        "task": "post_office.tasks.send_queued_mail",
        "schedule": 600.0,
        "kwargs": {
            "days": 365,
        },
    },
}


@signals.setup_logging.connect
def receiver_setup_logging(
    loglevel, logfile, format, colorize, **kwargs  # noqa
):
    logging.config.dictConfig(settings.LOGGING)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
