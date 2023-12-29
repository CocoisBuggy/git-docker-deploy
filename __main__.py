#!/usr/bin/env python3

from lib import args
from lib.integration import update_git_and_docker

if __name__ == "__main__":
    # Run the actual script
    kwargs = vars(args)
    del kwargs["verbose"]  # don't need to pass this in

    update_git_and_docker(**kwargs)
