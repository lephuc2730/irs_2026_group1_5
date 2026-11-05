#!/usr/bin/env bash
set -eo pipefail

# Grand Challenge Nav2 runtime tuning for the official Hand Solo stack.
# The stock course values are tight enough to trigger stale-TF / action-server
# timeouts under the full Docker workload. These values were validated against
# the official Pine-Apple + Hand Solo environment.

source /opt/ros/jazzy/setup.bash

retry_set() {
  local node="$1"
  local param="$2"
  local value="$3"

  for attempt in {1..20}; do
    if ros2 param set "$node" "$param" "$value" >/tmp/grand_challenge_param_set.txt 2>&1; then
      echo "[OK] $node $param=$value"
      return 0
    fi
    sleep 1
  done

  echo "[ERROR] Could not set $node $param=$value"
  cat /tmp/grand_challenge_param_set.txt || true
  return 1
}

retry_set /amcl update_min_d 0.0
retry_set /amcl update_min_a 0.0
retry_set /amcl transform_tolerance 3.0
retry_set /controller_server FollowPath.transform_tolerance 3.0
retry_set /local_costmap/local_costmap transform_tolerance 3.0
retry_set /bt_navigator default_server_timeout 5000
retry_set /bt_navigator wait_for_service_timeout 5000

echo
echo "Grand Challenge Nav2 tuning applied."
echo "Validated pickup target: x=5.0, y=0.0, yaw=pi"
