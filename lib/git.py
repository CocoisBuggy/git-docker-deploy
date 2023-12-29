import os
from git import Repo
from .logger import log


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

    log.info(f"🌳 {directory} on branch ({repo.active_branch.name})")
    log.info(f"\t📝 local commit: {local_commit_msg}")

    if repo.is_dirty():
        log.info("\t🧹 repo is dirty, which may affect the pull")

    remote_commits = get_remote_commits(repo)

    if len(remote_commits) == 0:
        log.info("\t🚏 no remote commits to pull, up to date!")

    for commit in remote_commits:
        incomming_message = commit.message.strip().split("\n")[0]
        log.info(f"\t\t🚛 incoming commit: {incomming_message}")

    if not skip_pull and len(remote_commits) > 0:
        repo.remotes.origin.pull()
        log.info("\t🎉 Git pull completed!")
        return True

    log.info("\t🦘 Git repo had no state change!")
    return False


def is_valid_repo(directory):
    try:
        return os.path.isdir(directory) and Repo(directory).git_dir
    except Exception:
        return False

