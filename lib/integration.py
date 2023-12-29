import os
from .logger import log
from .git import is_valid_repo, update_git
from .docker import can_execute_docker_compose, manage_docker_deploy, system_has_docker


def process_dir(
    directory: str,
    skip_deploy: bool = False,
    skip_pull: bool = False,
    **kwargs,
):
    log.debug(f"processing {directory}...")

    try:
        did_update = update_git(
            directory,
            skip_pull,
        )

        if did_update:
            log.debug(f"{directory} did_update and pull changes")

        if not skip_deploy:
            log.debug(f"{directory} did update and user did not set skip-deploy")
            manage_docker_deploy(directory, did_update, **kwargs)

    except Exception as e:
        log.error(f"\t🚨 Error updating {directory}: {e}")


def update_git_and_docker(
    directory: str = os.getcwd(),
    recurse=False,
    **kwargs,
):
    if not kwargs.get("skip_deploy", False):
        if not system_has_docker():
            log.error("🚨 Docker not available")
            exit(1)

        if not can_execute_docker_compose():
            log.error("🚨 Docker needs sudo, this script won't work")
            log.error("https://docs.docker.com/engine/install/linux-postinstall/")
            exit(1)

    # Iterate over all items in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        log.debug(f"📁 inspecting {item_path}")

        # If the item is a directory and a Git repository
        if is_valid_repo(item_path):
            log.debug(f"📁 {item_path} is a valid repo")
            # Valid repo, so we can enter the processing immediately
            process_dir(item_path, **kwargs)
        else:
            log.debug(f"{item_path} is a not a valid repo")

            if os.path.isdir(item_path) and recurse:
                log.info(f"📁 {item_path} is a directory, trying recurse")
                # Recurse into the directory
                update_git_and_docker(
                    directory=item_path,
                    recurse=recurse,
                    **kwargs,
                )
