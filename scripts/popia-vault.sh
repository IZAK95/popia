#!/usr/bin/env bash
# Keep the POPIA app's data in an encrypted LUKS container on Ubuntu – an
# alternative to full-disk encryption when reinstalling isn't practical.
#
#   scripts/popia-vault.sh create [size]   one-time: make the encrypted vault (default 2G)
#   scripts/popia-vault.sh unlock          after each reboot: unlock the vault and start the app
#   scripts/popia-vault.sh lock            stop the app and lock the vault
#   scripts/popia-vault.sh status          show whether the vault is unlocked and the app running
#   scripts/popia-vault.sh copy-backups <folder>
#                                          copy backups to another (encrypted!) drive, e.g. a LUKS USB stick
#
# Settings (optional, as environment variables):
#   VAULT_IMG   the encrypted container file   (default: ~/popia-vault.img)
#   VAULT_MOUNT where it is opened             (default: /srv/popia-vault)
set -euo pipefail

VAULT_IMG="${VAULT_IMG:-$HOME/popia-vault.img}"
VAULT_MOUNT="${VAULT_MOUNT:-/srv/popia-vault}"
MAPPER="popia-vault"
APP_UID=1000   # the user the app runs as inside the container (see Dockerfile)
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE=(docker compose --project-directory "$REPO_DIR" -f "$REPO_DIR/docker-compose.local.yml")

say() { printf '\033[1m%s\033[0m\n' "$*"; }
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

is_open() { [ -e "/dev/mapper/$MAPPER" ]; }
is_mounted() { mountpoint -q "$VAULT_MOUNT"; }

need_tools() {
  command -v cryptsetup >/dev/null || die "cryptsetup is not installed. Run: sudo apt install cryptsetup"
  command -v docker >/dev/null || die "Docker is not installed."
}

set_env() {  # set_env KEY VALUE – add or replace a line in .env
  local file="$REPO_DIR/.env"
  [ -f "$file" ] || die ".env not found. Run: cp .env.example .env  and fill it in first."
  if grep -q "^$1=" "$file"; then
    sed -i "s|^$1=.*|$1=$2|" "$file"
  else
    printf '%s=%s\n' "$1" "$2" >> "$file"
  fi
}

open_and_mount() {
  [ -f "$VAULT_IMG" ] || die "No vault at $VAULT_IMG. Run: scripts/popia-vault.sh create"
  if ! is_open; then
    say "Unlocking $VAULT_IMG (enter the vault passphrase)"
    sudo cryptsetup open "$VAULT_IMG" "$MAPPER"
  fi
  if ! is_mounted; then
    sudo mkdir -p "$VAULT_MOUNT"
    sudo mount "/dev/mapper/$MAPPER" "$VAULT_MOUNT"
  fi
}

cmd_create() {
  need_tools
  local size="${1:-2G}"
  [ -e "$VAULT_IMG" ] && die "$VAULT_IMG already exists. Use 'unlock' instead."
  "${COMPOSE[@]}" down 2>/dev/null || true

  say "Creating a $size encrypted vault at $VAULT_IMG"
  echo "Choose a strong passphrase and store it in your password manager."
  echo "If you lose it, the data in the vault cannot be recovered."
  fallocate -l "$size" "$VAULT_IMG"
  chmod 600 "$VAULT_IMG"
  sudo cryptsetup luksFormat --type luks2 "$VAULT_IMG"
  sudo cryptsetup open "$VAULT_IMG" "$MAPPER"
  sudo mkfs.ext4 -q -L popia-vault "/dev/mapper/$MAPPER"
  sudo mkdir -p "$VAULT_MOUNT"
  sudo mount "/dev/mapper/$MAPPER" "$VAULT_MOUNT"
  sudo mkdir -p "$VAULT_MOUNT/data" "$VAULT_MOUNT/backups"
  sudo touch "$VAULT_MOUNT/data/.popia-vault" "$VAULT_MOUNT/backups/.popia-vault"

  if [ -f "$REPO_DIR/data/popia.sqlite3" ]; then
    read -r -p "Move the existing app data from $REPO_DIR/data into the vault? [Y/n] " answer
    if [[ ! "$answer" =~ ^[Nn] ]]; then
      sudo cp -a "$REPO_DIR/data/." "$VAULT_MOUNT/data/"
      [ -d "$REPO_DIR/backups" ] && sudo cp -a "$REPO_DIR/backups/." "$VAULT_MOUNT/backups/"
      rm -rf "${REPO_DIR:?}/data" "${REPO_DIR:?}/backups" 2>/dev/null || sudo rm -rf "${REPO_DIR:?}/data" "${REPO_DIR:?}/backups"
      echo "Moved. (Deleted files may still be recoverable from the unencrypted disk until overwritten.)"
    fi
  fi
  sudo chown -R "$APP_UID:$APP_UID" "$VAULT_MOUNT/data" "$VAULT_MOUNT/backups"

  set_env POPIA_DATA_DIR "$VAULT_MOUNT/data"
  set_env POPIA_BACKUP_DIR "$VAULT_MOUNT/backups"
  set_env REQUIRE_VAULT 1
  say "Vault ready. .env now points the app at it."
  cmd_start
}

cmd_start() {
  say "Starting the app"
  "${COMPOSE[@]}" up -d --build
  say "Open http://localhost:8000  –  when you're done, run: scripts/popia-vault.sh lock"
}

cmd_unlock() {
  need_tools
  open_and_mount
  [ -f "$VAULT_MOUNT/data/.popia-vault" ] || die "Vault mounted but marker missing – is this the right vault?"
  cmd_start
}

cmd_lock() {
  say "Stopping the app"
  "${COMPOSE[@]}" down || true
  if is_mounted; then sync; sudo umount "$VAULT_MOUNT"; fi
  if is_open; then sudo cryptsetup close "$MAPPER"; fi
  say "Vault locked."
}

cmd_status() {
  echo "Vault file:  $VAULT_IMG $( [ -f "$VAULT_IMG" ] && echo '(exists)' || echo '(missing)')"
  echo "Unlocked:    $(is_open && echo yes || echo no)"
  echo "Mounted at:  $(is_mounted && echo "$VAULT_MOUNT" || echo '-')"
  "${COMPOSE[@]}" ps 2>/dev/null || true
}

cmd_copy_backups() {
  local target="${1:-}"
  [ -n "$target" ] || die "Usage: scripts/popia-vault.sh copy-backups /media/$USER/<usb-drive>"
  [ -d "$target" ] || die "$target is not a folder. Is the drive plugged in and unlocked?"
  is_mounted || die "Unlock the vault first."
  mkdir -p "$target/popia-backups"
  sudo cp -u --preserve=timestamps "$VAULT_MOUNT"/backups/popia-*.sqlite3.gz "$target/popia-backups/"
  sudo chown -R "$(id -u):$(id -g)" "$target/popia-backups"
  say "Backups copied to $target/popia-backups"
}

case "${1:-}" in
  create) shift; cmd_create "$@" ;;
  unlock | start) cmd_unlock ;;
  lock | stop) cmd_lock ;;
  status) cmd_status ;;
  copy-backups) shift; cmd_copy_backups "$@" ;;
  *) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
