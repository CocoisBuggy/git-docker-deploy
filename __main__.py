from lib import args
from lib.integration import update_git_and_docker

if __name__ == '__main__':
    # Run the actual script
    update_git_and_docker(**vars(args))