#!/usr/bin/env python3
"""
Quick script that goes through all the files in a directory supplied as
an argument, pulls git changes for it (if that dir is a git repo), and
then re-runs the docker compose to make everything up to date
"""

import os
import subprocess
from git import Repo
import shutil


import argparse
import os
import subprocess
from git import Repo
import docker
import yaml

# Create the parser
parser = argparse.ArgumentParser(description="Update git repos and deploy via docker")

# Add the arguments
parser.add_argument("-d", "--directory", type=str, help="the directory to update")

parser.add_argument(
    "--skip-deploy",
    action="store_true",
    help="skip the steps involving docker deployment",
)

parser.add_argument(
    "--skip-pull",
    action="store_true",
    help="skip pulling new changes from git, will still print out commits that should be pulled",
)

parser.add_argument(
    "--recurse",
    "-r",
    action="store_true",
    help="recurse into the directory and update all git repos in the directory",
)

parser.add_argument(
    "--deploy-all",
    action="store_true",
    help="Deploy all docker compose services, even if they aren't running when the script is started",
)

parser.add_argument(
    "--force-rebuild",
    action="store_true",
    help="Rebuild the docker compose services even if there are no new commits",
)

parser.add_argument(
    "--force-restart",
    action="store_true",
    help="Restart the compose services even if there are no new commits",
)


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


def get_remote_commits(repo: Repo):
    # Fetch the remote commits
    repo.remotes.origin.fetch()

    # Get the commit of the local branch
    local_commit = repo.head.commit

    # Get the commit of the remote branch
    remote_commit = repo.remotes.origin.refs[repo.active_branch.name].commit

    # Get the list of commits that are in the remote branch but not in the local branch
    remote_commits = list(
        repo.iter_commits(f"{local_commit.hexsha}..{remote_commit.hexsha}")
    )

    return remote_commits


def update_git(directory: str, skip_pull: bool):
    repo: Repo = Repo(directory)
    local_commit = repo.head.commit
    local_commit_msg = local_commit.message.strip().split("\n")[0]

    print(f"🌳 {directory} on branch ({repo.active_branch.name})")
    print(f"\t📝 local commit: {local_commit_msg}")

    if repo.is_dirty():
        print("\t🧹 repo is dirty, which may affect the pull")

    remote_commits = get_remote_commits(repo)

    if len(remote_commits) == 0:
        print("\t🚏 no remote commits to pull, up to date!")

    for commit in remote_commits:
        incomming_message = commit.message.strip().split("\n")[0]
        print(f"\t\t🚛 incoming commit: {incomming_message}")

    if not skip_pull and len(remote_commits) > 0:
        repo.remotes.origin.pull()
        print("\t🎉 Git pull completed!")
        return True

    print("\t🦘 Git repo had no state change!")
    return False


def is_valid_repo(directory):
    try:
        return os.path.isdir(directory) and Repo(directory).git_dir
    except Exception:
        return False


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
        print(e)
        return False


def has_docker_spec(directory):
    return os.path.isfile(os.path.join(directory, "docker-compose.yml"))


def service_is_running(client: docker.DockerClient, name: str):
    for service in client.services.list():
        service = client.services.get(service.id)

        if service.name == name:
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
        print("\t🚨 Docker not available, skipping")
        return

    if not has_docker_spec(directory):
        print("\t🚨 No docker-compose.yml, skipping")
        return

    if not can_execute_docker_compose():
        print("\t🚨 Docker needs sudo, this script won't work")
        return

    # We need to check if the services described in the docker-compose.yml
    # are running, and if they aren't running, we need to skip starting them
    # by default. Only if the user has specified deploy-all do we start them
    client = docker.from_env()
    config = read_docker_compose_file(directory)
    any_services_running = False

    for service in config["services"]:
        print(f"\t🐳 Checking service {service}...")
        if service_is_running(client, service):
            any_services_running = True
            break

    if not any_services_running and not deploy_all:
        print("\t🐳 No services running already running, and deploy_all is false")
        return

    if not any_services_running and deploy_all:
        print(
            "\t🐳 No services running, but deploy_all is true, so deploying all services"
        )

        force_rebuild = True
        force_restart = True

    if did_update or force_rebuild:
        print(f"\t🐳 Rebuilding docker images for {directory}...")
        subprocess.run(
            [*which_docker_compose(), "build"],
            cwd=directory,
        )

    if did_update or force_restart:
        print("\t🐳 Stopping docker services...")
        subprocess.run(
            [*which_docker_compose(), "down"],
            cwd=directory,
        )

        print(f"\t🐳 Re-running docker compose for {directory}...")
        subprocess.run(
            [*which_docker_compose(), "up", "-d"],
            cwd=directory,
        )
    else:
        print(f"\t🐳 No repo state change, docker left untouched")


def process_dir(
    directory: str,
    skip_deploy: bool = False,
    skip_pull: bool = False,
    **kwargs,
):
    try:
        did_update = update_git(
            directory,
            skip_pull,
        )

        if not skip_deploy:
            manage_docker_deploy(directory, did_update, **kwargs)

    except Exception as e:
        print(f"\t🚨 Error updating {directory}: {e}")


def update_git_and_docker(
    directory: str = os.getcwd(),
    recurse=False,
    **kwargs,
):
    if not kwargs.get("skip_deploy", False):
        if not system_has_docker():
            print("🚨 Docker not available")
            return

        if not can_execute_docker_compose():
            print("🚨 Docker needs sudo, this script won't work")
            print("https://docs.docker.com/engine/install/linux-postinstall/")
            return

    # Iterate over all items in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # If the item is a directory and a Git repository
        if is_valid_repo(item_path):
            # Valid repo, so we can enter the processing immediately
            process_dir(item_path, **kwargs)
        else:
            if os.path.isdir(item_path) and recurse:
                print(f"📁 {item_path} is a directory, trying recurse")
                # Recurse into the directory
                update_git_and_docker(
                    directory=item_path,
                    recurse=recurse,
                    **kwargs,
                )


# Parse the arguments
args = parser.parse_args()

# Run the actual script
update_git_and_docker(**vars(args))
