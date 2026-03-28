#!/usr/bin/env sh
# wezterm-tui installer
# Usage: curl -sS https://raw.githubusercontent.com/DarkoKuzmanovic/wezterm-tui/master/install.sh | sh
set -eu

REPO="https://github.com/DarkoKuzmanovic/wezterm-tui.git"
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=12
BOLD=''
RESET=''
GREEN=''
RED=''
YELLOW=''

setup_colors() {
    if [ -t 1 ] && command -v tput >/dev/null 2>&1; then
        BOLD=$(tput bold 2>/dev/null || true)
        RESET=$(tput sgr0 2>/dev/null || true)
        GREEN=$(tput setaf 2 2>/dev/null || true)
        RED=$(tput setaf 1 2>/dev/null || true)
        YELLOW=$(tput setaf 3 2>/dev/null || true)
    fi
}

info() {
    printf '%s[info]%s %s\n' "$GREEN" "$RESET" "$1"
}

warn() {
    printf '%s[warn]%s %s\n' "$YELLOW" "$RESET" "$1"
}

error() {
    printf '%s[error]%s %s\n' "$RED" "$RESET" "$1" >&2
}

die() {
    error "$1"
    exit 1
}

check_python() {
    for cmd in python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null) || continue
            major=$(echo "$version" | cut -d. -f1)
            minor=$(echo "$version" | cut -d. -f2)
            if [ "$major" -ge "$MIN_PYTHON_MAJOR" ] && [ "$minor" -ge "$MIN_PYTHON_MINOR" ]; then
                PYTHON_CMD="$cmd"
                PYTHON_VERSION="$version"
                return 0
            fi
        fi
    done
    return 1
}

install_with_uv() {
    info "Installing with uv..."
    uv tool install "wezterm-tui @ git+${REPO}"
}

install_with_pipx() {
    info "Installing with pipx..."
    pipx install "git+${REPO}"
}

install_with_pip() {
    info "Installing with pip..."
    "$PYTHON_CMD" -m pip install --user "git+${REPO}"
}

check_path() {
    if command -v wezterm-tui >/dev/null 2>&1; then
        return 0
    fi

    # Check common install locations
    for dir in "$HOME/.local/bin" "$HOME/.cargo/bin" "$HOME/.local/share/uv/tools"; do
        if [ -x "$dir/wezterm-tui" ]; then
            warn "Installed to $dir which is not in your PATH."
            warn "Add this to your shell profile:"
            echo ""
            echo "  export PATH=\"$dir:\$PATH\""
            echo ""
            return 0
        fi
    done
}

main() {
    setup_colors

    printf '\n  %swezterm-tui installer%s\n\n' "$BOLD" "$RESET"

    # Check Python
    if ! check_python; then
        die "Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ is required but not found. Install it first."
    fi
    info "Found Python ${PYTHON_VERSION} (${PYTHON_CMD})"

    # Pick install method: uv > pipx > pip
    if command -v uv >/dev/null 2>&1; then
        install_with_uv
    elif command -v pipx >/dev/null 2>&1; then
        install_with_pipx
    else
        warn "Neither uv nor pipx found. Falling back to pip --user install."
        warn "Consider installing uv (https://docs.astral.sh/uv/) for better tool management."
        install_with_pip
    fi

    echo ""
    check_path
    info "${GREEN}${BOLD}wezterm-tui${RESET} installed successfully! Run it with:"
    echo ""
    echo "  wezterm-tui"
    echo ""
}

main
