﻿__title__ = 'sloth-ci.ext.docker_exec'
__description__ = 'Docker executor app extension for Sloth CI'
__long_description__ = 'Docker executor Sloth CI app extension that replaces the default executor and runs actions inside a given Docker image.'
__version__ = '0.1.3'
__author__ = 'Konstantin Molchanov'
__author_email__ = 'moigagoo@live.com'
__license__ = 'MIT'


"""Docker executor Sloth CI app extension that replaces the default executor and runs actions inside a given Docker image.

Config params:

[docker_exec]
;Image name. If missing, the Sloth app name is used.
image = foo

;Path to the Docker daemon to connect to. Can point to either a tcp URL or a unix socket. If missing, the client connects to */var/run/docker.sock
base_url = tcp://555.55.55.55:5555 *.

;Path to the Dockerfile used to build an image if it doesn't exist. If missing, current directory is used.
path_to_dockerfile = docker/files 

All config params are optional.
"""


from docker import Client
from docker.errors import APIError


def extend(cls):
    class Sloth(cls):
        def __init__(self, config):
            super().__init__(config)

            self._docker_config = self.config['docker']

            self._docker_client = Client(self._docker_config.get('base_url'))

            self._docker_image = self._docker_config.get('image') or self.name

        def execute(self, action):
            """Execute an action inside a container, then commit the changes to the image and remove the container.

            :param action: action to be executed

            :returns: True if successful, Exception otherwise
            """

            self.processing_logger.info('Executing action: %s', action)

            try:
                try:
                    container_id = self.docker_client.create_container(
                        self._docker_image,
                        command=action,
                        working_dir=self.config.get('work_dir') or '.'
                    )['Id']

                except APIError as e:
                    if e.response.status_code == 404:
                        self.docker_client.build(
                            self._docker_config.get('path_to_dockerfile') or '.',
                            tag=self._docker_image
                        )

                        container_id = self.docker_client.create_container(
                            self._docker_image,
                            command=action,
                            working_dir=self.config['work_dir']
                        )['Id']

                    else:
                        raise

                self.docker_client.start(container_id)
                self.docker_client.commit(
                    container_id,
                    self._docker_image,
                    message=action
                )
                self.docker_client.remove_container(container_id)

                self.processing_logger.info('Action executed: %s', action)
                return True

            except Exception:
                raise

    return Sloth