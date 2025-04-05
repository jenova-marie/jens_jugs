#!/bin/bash

# Usage: ./make-archive.sh archive-name.tar.gz '*.md' '*.ts' ...

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <archive-name.tar.gz> <glob1> [<glob2> ...]"
  exit 1
fi

ARCHIVE_NAME="$1"
shift

# Create destination folder if needed
DEST_DIR=$(dirname "$ARCHIVE_NAME")
mkdir -p "$DEST_DIR"

# Create the archive silently from matched git-tracked files
git ls-files "$@" -z | xargs -0 tar -czf "$ARCHIVE_NAME"
