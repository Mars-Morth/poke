#!/usr/bin/env bash
# ==============================================================================
# Poke Installer
# Installs Poke CLI & background daemon with systemd and Tailscale
# ==============================================================================

set -euo pipefail
shopt -s extglob

# Configuration & Defaults
PROJECT_REPO="https://github.com/Mars-Morth/poke"
PROJECT_DIR="${HOME}/opt/poke"
LOG_FILE="${TMPDIR:-/tmp}/poke-install.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VERBOSE=0
INSTALL_MODE="git"
SKIP_TAILSCALE=0
PYTHON_BIN=""

BOX_INNER_WIDTH=68

# Step & Error State Tracking
CURRENT_STEP_LABEL=""
CURRENT_STEP_IDX=0
CURRENT_TOTAL_STEPS=0
CURRENT_PCT=0
IN_STEP=0
STEP_FAILED_PRINTED=0
ERROR_BOX_SHOWN=0

# Signal Handling & Cleanup
cleanup() {
  local ec="${1:-$?}"
  trap - INT TERM EXIT

  # Restore cursor visibility if in terminal
  if [ -t 1 ]; then
    printf '\033[?25h'
  fi

  # Terminate background jobs from this script
  local bg_jobs
  bg_jobs=$(jobs -p 2>/dev/null || true)
  if [ -n "$bg_jobs" ]; then
    kill $bg_jobs 2>/dev/null || true
  fi

  # Handle non-zero exit
  if [ "$ec" -ne 0 ]; then
    # Ensure theme is initialized even if error occurred before setup_theme
    if [ -z "${CLR_RED+x}" ] || [ -z "${BOX_TL+x}" ]; then
      setup_theme
    fi

    # If interrupted or failed before step failure was printed, render red progress bar
    if [ -t 1 ] && [ "${IN_STEP:-0}" -eq 1 ] && [ "${STEP_FAILED_PRINTED:-0}" -eq 0 ]; then
      local bar_str
      bar_str="$(render_progress_bar "${CURRENT_PCT:-0}" "$CLR_RED")"
      local step_state="failed"
      if [ "$ec" -eq 130 ]; then
        step_state="interrupted"
      fi
      printf "\r  ${CLR_RED}%s${CLR_RESET} [%d/%d] %s  ${CLR_RED}%s (%s)${CLR_RESET}\033[K\n" \
        "$CHAR_CROSS" "${CURRENT_STEP_IDX:-1}" "${CURRENT_TOTAL_STEPS:-1}" "$bar_str" "${CURRENT_STEP_LABEL:-Failed}" "$step_state"
      STEP_FAILED_PRINTED=1
    elif [ ! -t 1 ] && [ "${IN_STEP:-0}" -eq 1 ] && [ "${STEP_FAILED_PRINTED:-0}" -eq 0 ]; then
      local bar_str
      bar_str="$(render_progress_bar "${CURRENT_PCT:-0}" "$CLR_RED")"
      printf "%s %s (failed)\n" "$bar_str" "$CHAR_CROSS"
      STEP_FAILED_PRINTED=1
    fi

    # Determine appropriate failure message/step name
    local fail_step="${CURRENT_STEP_LABEL:-}"
    if [ -z "$fail_step" ]; then
      if [ "$ec" -eq 130 ]; then
        fail_step="Installation interrupted by user (SIGINT)"
      elif [ "$ec" -eq 143 ]; then
        fail_step="Installation terminated (SIGTERM)"
      elif [ -n "${BASH_COMMAND:-}" ] && [ "${BASH_COMMAND}" != "exit \"$ec\"" ] && [ "${BASH_COMMAND}" != "cleanup" ]; then
        fail_step="Command failed: ${BASH_COMMAND}"
      else
        fail_step="Installation process"
      fi
    elif [ "$ec" -eq 130 ]; then
      fail_step="${fail_step} (interrupted by user)"
    elif [ "$ec" -eq 143 ]; then
      fail_step="${fail_step} (terminated)"
    fi

    if type show_error_box >/dev/null 2>&1; then
      show_error_box "$fail_step" "$ec"
    else
      printf "%s Installation error in: %s (exit code: %d)\n" "${CHAR_CROSS:-[FAIL]}" "$fail_step" "$ec" >&2
    fi
  fi

  exit "$ec"
}

handle_signal() {
  local sig="$1"
  trap - INT TERM EXIT
  case "$sig" in
  INT) cleanup 130 ;;
  TERM) cleanup 143 ;;
  *) cleanup 1 ;;
  esac
}

trap 'handle_signal INT' INT
trap 'handle_signal TERM' TERM
trap cleanup EXIT

# Theme & Visual Styling
setup_theme() {
  # Check color support
  if [ -t 1 ] && [ -z "${NO_COLOR:-}" ] && [ "${TERM:-}" != "dumb" ]; then
    CLR_RESET=$'\033[0m'
    CLR_BOLD=$'\033[1m'
    CLR_DIM=$'\033[2m'
    CLR_RED=$'\033[1;31m'
    CLR_GREEN=$'\033[1;32m'
    CLR_YELLOW=$'\033[1;33m'
    CLR_BLUE=$'\033[1;34m'
    CLR_MAGENTA=$'\033[1;35m'
    CLR_CYAN=$'\033[1;36m'
    CLR_WHITE=$'\033[1;37m'
  else
    CLR_RESET=''
    CLR_BOLD=''
    CLR_DIM=''
    CLR_RED=''
    CLR_GREEN=''
    CLR_YELLOW=''
    CLR_BLUE=''
    CLR_MAGENTA=''
    CLR_CYAN=''
    CLR_WHITE=''
  fi

  # Standard clean text tags (no emojis)
  CHAR_CHECK="[OK]"
  CHAR_CROSS="[FAIL]"
  CHAR_ARROW="->"
  CHAR_BULLET="-"
  CHAR_INFO="[INFO]"
  CHAR_WARN="[WARN]"
  SPINNER=('|' '/' '-' '\')

  # Check Unicode / UTF-8 support for box and progress bar elements
  local charset="${LC_ALL:-${LC_CTYPE:-${LANG:-}}}"
  if [[ "$charset" =~ [Uu][Tt][Ff]-?8 ]]; then
    BAR_FULL="█"
    BAR_EMPTY="░"
    BOX_TL="╭"
    BOX_TR="╮"
    BOX_BL="╰"
    BOX_BR="╯"
    BOX_H="─"
    BOX_V="│"
  else
    BAR_FULL="="
    BAR_EMPTY="-"
    BOX_TL="+"
    BOX_TR="+"
    BOX_BL="+"
    BOX_BR="+"
    BOX_H="-"
    BOX_V="|"
  fi
}
setup_theme

# UI Helpers & Progress Bar
render_progress_bar() {
  local percent="$1"
  local color="${2:-$CLR_GREEN}"
  local bar_width=22
  local num_filled=$(((percent * bar_width) / 100))
  local num_empty=$((bar_width - num_filled))

  local filled=""
  local empty=""
  local i
  for ((i = 0; i < num_filled; i++)); do filled="${filled}${BAR_FULL}"; done
  for ((i = 0; i < num_empty; i++)); do empty="${empty}${BAR_EMPTY}"; done

  if { [ -n "$CLR_RED" ] && [ "$color" = "$CLR_RED" ]; } || [ "$color" = "red" ]; then
    printf "${CLR_RED}[${CLR_RED}%s${CLR_DIM}%s${CLR_RED}]${CLR_RESET} ${CLR_BOLD}${CLR_RED}%3d%%${CLR_RESET}" "$filled" "$empty" "$percent"
  else
    printf "${CLR_CYAN}[${color}%s${CLR_DIM}%s${CLR_CYAN}]${CLR_RESET} ${CLR_BOLD}%3d%%${CLR_RESET}" "$filled" "$empty" "$percent"
  fi
}

# Prints a line inside a box with exact padding and closed right border
print_box_line() {
  local content="$1"
  local border_color="${2:-$CLR_GREEN}"

  # Strip ANSI color escapes to compute visible character length
  local clean="${content//$'\033'\[*([0-9;])m/}"
  local vis_len=${#clean}
  local pad=$((BOX_INNER_WIDTH - vis_len))
  if [ "$pad" -lt 0 ]; then
    pad=0
  fi

  local spaces=""
  local i
  for ((i = 0; i < pad; i++)); do
    spaces="${spaces} "
  done

  printf "${border_color}%s${CLR_RESET} %s%s ${border_color}%s${CLR_RESET}\n" \
    "$BOX_V" "$content" "$spaces" "$BOX_V"
}

print_banner() {
  printf "\n"
  printf "%s\n" "${CLR_RED}   ___       __        ${CLR_RESET}"
  printf "%s\n" "${CLR_RED}  / _ \___  / /_____   ${CLR_BOLD}${CLR_WHITE}POKE INSTALLER${CLR_RESET}"
  printf "%s\n" "${CLR_RED} / ___/ _ \/  '_/ -_)  ${CLR_DIM}Pokemon CLI Battler & Daemon${CLR_RESET}"
  printf "%s\n" "${CLR_RED}/_/   \\___/_/\\_\\\\__/   ${CLR_CYAN}${PROJECT_REPO}${CLR_RESET}"
  printf "%s\n" "${CLR_CYAN}────────────────────────────────────────────────────────────────${CLR_RESET}"
  if [ "$VERBOSE" -eq 1 ]; then
    printf "  ${CLR_DIM}Mode: %s | Verbose: ON | Log: %s${CLR_RESET}\n\n" "$INSTALL_MODE" "$LOG_FILE"
  else
    printf "  ${CLR_DIM}Mode: %s | Verbose: OFF (detailed log: %s)${CLR_RESET}\n\n" "$INSTALL_MODE" "$LOG_FILE"
  fi
}

show_help() {
  cat <<EOF
Poke Installer

Usage:
  ./install.sh [OPTIONS] [local]

Options:
  -v, --verbose         Show full real-time output from all subcommands
  -l, --local, local    Install from local source files instead of git clone
      --skip-tailscale  Skip Tailscale VPN installation and configuration
  -h, --help            Show this help message and exit

Description:
  Installs the Poke daemon and CLI into $PROJECT_DIR, symlinks poke to
  /usr/bin, configures the systemd user service, and connects to the
  Tailscale battle network.
EOF
}

show_error_box() {
  if [ "${ERROR_BOX_SHOWN:-0}" -eq 1 ]; then
    return 0
  fi
  ERROR_BOX_SHOWN=1

  local step_name="$1"
  local error_code="${2:-1}"

  local h_line=""
  local i
  for ((i = 0; i < BOX_INNER_WIDTH + 2; i++)); do
    h_line="${h_line}${BOX_H}"
  done

  printf "\n"
  printf "${CLR_RED}%s%s%s${CLR_RESET}\n" "$BOX_TL" "$h_line" "$BOX_TR"
  print_box_line "${CLR_BOLD}${CLR_RED}${CHAR_CROSS} INSTALLATION ERROR${CLR_RESET}" "$CLR_RED"
  print_box_line "Failed step: ${CLR_BOLD}${step_name}${CLR_RESET} (exit code: ${error_code})" "$CLR_RED"
  if [ "${IN_STEP:-0}" -eq 1 ] || [ "${CURRENT_PCT:-0}" -gt 0 ]; then
    print_box_line "Progress:  $(render_progress_bar "${CURRENT_PCT:-0}" "$CLR_RED")" "$CLR_RED"
  fi
  print_box_line "" "$CLR_RED"

  if [ -f "$LOG_FILE" ] && [ -s "$LOG_FILE" ]; then
    print_box_line "${CLR_DIM}Recent output from log:${CLR_RESET}" "$CLR_RED"
    while IFS= read -r line; do
      local clean_line="${line:0:60}"
      print_box_line "  ${CLR_DIM}${clean_line}${CLR_RESET}" "$CLR_RED"
    done < <(tail -n 8 "$LOG_FILE")
    print_box_line "" "$CLR_RED"
    print_box_line "Log file: ${CLR_CYAN}${LOG_FILE}${CLR_RESET}" "$CLR_RED"
  fi

  print_box_line "Tip: Re-run with ${CLR_CYAN}--verbose${CLR_RESET} to view live subcommand output." "$CLR_RED"
  printf "${CLR_RED}%s%s%s${CLR_RESET}\n" "$BOX_BL" "$h_line" "$BOX_BR"
  printf "\n"
}

show_tailscale_notice() {
  local h_line=""
  local i
  for ((i = 0; i < BOX_INNER_WIDTH + 2; i++)); do
    h_line="${h_line}${BOX_H}"
  done

  printf "\n"
  printf "${CLR_CYAN}%s%s%s${CLR_RESET}\n" "$BOX_TL" "$h_line" "$BOX_TR"
  print_box_line "${CLR_BOLD}${CLR_YELLOW}${CHAR_INFO} Tailscale Credentials Notice${CLR_RESET}" "$CLR_CYAN"
  print_box_line "" "$CLR_CYAN"
  print_box_line "Account: ${CLR_BOLD}${CLR_WHITE}pokepeoplegd@gmail.com${CLR_RESET}" "$CLR_CYAN"
  print_box_line "Please check Microsoft Teams for credentials if prompted." "$CLR_CYAN"
  printf "${CLR_CYAN}%s%s%s${CLR_RESET}\n" "$BOX_BL" "$h_line" "$BOX_BR"
  printf "\n"
}

show_success_card() {
  local install_dir="$1"
  local daemon_status="$2"
  local ts_info="$3"

  local h_line=""
  local i
  for ((i = 0; i < BOX_INNER_WIDTH + 2; i++)); do
    h_line="${h_line}${BOX_H}"
  done

  printf "\n"
  printf "${CLR_GREEN}%s%s%s${CLR_RESET}\n" "$BOX_TL" "$h_line" "$BOX_TR"
  print_box_line "${CLR_BOLD}${CLR_GREEN}${CHAR_CHECK} Poke successfully installed!${CLR_RESET}" "$CLR_GREEN"
  print_box_line "" "$CLR_GREEN"
  print_box_line "Progress:  $(render_progress_bar 100)" "$CLR_GREEN"
  print_box_line "Location:  ${CLR_WHITE}${install_dir}${CLR_RESET}" "$CLR_GREEN"
  print_box_line "CLI:       ${CLR_WHITE}/usr/bin/poke${CLR_RESET}" "$CLR_GREEN"
  print_box_line "Daemon:    ${CLR_GREEN}${daemon_status}${CLR_RESET}" "$CLR_GREEN"
  print_box_line "Tailscale: ${CLR_CYAN}${ts_info}${CLR_RESET}" "$CLR_GREEN"
  print_box_line "" "$CLR_GREEN"
  print_box_line "${CLR_BOLD}Quick Commands:${CLR_RESET}" "$CLR_GREEN"
  print_box_line "  - Daemon status:  ${CLR_WHITE}systemctl --user status poke.service${CLR_RESET}" "$CLR_GREEN"
  print_box_line "  - Daemon logs:    ${CLR_WHITE}journalctl --user -u poke.service -f${CLR_RESET}" "$CLR_GREEN"
  print_box_line "  - Restart daemon: ${CLR_WHITE}systemctl --user restart poke.service${CLR_RESET}" "$CLR_GREEN"
  print_box_line "  - Run Poke CLI:   ${CLR_WHITE}poke${CLR_RESET}" "$CLR_GREEN"
  printf "${CLR_GREEN}%s%s%s${CLR_RESET}\n" "$BOX_BL" "$h_line" "$BOX_BR"
  printf "\n"
}

# Privilege Escalation Helpers
step_requires_sudo() {
  local cmd="${1:-}"
  if [ -z "$cmd" ]; then
    return 1
  fi
  if [ "$cmd" = "sudo" ] || [ "$cmd" = "step_link_to_usr_bin" ] || [ "$cmd" = "step_setup_tailscale" ]; then
    return 0
  fi
  if type "$cmd" 2>/dev/null | grep -qE '\bsudo\b'; then
    return 0
  fi
  return 1
}

ensure_sudo() {
  local reason="${1:-privileged operation}"
  if ! sudo -n true 2>/dev/null; then
    if [ -t 1 ]; then
      printf "\r\033[K"
      printf '\033[?25h'
      printf "  ${CLR_CYAN}%s${CLR_RESET} ${CLR_BOLD}[sudo] Password required for: %s${CLR_RESET}\n" "$CHAR_ARROW" "$reason"
    fi
    local ec=0
    sudo -v || ec=$?
    if [ "$ec" -ne 0 ]; then
      if [ -t 1 ]; then
        printf '\033[?25h'
      fi
      return "$ec"
    fi
    if [ -t 1 ]; then
      printf '\033[?25l'
    fi
  fi
  return 0
}

# Task Runner (Single-Line Progress Bar & Spinner)
execute_step() {
  local step_idx="$1"
  local total_steps="$2"
  local start_pct="$3"
  local end_pct="$4"
  local label="$5"
  shift 5

  CURRENT_STEP_IDX="$step_idx"
  CURRENT_TOTAL_STEPS="$total_steps"
  CURRENT_STEP_LABEL="$label"
  CURRENT_PCT="$start_pct"
  IN_STEP=1
  STEP_FAILED_PRINTED=0

  # Verbose mode: Stream full output directly
  if [ "$VERBOSE" -eq 1 ]; then
    printf "\n${CLR_BOLD}${CLR_CYAN}==> [%d/%d] %s${CLR_RESET} %s\n" \
      "$step_idx" "$total_steps" "$label" "$(render_progress_bar "$end_pct")"
    if "$@"; then
      printf "${CLR_GREEN}%s [%d/%d] %s completed successfully.${CLR_RESET}\n" \
        "$CHAR_CHECK" "$step_idx" "$total_steps" "$label"
      CURRENT_PCT="$end_pct"
      IN_STEP=0
      CURRENT_STEP_LABEL=""
      return 0
    else
      local ec=$?
      local bar_str
      bar_str="$(render_progress_bar "$end_pct" "$CLR_RED")"
      printf "${CLR_RED}%s [%d/%d] %s  %s (failed, exit code %d).${CLR_RESET}\n" \
        "$CHAR_CROSS" "$step_idx" "$total_steps" "$bar_str" "$label" "$ec"
      STEP_FAILED_PRINTED=1
      CURRENT_PCT="$end_pct"
      return "$ec"
    fi
  fi

  # In non-verbose mode, ensure sudo credentials before redirecting output to log file
  if step_requires_sudo "$@"; then
    local sudo_ec=0
    ensure_sudo "$label" || sudo_ec=$?
    if [ "$sudo_ec" -ne 0 ]; then
      if [ -t 1 ]; then
        printf '\033[?25h'
      fi
      local bar_str
      bar_str="$(render_progress_bar "$start_pct" "$CLR_RED")"
      if [ -t 1 ]; then
        printf "\r  ${CLR_RED}%s${CLR_RESET} [%d/%d] %s  ${CLR_RED}%s (sudo authentication failed)${CLR_RESET}\033[K\n" \
          "$CHAR_CROSS" "$step_idx" "$total_steps" "$bar_str" "$label"
      else
        printf "%s %s (failed)\n" "$bar_str" "$CHAR_CROSS"
      fi
      STEP_FAILED_PRINTED=1
      CURRENT_PCT="$start_pct"
      return "$sudo_ec"
    fi
  fi

  # Non-verbose, non-TTY mode (pipes, files, CI)
  if [ ! -t 1 ]; then
    if [ "$step_idx" -eq 1 ]; then
      printf "Installing Poke... "
    fi
    if "$@" >>"$LOG_FILE" 2>&1; then
      if [ "$step_idx" -eq "$total_steps" ]; then
        printf "%s %s\n" "$(render_progress_bar 100)" "$CHAR_CHECK"
      fi
      CURRENT_PCT="$end_pct"
      IN_STEP=0
      CURRENT_STEP_LABEL=""
      return 0
    else
      local ec=$?
      local bar_str
      bar_str="$(render_progress_bar "$start_pct" "$CLR_RED")"
      printf "%s %s (failed)\n" "$bar_str" "$CHAR_CROSS"
      STEP_FAILED_PRINTED=1
      CURRENT_PCT="$start_pct"
      return "$ec"
    fi
  fi

  # Non-verbose, interactive TTY mode: Single-line progress bar & spinner
  printf '\033[?25l' # Hide cursor

  "$@" >>"$LOG_FILE" 2>&1 &
  local cmd_pid=$!

  local frame_idx=0
  local num_frames=${#SPINNER[@]}
  local cur_pct=$start_pct
  local pct_range=$((end_pct - start_pct))
  local tick=0

  while kill -0 "$cmd_pid" 2>/dev/null; do
    if [ "$pct_range" -gt 1 ]; then
      cur_pct=$((start_pct + (tick / 4)))
      if [ "$cur_pct" -ge "$end_pct" ]; then
        cur_pct=$((end_pct - 1))
      fi
    fi
    CURRENT_PCT="$cur_pct"

    local spin_char="${SPINNER[$frame_idx]}"
    local bar_str
    bar_str="$(render_progress_bar "$cur_pct")"

    printf "\r  ${CLR_CYAN}%s${CLR_RESET} [%d/%d] %s  ${CLR_WHITE}%s...${CLR_RESET}\033[K" \
      "$spin_char" "$step_idx" "$total_steps" "$bar_str" "$label"

    frame_idx=$(((frame_idx + 1) % num_frames))
    tick=$((tick + 1))
    sleep 0.08
  done

  wait "$cmd_pid"
  local ec=$?

  if [ "$ec" -eq 0 ]; then
    CURRENT_PCT="$end_pct"
    IN_STEP=0
    CURRENT_STEP_LABEL=""
    local bar_str
    bar_str="$(render_progress_bar "$end_pct")"
    if [ "$step_idx" -eq "$total_steps" ]; then
      # Final step: Emit newline and restore cursor
      printf "\r  ${CLR_GREEN}%s${CLR_RESET} [%d/%d] %s  ${CLR_GREEN}Installation complete!${CLR_RESET}\033[K\n" \
        "$CHAR_CHECK" "$step_idx" "$total_steps" "$bar_str"
      printf '\033[?25h'
    else
      # Intermediate step: Remain on the same line, no newline
      printf "\r  ${CLR_CYAN}%s${CLR_RESET} [%d/%d] %s  ${CLR_WHITE}%s...${CLR_RESET}\033[K" \
        "${SPINNER[0]}" "$step_idx" "$total_steps" "$bar_str" "$label"
    fi
    return 0
  else
    printf '\033[?25h' # Restore cursor
    CURRENT_PCT="$cur_pct"
    local bar_str
    bar_str="$(render_progress_bar "$cur_pct" "$CLR_RED")"
    printf "\r  ${CLR_RED}%s${CLR_RESET} [%d/%d] %s  ${CLR_RED}%s (failed)${CLR_RESET}\033[K\n" \
      "$CHAR_CROSS" "$step_idx" "$total_steps" "$bar_str" "$label"
    STEP_FAILED_PRINTED=1
    return "$ec"
  fi
}

# Installation Step Definitions
step_prepare_workspace() {
  if [ "$INSTALL_MODE" = "local" ]; then
    local src_dir=""
    if [ -f "${SCRIPT_DIR}/src/poke.service" ]; then
      src_dir="${SCRIPT_DIR}"
    elif [ -f "${PWD}/src/poke.service" ]; then
      src_dir="${PWD}"
    else
      echo "Error: Cannot locate Poke source directory containing src/poke.service" >&2
      return 1
    fi

    if [ "$src_dir" != "$PROJECT_DIR" ]; then
      rm -rf "${PROJECT_DIR}"
      mkdir -p "${PROJECT_DIR}"
      cp -a "${src_dir}/." "${PROJECT_DIR}/"
      # Remove any copied source venv to ensure clean installation in target
      rm -rf "${PROJECT_DIR}/src/venv"
    else
      rm -rf "${PROJECT_DIR}/src/venv"
    fi
  else
    rm -rf "${PROJECT_DIR}"
    mkdir -p "${PROJECT_DIR}"
    git clone --depth=1 "${PROJECT_REPO}" "${PROJECT_DIR}"
  fi
}

step_setup_venv() {
  rm -rf "${PROJECT_DIR}/src/venv"
  "$PYTHON_BIN" -m venv "${PROJECT_DIR}/src/venv"
}

step_install_dependencies() {
  "${PROJECT_DIR}/src/venv/bin/pip" install --disable-pip-version-check --no-input -r "${PROJECT_DIR}/src/requirements.txt"
  chmod +x "${PROJECT_DIR}/src/run_daemon.sh"
}

step_configure_systemd() {
  mkdir -p "${HOME}/.config/systemd/user"
  cp "${PROJECT_DIR}/src/poke.service" "${HOME}/.config/systemd/user/poke.service"

  if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload
    systemctl --user enable poke.service
    systemctl --user restart poke.service
    sleep 1
    systemctl --user is-active --quiet poke.service
  else
    echo "Warning: systemctl not available; skipped starting poke.service"
  fi
}

step_link_to_usr_bin() {
  ensure_sudo "Linking Poké CLI to /usr/bin"
  local launcher="${PROJECT_DIR}/src/venv/bin/poke"
  printf '#!/bin/bash\nexec %q %q "$@"\n' \
    "${PROJECT_DIR}/src/venv/bin/python" \
    "${PROJECT_DIR}/src/poke_cli.py" >"$launcher"
  chmod +x "$launcher"
  sudo ln -sf "$launcher" /usr/bin/poke
}

step_setup_tailscale() {
  if ! command -v tailscale >/dev/null 2>&1; then
    ensure_sudo "Configuring Tailscale battle network"
    curl -fsSL https://tailscale.com/install.sh | sh
  fi
}

# CLI Argument Parsing
parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
    -v | --verbose)
      VERBOSE=1
      shift
      ;;
    -l | --local | local)
      INSTALL_MODE="local"
      shift
      ;;
    --skip-tailscale)
      SKIP_TAILSCALE=1
      shift
      ;;
    -h | --help)
      show_help
      exit 0
      ;;
    *)
      printf "Error: Unknown option '%s'\nRun with --help for usage details.\n" "$1" >&2
      CURRENT_STEP_LABEL="CLI option parsing ($1)"
      exit 1
      ;;
    esac
  done
}

# Main
main() {
  parse_args "$@"
  setup_theme

  # Initialize log file
  : >"$LOG_FILE"

  print_banner

  # Check Python requirement
  CURRENT_STEP_LABEL="Python 3 check"
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    printf "${CLR_RED}%s Error: Python 3 was not found on your PATH.${CLR_RESET}\n" "$CHAR_CROSS" >&2
    printf "Please install Python 3.8+ and try again.\n" >&2
    exit 1
  fi
  CURRENT_STEP_LABEL=""

  # Determine step percentages
  local total_steps=6
  local s1_start=0 s1_end=16
  local s2_start=16 s2_end=32
  local s3_start=32 s3_end=48
  local s4_start=48 s4_end=64
  local s5_start=64 s5_end=80
  local s6_start=80 s6_end=100

  if [ "$SKIP_TAILSCALE" -eq 1 ]; then
    total_steps=5
    s1_start=0 s1_end=20
    s2_start=20 s2_end=40
    s3_start=40 s3_end=60
    s4_start=60 s4_end=80
    s5_start=80 s5_end=100
  fi

  # Step 1: Workspace setup
  execute_step 1 "$total_steps" "$s1_start" "$s1_end" "Preparing Poke workspace" step_prepare_workspace

  # Step 2: Python virtual environment
  execute_step 2 "$total_steps" "$s2_start" "$s2_end" "Creating Python virtual environment" step_setup_venv

  # Step 3: Python dependencies
  execute_step 3 "$total_steps" "$s3_start" "$s3_end" "Installing Python dependencies" step_install_dependencies

  # Step 4: Systemd Service
  execute_step 4 "$total_steps" "$s4_start" "$s4_end" "Configuring systemd background daemon" step_configure_systemd

  # Step 5: Link to /usr/bin
  execute_step 5 "$total_steps" "$s5_start" "$s5_end" "Linking Poké CLI to /usr/bin" step_link_to_usr_bin

  # Step 6: Tailscale Setup (if not skipped)
  local ts_info="Skipped"
  if [ "$SKIP_TAILSCALE" -eq 0 ]; then
    if tailscale status >/dev/null 2>&1; then
      execute_step 6 "$total_steps" "$s6_start" "$s6_end" "Configuring Tailscale battle network" step_setup_tailscale
      local ts_ip
      ts_ip=$(tailscale ip -4 2>/dev/null || echo "Active")
      ts_info="Connected (${ts_ip})"
    else
      # Clear progress line before interactive prompt
      printf "\r\033[K"
      show_tailscale_notice
      printf "  %s Connecting to Tailscale network...\n" "$CHAR_ARROW"
      CURRENT_STEP_IDX=6
      CURRENT_TOTAL_STEPS="$total_steps"
      CURRENT_STEP_LABEL="Connecting to Tailscale network"
      CURRENT_PCT=80
      IN_STEP=1
      STEP_FAILED_PRINTED=0
      if [ -t 1 ]; then
        sudo tailscale up
      else
        sudo tailscale up >>"$LOG_FILE" 2>&1
      fi
      IN_STEP=0
      CURRENT_STEP_LABEL=""
      local ts_ip
      ts_ip=$(tailscale ip -4 2>/dev/null || echo "Active")
      ts_info="Connected (${ts_ip})"
      local full_bar
      full_bar="$(render_progress_bar 100)"
      printf "  ${CLR_GREEN}%s${CLR_RESET} [6/%d] %s  ${CLR_GREEN}Installation complete!${CLR_RESET}\033[K\n" \
        "$CHAR_CHECK" "$total_steps" "$full_bar"
    fi
  fi

  # Fetch daemon status
  local daemon_status="inactive"
  if command -v systemctl >/dev/null 2>&1 && systemctl --user is-active poke.service >/dev/null 2>&1; then
    daemon_status="poke.service (active / running)"
  fi

  # Display final summary card
  show_success_card "$PROJECT_DIR" "$daemon_status" "$ts_info"
}

main "$@"
