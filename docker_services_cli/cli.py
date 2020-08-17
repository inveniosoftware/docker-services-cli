# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Docker-Services-CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI module."""

import sys
from distutils.sysconfig import get_python_lib
from pathlib import Path

import click

from .env import set_env
from .services import services_down, services_up


@click.group()
@click.version_option()
def cli():
    """Initialize CLI context."""


@cli.command()
@click.argument(
    "action",
    default="up",
    required=False,
    type=click.Choice(["up", "down"], case_sensitive=False),
)
@click.argument("services", nargs=-1, required=False)  # -1 incompat with default
@click.option(
    "--filepath",
    "-f",
    required=False,
    default=f"{get_python_lib()}/docker_services_cli/docker-services.yml",
    type=click.Path(exists=True),
    help="Path to a docker compose file with the desired services definition.",
)
def services(action, services, filepath):
    """Boots up or down the required services."""
    set_env()
    if action == "up":
        services_up(list(services), filepath)

    else:
        services_down(filepath)
