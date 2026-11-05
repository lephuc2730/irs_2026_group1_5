#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source /opt/ros/jazzy/setup.bash
if [ -f /workspace/irs_ws/install/setup.bash ]; then
  source /workspace/irs_ws/install/setup.bash
fi

echo "=== Applying Grand Challenge Nav2 tuning ==="
bash "$SCRIPT_DIR/grand_challenge_nav2_tuning.sh"

echo
echo "=== Starting integrated Grand Challenge controller ==="
exec ros2 launch pa_warehouse_status grand_challenge.launch.py
