# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Docker-Services-CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Services module."""

import subprocess

from .config import DOCKER_SERVICES_FILEPATH


def services_down(filepath=DOCKER_SERVICES_FILEPATH):
    """Stops the given services.

    It does not requries the services. It stops containers and removes
    containers, networks, volumes, and images created by ``up``.
    """
    command = ["docker-compose", "--file", filepath, "down"]

    subprocess.run(command, check=True)


def services_up(services, filepath=DOCKER_SERVICES_FILEPATH):
    """Start the given services up.

    docker-compose is smart about not rebuilding an image if
    there is no need to, so --build is not a slow default. In addition
    ``--detach`` is not supported in 1.17.0 or previous.
    """
    command = ["docker-compose", "--file", filepath, "up", "-d"]

    command.extend(services)

    subprocess.run(command, check=True)
