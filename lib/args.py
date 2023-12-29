import argparse


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
    help="skip pulling new changes from git, will still logger.info out commits that should be pulled",
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
    help="Restart the compose services even if there are no new commits, but will not force deploy",
)

parser.add_argument(
    "--verbose",
    action="store_true",
    help="Whether or not to logger.info out verbose logging information",
)
