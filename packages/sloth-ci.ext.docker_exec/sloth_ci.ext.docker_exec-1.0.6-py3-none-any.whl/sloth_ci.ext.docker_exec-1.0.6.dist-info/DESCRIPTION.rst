Docker executor Sloth CI app extension that replaces the default executor and runs actions inside a given Docker image.

Config params::

    [docker_exec]
    ;Image name. If missing, the Sloth app name is used.
    image = foo

    ;Path to the Docker daemon to connect to. Can point to either a tcp URL or a unix socket. If missing, the client connects to /var/run/docker.sock.
    base_url = tcp://555.55.55.55:5555

    ;Docker API version used on the server. If missing, the latest version is used.
    version = 1.10

    ;Path to the Dockerfile used to build an image if it doesn't exist. If missing, current directory is used.
    path_to_dockerfile = docker/files

All config params are optional.


