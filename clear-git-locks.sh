#!/bin/bash
# This mount blocks unlink, so git's own lock/tmp cleanup fails and leaves
# stale *.lock / tmp_obj_* files behind that block the NEXT git command.
# Run this before any git command in this repo if it errors with
# "Unable to create '.../.lock': File exists" or "cannot lock ref".
set -e
DEBRIS_DIR="$HOME/mnt/side_hustle/_to_delete/07_blogtoolstack_debris"
mkdir -p "$DEBRIS_DIR"
find .git -maxdepth 4 \( -name "*.lock" -o -name "tmp_obj_*" \) 2>/dev/null | while read -r f; do
  mv "$f" "$DEBRIS_DIR/$(basename "$f").$(date +%s%N)" 2>/dev/null || true
done
echo "cleared stale git lock/tmp files (if any)"
