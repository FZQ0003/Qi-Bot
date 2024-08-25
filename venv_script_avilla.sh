#!/bin/bash
# Author: F_Qilin
# Version: 1.0.0
# Note: This is an example to show how to write the script for venv.sh.

# You can source venv.sh or check envs here to make this script independent.
# Note: Dry run mode and ENV_SCRIPT checking must be set.
# shellcheck disable=SC2034
if [ -z "$ENV_SCRIPT" ]; then
  . venv.sh --auto --dry-run
  # Unset FLAG_DRYRUN and init venv
  FLAG_DRYRUN=
  venv_init
fi

# New venv_update
# Note: You can use functions defined in venv.sh. Use "run" function is recommended.

VAR_ROOT=$PWD
VAR_LOCAL_REPO=$ENV_NAME/share/Avilla
if [ -d "$VAR_LOCAL_REPO" ]; then
  run cd "$VAR_LOCAL_REPO" || exit 1
  run git pull
  run cd "$VAR_ROOT" || exit 1
else
  run mkdir -p "$(dirname "$VAR_LOCAL_REPO")"
  run git clone "${ENV_REPOS[0]}" "$VAR_LOCAL_REPO"
fi

run "$VAR_PYTHON" -m pip install "$VAR_LOCAL_REPO" --force-reinstall
run "$VAR_PYTHON" -m pip install "graia-scheduler" --upgrade
# Use pdm
#pdm install

# Fix graia/ryanvk not installed
VAR_SITE=$(find "$ENV_NAME" -regex '.*/site-packages$' 2>/dev/null | head -n +1)
if [ ! -e "$VAR_SITE/graia/ryanvk" ]; then
  run ln -sr "$VAR_LOCAL_REPO/graia/ryanvk" "$VAR_SITE/graia/ryanvk"
fi
