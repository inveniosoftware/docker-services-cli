# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Docker-Services-CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI module."""

import sys
from functools import update_wrapper
from distutils.sysconfig import get_python_lib
from pathlib import Path

import click

from .config import SERVICES
from .env import override_default_env, print_setup_env_config, set_env
from .services import services_down, services_up


def normalize_service_name(service_with_version):
    """Return the name of the passed service without version number."""
    for service_name in SERVICES:
        if service_name in service_with_version:
            return service_name


def env_output(env_set_command):
    """Decorate command to print exportable environment settings."""
    if env_set_command not in ["export", "unset"]:
        click.secho("Wrong environment set command.", fg="red")
        exit(1)

    def pass_obj(func):
        @click.option(
            "--env",
            is_flag=True,
            default=False,
            help="Print export statements to set environment.",
        )
        @click.pass_context
        def add_env_output(ctx, *args, **kwargs):

            env = kwargs.pop("env", False)
            services = [
                normalize_service_name(s) for s in kwargs.get("services", [])
            ] or SERVICES.keys()
            if env:
                click.echo(": '")  # comment command output until env export
            ctx.invoke(func, **kwargs)
            if env:
                click.echo("'")  # end of multiline comment, start of export statements
                print_setup_env_config(
                    services,
                    click.get_current_context().info_name,
                    env_set_command=env_set_command,
                )

        return update_wrapper(add_env_output, func)

    return pass_obj


class ServicesCtx(object):
    """Context class for docker services cli."""

    def __init__(self, filepath, verbose):
        """Constructor."""
        self.filepath = filepath
        self.verbose = verbose


@click.group()
@click.version_option()
@click.option(
    "--filepath",
    "-f",
    required=False,
    default=f"{get_python_lib()}/docker_services_cli/docker-services.yml",
    type=click.Path(exists=True),
    help="Path to a docker compose file with the desired services definition.",
)
@click.option(
    "--verbose", is_flag=True, default=False, help="Verbose output.",
)
@click.pass_context
def cli(ctx, filepath, verbose):
    """Initialize CLI context."""
    set_env()
    ctx.obj = ServicesCtx(filepath=filepath, verbose=verbose)


@cli.command()
@click.argument("services", nargs=-1, required=False)  # -1 incompat with default
@click.option(
    "--no-wait", is_flag=True, help="Wait for services to be up (use healthchecks).",
)
@click.option(
    "--retries",
    default=6,
    type=int,
    help="Number of times to retry a service's healthcheck.",
)
@env_output(env_set_command="export")
@click.pass_obj
def up(services_ctx, services, no_wait, retries):
    """Boots up the required services."""
    _services = list(services)

    if not _services:
        click.secho("No service was provided... Exiting", fg="red")
        exit(0)  # Do not fail to allow SQLite

    # NOTE: docker-compose boots up all if none is provided
    if len(_services) == 1 and _services[0].lower() == "all":
        _services = []

    override_default_env(services_to_override=_services)
    click.secho("Environment setup", fg="green")

    normalized_services = [normalize_service_name(s) for s in _services]
    services_up(
        services=normalized_services,
        filepath=services_ctx.filepath,
        wait=(not no_wait),
        retries=retries,
        verbose=services_ctx.verbose,
    )
    click.secho("Services up!", fg="green")


@cli.command()
@env_output(env_set_command="unset")
@click.pass_obj
def down(services_ctx):
    """Boots down the required services."""
    services_down(filepath=services_ctx.filepath)
    click.secho("Services down!", fg="green")
