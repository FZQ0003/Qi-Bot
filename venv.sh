#!/bin/bash
# Author: F_Qilin
# Version: 1.0

### Functions

# Help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Use virtualenv to manage current environment."
    echo
    echo "Options:"
    echo "  -n, --new           Create or reinstall a new virtual environment."
    echo "      --local         Do not add global site packages."
    echo "      --requirement   Use requirements.txt instead of $ENV_REQ."
    echo "      --name name     Directory name (default $ENV_NAME)."
    echo "      --display name  Display name for prompt (default $ENV_DISPLAY)."
    echo "  -r, --remove        Remove and delete current environment."
    echo "  -u, --update        Update packages of the current environment."
    echo "  -h, --help          Show this help and exit."
    echo "  -v, --version       Show the version and exit."
    exit
}

# Version
show_version() {
    echo "Script version: 1.0."
    echo "Written by F_Qilin."
    exit
}

# Install
# shellcheck disable=SC2086
venv_install() {
    virtualenv "$ENV_NAME" $ARG_CLEAR $ARG_GLOBAL --activators bash --prompt "($ENV_DISPLAY) "
    "$ENV_NAME/bin/python" -m pip install $ENV_REQ
}

# Update
# shellcheck disable=SC2086
venv_update() {
    "$ENV_NAME/bin/python" -m pip install $ENV_REQ --upgrade
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
    ENV_NAME="graia-ariadne"
fi
if [ -z "$ENV_DISPLAY" ]; then
    ENV_DISPLAY="bot"
fi
if [ -z "$ENV_REQ" ]; then
    ENV_REQ="graia-ariadne[full]"
fi

# Args
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
                echo "[Warning] Invalid display."
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

# Envs: ENV_NAME, ENV_DISPLAY, ENV_REQ
# Args: ARG_GLOBAL, ARG_CLEAR
# Flags: FLAG_NEW, FLAG_REMOVE, FLAG_UPDATE, FLAG_EXIST

### Main

# Check virtualenv
if ! command -v virtualenv >/dev/null; then
    echo "[ERROR] Virtualenv not found. Please install it."
    exit 1
fi

# Check if the environment exists
if command -v "$ENV_NAME/bin/python" >/dev/null; then
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
    venv_install
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
    if [ $FLAG_EXIST ]; then
        venv_update
    else
        echo "[INFO] Environment not found. Installing..."
        venv_install
    fi
else
    echo "[ERROR] Unknown operation. Use \"$0 -h\" for help."
    exit 1
fi
