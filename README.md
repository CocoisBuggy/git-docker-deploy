# Git Auto-Update and Docker Deploy Tool


<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Git Auto-Update and Docker Deploy Tool](#git-auto-update-and-docker-deploy-tool)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Usage](#usage)
    - [Basic Command](#basic-command)
    - [Advanced Usage](#advanced-usage)
  - [License](#license)

<!-- /code_chunk_output -->


This Python CLI tool automates the process of updating Git repositories and deploying changes using Docker. It checks for updates in specified Git repositories, pulls changes, and re-runs Docker Compose to keep your deployments up-to-date.

If the script detects that the repo has changed, it will also rebuild with `docker compose build` and redeploy with `docker compose up -d`.

## Features

- **Git Repository Update**: Automatically pulls changes from Git repositories.
- **Docker Deployment**: Rebuilds and reruns Docker Compose for updated repositories.
- **Directory Recursion**: Option to recursively update all Git repositories in a directory.
- **Skip Options**: Flexibility to skip Git pull or Docker deployment steps.


## Requirements

- Python 3.10
- GitPython (`pip install GitPython`)
- Docker and Docker Compose installed on the system.

## Setup

1. **Clone the Repository**

Clone this repository to your local machine using:

```bash
git clone https://github.com/CocoisBuggy/git-docker-deploy.git
```


2. **Install Dependencies**

Install the required Python package, GitPython:

```bash
pip install GitPython
```

3. (Optional) **Add to PATH**

If you'd like the script to be available for execution in your terminal environment, you can add it to your PATH

add it to your system's PATH. Here's how you can do it:

1. Move the script to a directory that's already in your PATH. A common choice is `/usr/local/bin` or `~/bin`. You can do this with the `mv` command. For example, if your script is named `myscript.py`, you can use the following command:

```bash
cp main.py /usr/local/bin/quick-deploy
```

2. Make the script executable. You can do this with the `chmod` command. For example:

```bash
chmod +x /usr/local/bin/quick-deploy
```

now you can call the script from anywhere in your terminal environment with:

```bash
quick-deploy
```

## Usage

The tool is used via the command line. Navigate to the directory where the script is located and run it with the following arguments:

- `-d`, `--directory`: Specify the directory containing the Git repositories to update.
- `--skip-deploy`: Skip Docker deployment steps.
- `--skip-pull`: Skip pulling new changes from Git.
- `--recurse`, `-r`: Recursively update all Git repositories in the specified directory.

### Basic Command

```bash
python update_git_and_docker.py -d /path/to/directory
```


This will update all Git repositories in `/path/to/directory`, pull the latest changes, and redeploy using Docker Compose.

### Advanced Usage

- **Skip Docker Deployment**:

```bash
python update_git_and_docker.py -d /path/to/directory --skip-deploy
```

- **Skip Git Pull**:

```bash
python update_git_and_docker.py -d /path/to/directory --skip-pull
```

- **Recurse Into Subdirectories**:

```bash
python main.py -d /path/to/directory --recurse
```


## License

This project is licensed under the MIT License

---

*Note: Docker needs to be set up such that sudo is not required for it to run.*
