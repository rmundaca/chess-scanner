#!/bin/sh
# Requires Python >= 3.10. On the AS-202TE, ADM ships Python 3.7: Entware (App Central) is needed.
PKG="chess-scanner"
APKG_PATH="/usr/local/AppCentral/$PKG"
UPGRADE_DIR="/volume1/.$PKG-upgrade"

export PATH="/opt/bin:/opt/sbin:$PATH"

HAS_MODERN_PY=0
if command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 -c 'import sys; print(sys.version_info.major * 100 + sys.version_info.minor)' 2>/dev/null)
    if [ -n "$PY_VER" ] && [ "$PY_VER" -ge 310 ]; then
        HAS_MODERN_PY=1
    fi
fi

if [ "$HAS_MODERN_PY" -eq 0 ] && [ ! -x "/opt/bin/opkg" ] && [ ! -x "/opt/bin/python3" ]; then
    echo "=================================================================="
    echo "ERROR: this app requires Python 3.10 or later."
    echo "Install 'Entware' from App Central and try again."
    echo "=================================================================="
    exit 1
fi

# Upgrade: ADM deletes the app folder (including data/). It is copied aside and post-install restores it.
if [ -d "$APKG_PATH/data" ]; then
    if [ -x "$APKG_PATH/CONTROL/start-stop.sh" ]; then
        "$APKG_PATH/CONTROL/start-stop.sh" stop
    fi
    rm -rf "$UPGRADE_DIR"
    mkdir -p "$UPGRADE_DIR"
    cp -a "$APKG_PATH/data" "$UPGRADE_DIR/" || exit 1
fi

exit 0
