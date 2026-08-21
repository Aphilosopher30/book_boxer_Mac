#!/bin/bash

# Usage: ./delete_files.sh [-y] <folder_path>

SKIP_CONFIRM=false

# Parse optional flags
while getopts "y" opt; do
  case "$opt" in
    y) SKIP_CONFIRM=true ;;
    *) echo "Usage: \$0 [-y] <folder_path>"; exit 1 ;;
  esac
done

# Shift past the parsed options so \$1 now points to <folder_path>
shift $((OPTIND - 1))

FOLDER="${1:-.}"

# Validate argument
if [ ! -d "$FOLDER" ]; then
  echo "Error: '$FOLDER' is not a valid directory."
  exit 1
fi

# Confirm before deleting (unless -y was passed)
if [ "$SKIP_CONFIRM" = false ]; then
  echo "This will delete all files in: $(realpath "$FOLDER")"
  read -rp "Are you sure? (y/N): " CONFIRM

  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
fi

find "$FOLDER" -maxdepth 1 -type f -delete
echo "All files deleted from '$FOLDER'."

# #!/bin/bash
#
# # Usage: ./delete_files.sh <folder_path>
#
# FOLDER="${1:-.}"
#
# # Validate argument
# if [ ! -d "$FOLDER" ]; then
#   echo "Error: '$FOLDER' is not a valid directory."
#   exit 1
# fi
#
# # Confirm before deleting
# echo "This will delete all files in: $(realpath "$FOLDER")"
# read -rp "Are you sure? (y/N): " CONFIRM
#
# if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
#   find "$FOLDER" -maxdepth 1 -type f -delete
#   echo "All files deleted from '$FOLDER'."
# else
#   echo "Aborted."
# fi
