#!/bin/bash
# Author: F_Qilin
# Version: 1.3.0-avilla
# Note: See show_help().

# Envs: ENV_NAME, ENV_DISPLAY, ENV_REQ, ENV_REPOS, ENV_SCRIPT
# Args: ARG_GLOBAL, ARG_CLEAR
# Flags: FLAG_NEW, FLAG_REMOVE, FLAG_UPDATE, FLAG_GIT, FLAG_DEBUG, FLAG_DRYRUN, FLAG_AUTO
# Vars: VAR_PYTHON

### Functions

# Help
show_help() {
  echo "Usage: $0 [OPTIONS]"
  echo "Legacy virtual Python environment manager for Qi-Bot."
  echo
  echo "Options:"
  echo "  -n, --new           Create or reinstall a new virtual environment."
  echo "  -g, --global        Add global site packages."
  echo "      --requirement   Use requirements.txt instead of ENV_REQ."
  echo "      --name NAME     Directory name instead of ENV_NAME."
  echo "      --display NAME  Display name for prompt instead of ENV_DISPLAY."
  echo "  -r, --remove        Remove and delete current environment."
  echo "  -u, --update        Update packages of the current environment."
  echo "  -h, --help          Show this help and exit."
  echo "  -v, --version       Show the version and exit."
  echo "      --auto          Do not ask user"
  echo
  echo "Options for development:"
  echo "      --debug         Show debug logs."
  echo "      --dry-run       Do not actually run commands and show debug logs."
  echo "      --use-git       Install core packages from git instead of pypi."
  echo "                      You will need to manually install other packages."
  echo "      --script FILE   Install from an external script."
  echo "                      The script will override venv_update()."
  echo
  echo "Environment variables:"
  echo "  ENV_NAME            Directory name (default: $ENV_NAME)."
  echo "  ENV_DISPLAY         Display name for prompt (default: $ENV_DISPLAY)."
  echo "  ENV_REQ             Initial packages (default: $ENV_REQ)."
  echo "  ENV_REPOS           Git repositories of core packages (shell array)."
  echo "                      eg. ('repo1.git' 'repo2.git' ...)"
  echo "  ENV_SCRIPT          External venv_update script path."
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
  echo "Script version: 1.3.0-avilla."
  echo "Written by F_Qilin."
  exit
}

# Echo
echo_info() { echo "[INFO]    $*"; }
echo_warn() { echo "[WARNING] $*"; }
echo_error() { echo "[ERROR]   $*"; }
echo_debug() {
  if [ "$FLAG_DEBUG" ]; then
    if [ -n "$2" ]; then
      local __prefix="$1: "
      shift
    fi
    echo "[DEBUG]   $__prefix$*"
  fi
}
question() {
  if [ "$FLAG_AUTO" ]; then
    echo "          $1: $3 [AUTO]"
    eval "$2=$3"
  else
    read -rp "          $1: " "$2"
  fi
}

# Set flag
flag() {
  eval "$1=1"
  echo_debug flag "set $1"
}

# Run
run() {
  if [ "$FLAG_DRYRUN" ]; then
    echo_debug run "$*"
  else
    # shellcheck disable=SC2048
    $*
  fi
}

# Find python and update VAR_PYTHON
find_python() {
  VAR_PYTHON=$(find "$ENV_NAME" -regex '.*/python\(\.exe\)?$' 2>/dev/null | head -n +1)
  echo_debug find_python "VAR_PYTHON=$VAR_PYTHON"
}

# Install
venv_init() {
  echo_debug venv_init "python -m venv \"$ENV_NAME\" $ARG_CLEAR $ARG_GLOBAL --prompt \"$ENV_DISPLAY\""
  # virtualenv: --activators bash --prompt "($ENV_DISPLAY) "
  # shellcheck disable=SC2086
  run python -m venv "$ENV_NAME" $ARG_CLEAR $ARG_GLOBAL --prompt "$ENV_DISPLAY"
  if [ "$FLAG_DRYRUN" ]; then
    VAR_PYTHON="$ENV_NAME/bin/python"
    echo_debug venv_init "VAR_PYTHON=$VAR_PYTHON"
  else
    find_python
  fi
}

# Update
venv_update() {
  # VAR_PYTHON always has value, no need to check
  if [ -n "$ENV_SCRIPT" ]; then
    # shellcheck disable=SC1090
    . "$ENV_SCRIPT"
  elif [ "$FLAG_GIT" ]; then
    for repo in "${ENV_REPOS[@]}"; do
      echo_debug venv_update "\"$VAR_PYTHON\" -m pip install \"git+$repo\" --force-reinstall"
      # "--force-reinstall" can also reinstall pypi packages.
      run "$VAR_PYTHON" -m pip install "git+$repo" --force-reinstall
    done
  else
    echo_debug venv_update "\"$VAR_PYTHON\" -m pip install $ENV_REQ --upgrade"
    # shellcheck disable=SC2086
    run "$VAR_PYTHON" -m pip install $ENV_REQ --upgrade
  fi
}

# Remove
venv_remove() {
  echo_debug venv_remove "rm -rf \"$ENV_NAME\""
  run rm -rf "$ENV_NAME"
}

# Abort message
abort() {
  echo_info "Abort."
  exit
}

### Prepare

# Environment
if [ -z "$ENV_NAME" ]; then
  ENV_NAME=".venv"
fi
if [ -z "$ENV_DISPLAY" ]; then
  ENV_DISPLAY="bot"
fi
if [ -z "$ENV_REQ" ]; then
  ENV_REQ="avilla-onebot-v11 avilla-standard-qq graia-saya graia-scheduler"
fi
if [ -z "$ENV_REPOS" ]; then
  ENV_REPOS=(
    "https://github.com/GraiaProject/Avilla.git"
    "https://github.com/GraiaProject/Scheduler.git"
  )
fi
#if [ -z "$ENV_SCRIPT" ]; then
#  ENV_SCRIPT="venv_script_avilla.sh"
#fi

# Parse args
# Note: Flags are parsed as strings,
#       so 0 or others -> true, empty or not set -> false.
if [[ "$*" =~ (--debug|--dry-run) ]]; then
  flag FLAG_DEBUG
fi
while [ -n "$1" ]; do
  case $1 in
  "--new" | "-n")
    flag FLAG_NEW
    ;;
  "--remove" | "-r")
    flag FLAG_REMOVE
    #rm -rf "$ENV_NAME/"
    ;;
  "--update" | "-u")
    flag FLAG_UPDATE
    ;;
  "--auto")
    flag FLAG_AUTO
    ;;
  "--use-git")
    flag FLAG_GIT
    ;;
  "--dry-run")
    flag FLAG_DRYRUN
    ;;
  "--debug")
    ;;
  "--script")
    if [ -f "$2" ]; then
      ENV_SCRIPT=$2
      shift
    else
      echo_warn "Invalid script path."
    fi
    ;;
  "--global" | "-g")
    ARG_GLOBAL="--system-site-packages"
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
      echo_warn "Invalid name."
    fi
    ;;
  "--display")
    if [ -n "$2" ]; then
      ENV_DISPLAY="$2"
      shift
    else
      echo_warn "Invalid display name."
    fi
    ;;
  "--help" | "-h")
    show_help
    ;;
  "--version" | "-v")
    show_version
    ;;
  *)
    echo_warn "Invalid argument: $1."
    ;;
  esac
  shift
done

echo_debug env "ENV_NAME=$ENV_NAME"
echo_debug env "ENV_DISPLAY=$ENV_DISPLAY"
echo_debug env "ENV_REQ=$ENV_REQ"
echo_debug env "ENV_REPOS=(${ENV_REPOS[*]})"
echo_debug env "ENV_SCRIPT=$ENV_SCRIPT"

### Main

# Check venv
if ! python -m venv -h >/dev/null; then
  echo_error "Python venv not found. Did you install python?"
  exit 1
fi

# Check if the environment exists
find_python
if [ -z "$VAR_PYTHON" ] && [ "$FLAG_DRYRUN" ]; then
  echo_debug dry_run "VAR_PYTHON is empty. You can set it manually or keep it empty."
  question "Set VAR_PYTHON" VAR_PYTHON "$ENV_NAME/bin/python"
fi

# Operations (new > remove > update)
if [ "$FLAG_NEW" ]; then
  if [ -n "$VAR_PYTHON" ]; then
    echo_info "Environment \"$ENV_NAME\" exists. Continue?"
    question "[y]yes, [N]No, [r]reinstall" REPLY
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
elif [ "$FLAG_REMOVE" ]; then
  echo_warn "Will delete directory: \"$ENV_NAME\". Continue?"
  question "[Y]Yes, [n]no" REPLY
  case $REPLY in
  n | N)
    abort
    ;;
  esac
  venv_remove
elif [ "$FLAG_UPDATE" ]; then
  if [ -z "$VAR_PYTHON" ]; then
    echo_info "Environment not found. Installing..."
    venv_init
  fi
  venv_update
elif [ "$FLAG_DRYRUN" ]; then
  echo_warn "Unknown operation. In dry run mode, the script does not exit."
else
  echo_error "Unknown operation. Use \"$0 -h\" for help."
  exit 1
fi
