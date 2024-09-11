#!/bin/bash

TARGET_DIR="/home/medico_eafit/WORKSPACES/sebastian_carmona/data"
OWNER="medico_eafit"

change_owner_and_permissions() {
    local dir="$1"

    if [[ -d "$dir" ]]; then
        # Change owner to medico_eafit recursively
        sudo chown -R "$OWNER":"$OWNER" "$dir"
        # Add all permissions (read, write, execute) for owner, group, and others recursively
        sudo chmod -R 777 "$dir"
    else
        printf "Directory %s does not exist.\n" "$dir" >&2
        return 1
    fi
}

main() {
    if [[ -z "$TARGET_DIR" ]]; then
        printf "Usage: %s <target_directory>\n" "$0" >&2
        exit 1
    fi
    
    change_owner_and_permissions "$TARGET_DIR"
}

main "$@"
