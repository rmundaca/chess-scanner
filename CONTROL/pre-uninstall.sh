#!/bin/sh
PKG="chess-scanner"
APKG_PATH="/usr/local/AppCentral/$PKG"

if [ -f "$APKG_PATH/CONTROL/start-stop.sh" ]; then
    "$APKG_PATH/CONTROL/start-stop.sh" stop
fi

# Back up the database and images before ADM deletes the directory. With WAL, data may live
# in app.db-wal: all three files are copied together (the app also checkpoints on shutdown).
if [ -f "$APKG_PATH/data/app.db" ]; then
    BACKUP_DIR="/volume1/home/$PKG-backup/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    for f in app.db app.db-wal app.db-shm; do
        [ -f "$APKG_PATH/data/$f" ] && cp "$APKG_PATH/data/$f" "$BACKUP_DIR/$f"
    done
    [ -d "$APKG_PATH/data/scans" ] && cp -a "$APKG_PATH/data/scans" "$BACKUP_DIR/"
    echo "Data backed up to $BACKUP_DIR"
fi

exit 0
