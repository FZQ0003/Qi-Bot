#!/bin/bash
# Author: F_Qilin
# Version: 1.2-ariadne
# Note: See show_help().

# Envs: ENV_NAME, ENV_DISPLAY, ENV_REQ, ENV_REPOS
# Args: ARG_GLOBAL, ARG_CLEAR
# Flags: FLAG_NEW, FLAG_REMOVE, FLAG_UPDATE, FLAG_EXIST, FLAG_GIT
# Vars: PY_DIR

### Functions

# Help
show_help() {
  echo "Usage: $0 [OPTIONS]"
  echo "Legacy virtual Python environment manager for Qi-Bot."
  echo
  echo "Options:"
  echo "  -n, --new           Create or reinstall a new virtual environment."
  echo "      --local         Do not add global site packages."
  echo "      --requirement   Use requirements.txt instead of ENV_REQ."
  echo "      --name name     Directory name instead of ENV_NAME."
  echo "      --display name  Display name for prompt instead of ENV_DISPLAY."
  echo "  -r, --remove        Remove and delete current environment."
  echo "  -u, --update        Update packages of the current environment."
  echo "  -h, --help          Show this help and exit."
  echo "  -v, --version       Show the version and exit."
  echo
  echo "Options for development:"
  echo "      --use-git       Install core packages from git instead of pypi."
  echo "                      You will need to manually install other packages."
  echo
  echo "Environment variables:"
  echo "  ENV_NAME            Directory name (default: $ENV_NAME)."
  echo "  ENV_DISPLAY         Display name for prompt (default: $ENV_DISPLAY)."
  echo "  ENV_REQ             Initial packages (default: $ENV_REQ)."
  echo "  ENV_REPOS           Git repositories of core packages (shell array)."
  echo "                      eg. ('repo1.git' 'repo2.git' ...)"
  echo
  echo "This script uses \"python -m venv\" bundled with python3.3+."
  echo "On some Debian-based systems, python3-venv is needed to install."
  echo "If you use python2 as python, consider run \"alias python=python3\"."
  echo "On Windows, you can use Git Bash to run this script."
  echo "Other systems (eg. MacOS) are not tested, use at your own risk."
  exit
}

# Version
show_version() {
  echo "Script version: 1.2-ariadne."
  echo "Written by F_Qilin."
  exit
}

# Find python and update PY_DIR
find_python() {
  PY_DIR=$(find "$ENV_NAME" -regex '.*/python\(\.exe\)+$' 2>/dev/null | head -n +1)
}

# Install
# shellcheck disable=SC2086
venv_init() {
  # virtualenv: --activators bash --prompt "($ENV_DISPLAY) "
  python -m venv "$ENV_NAME" $ARG_CLEAR $ARG_GLOBAL --prompt "$ENV_DISPLAY"
  find_python
}

# Update
# shellcheck disable=SC2086
venv_update() {
  # PY_DIR always has value, no need to check
  if [ $FLAG_GIT ]; then
    for repo in "${ENV_REPOS[@]}"; do
      # "--force-reinstall" can also reinstall pypi packages.
      "$PY_DIR" -m pip install "git+$repo" --force-reinstall
    done
  else
    "$PY_DIR" -m pip install $ENV_REQ --upgrade
  fi
}

# Remove
venv_remove() {
  rm -rf "$ENV_NAME"
}

# Abort message
abort() {
  echo "[INFO] Abort."
  exit
}

### Prepare

# Environment
if [ -z "$ENV_NAME" ]; then
  ENV_NAME="venv"
fi
if [ -z "$ENV_DISPLAY" ]; then
  ENV_DISPLAY="bot"
fi
if [ -z "$ENV_REQ" ]; then
  ENV_REQ="graia-ariadne[graia] arclet-alconna arclet-alconna-graia"
fi
if [ -z "$ENV_REPOS" ]; then
  ENV_REPOS=(
    "https://github.com/GraiaProject/Ariadne.git"
    "https://github.com/GraiaProject/Scheduler.git"
    "https://github.com/GraiaProject/Saya.git"
    "https://github.com/ArcletProject/Alconna.git"
    "https://github.com/ArcletProject/Alconna-Graia.git"
  )
fi

# Parse args
# Note: Flags are parsed as strings,
#       so 0 or others -> true, empty or not set -> false.
ARG_GLOBAL="--system-site-packages"
while [ -n "$1" ]; do
  case $1 in
  "--new" | "-n")
    FLAG_NEW=0
    ;;
  "--remove" | "-r")
    FLAG_REMOVE=0
    #rm -rf "$ENV_NAME/"
    ;;
  "--update" | "-u")
    FLAG_UPDATE=0
    ;;
  "--use-git")
    FLAG_GIT=0
    ;;
  "--local")
    ARG_GLOBAL=
    ;;
  "--requirement")
    ENV_REQ="-r requirements.txt"
    ;;
  "--name")
    # If you are trying to input invalid name, I will f***u.
    if [ -n "$2" ]; then
      ENV_NAME="$2"
      shift
    else
      echo "[Warning] Invalid name."
    fi
    ;;
  "--display")
    if [ -n "$2" ]; then
      ENV_DISPLAY="$2"
      shift
    else
      echo "[Warning] Invalid display name."
    fi
    ;;
  "--help" | "-h")
    show_help
    ;;
  "--version" | "-v")
    show_version
    ;;
  *)
    echo "[WARNING] Invalid argument: $1."
    ;;
  esac
  shift
done

### Main

# Check venv
if ! python -m venv -h >/dev/null; then
  echo "[ERROR] python venv not found. Did you install python?"
  exit 1
fi

# Check if the environment exists
find_python
if [ "$PY_DIR" ]; then
  FLAG_EXIST=0
fi

# Operations (new > remove > update)
if [ $FLAG_NEW ]; then
  if [ $FLAG_EXIST ]; then
    echo "[INFO] Environment \"$ENV_NAME\" exists. Continue?"
    read -rp "       [y]yes, [N]No, [r]reinstall: " REPLY
    case $REPLY in
    y | Y) ;;
    r | R)
      ARG_CLEAR="--clear"
      ;;
    *)
      abort
      ;;
    esac
  fi
  venv_init
  venv_update
elif [ $FLAG_REMOVE ]; then
  echo "[WARNING] Will delete directory: \"$ENV_NAME\". Continue?"
  read -rp "          [Y]Yes, [n]no: " REPLY
  case $REPLY in
  n | N)
    abort
    ;;
  esac
  venv_remove
elif [ $FLAG_UPDATE ]; then
  if [ ! $FLAG_EXIST ]; then
    echo "[INFO] Environment not found. Installing..."
    venv_init
  fi
  venv_update
else
  echo "[ERROR] Unknown operation. Use \"$0 -h\" for help."
  exit 1
fi
