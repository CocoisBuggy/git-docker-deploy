import os
import shutil
import subprocess
import docker
import yaml
from .logger import log


def which_docker_compose():
    """
    There are two ways docker compose can be run, depending on how new the system
    is and when docker compose was installed. One day is to call via docker-compose
    and the other is to call via docker compose.
    We first need to check which one is available and then run it
    """
    # Check if 'docker-compose' is available
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    # Check if 'docker compose' is available
    elif shutil.which("docker"):
        return ["docker", "compose"]

    raise Exception("Neither 'docker-compose' nor 'docker compose' is available")


def system_has_docker():
    return shutil.which("docker") is not None


def can_execute_docker_compose():
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
        )

        if "permission denied" in result.stderr:
            raise PermissionError("Permission denied")

        return True
    except PermissionError:
        return False
    except Exception as e:
        log.info(e)
        return False


def has_docker_spec(directory):
    return os.path.isfile(os.path.join(directory, "docker-compose.yml"))


def container_is_running(
    client: docker.DockerClient,
    service_name: str = None,
    container_name: str = None,
):
    contianer_names = [container.name for container in client.containers.list()]

    if container_name is not None:
        log.debug(
            f"\t\t🐳 container_name is specified - {container_name} - which is a reliable variable"
        )
        return container_name in contianer_names

    if service_name is None:
        raise Exception("You must specify either service_name or container_name")

    log.debug(
        "container_name not set. this means we will need to do some guesswork to see if the service is running"
    )

    for name in contianer_names:
        log.debug(f"\t\t🐳 comparing {service_name} - {name}")

        parts = name.split("-")

        if len(parts) > 1:
            for part in parts:
                if service_name == part:
                    log.debug(f"\t\t🐳 {service_name} is found to be running!")
                    return True

    return False


def read_docker_compose_file(directory):
    # Define the path to the docker-compose.yml file
    docker_compose_file = f"{directory}/docker-compose.yml"

    # Open and read the docker-compose.yml file
    with open(docker_compose_file, "r") as file:
        docker_compose = yaml.safe_load(file)

    return docker_compose


def manage_docker_deploy(
    directory: str,
    did_update: bool,
    force_restart=False,
    force_rebuild=False,
    deploy_all=False,
):
    if not system_has_docker():
        log.warn("\t🚨 Docker not available, skipping")
        return

    if not has_docker_spec(directory):
        log.warn("\t🚨 No docker-compose.yml, skipping")
        return

    if not can_execute_docker_compose():
        log.warn("\t🚨 Docker needs sudo, this script won't work")
        return

    # We need to check if the services described in the docker-compose.yml
    # are running, and if they aren't running, we need to skip starting them
    # by default. Only if the user has specified deploy-all do we start them
    client = docker.from_env()
    config = read_docker_compose_file(directory)
    any_services_running = False

    for service in config["services"]:
        log.debug(f"\t🐳 Checking service {service}...")

        # if container_name is set, use that, otherwise use the service name
        if "container_name" in config["services"][service]:
            service = config["services"][service]["container_name"]
            log.debug(
                f"container_name is set in this service, so we use that ({service})"
            )

        if container_is_running(client, service):
            any_services_running = True
            break

    if not any_services_running and not deploy_all:
        log.info("\t🐳 No services running already running, and deploy_all is not set")
        return

    if not any_services_running and deploy_all:
        log.info("\t🐳 No services running, but deploy_all is set, so we will deploy")

        force_rebuild = True
        force_restart = True

    if did_update or force_rebuild:
        log.info(f"\t🐳 Rebuilding docker images for {directory}...")
        subprocess.run(
            [*which_docker_compose(), "build"],
            cwd=directory,
        )

    if did_update or force_restart:
        log.info("\t🐳 Stopping docker services...")
        subprocess.run(
            [*which_docker_compose(), "down"],
            cwd=directory,
        )

        log.info(f"\t🐳 Re-running docker compose for {directory}...")
        subprocess.run(
            [*which_docker_compose(), "up", "-d"],
            cwd=directory,
        )
    else:
        log.info(f"\t🐳 No repo state change, docker left untouched")
