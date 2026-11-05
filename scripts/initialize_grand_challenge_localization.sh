#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/jazzy/setup.bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Grand Challenge localization initialization ==="

echo "Waiting for odom -> base_link TF before setting initial pose..."
python3 "$SCRIPT_DIR/wait_for_tf.py" virtual_hand_solo/odom virtual_hand_solo/base_link 30

python3 "$SCRIPT_DIR/publish_initial_pose.py"

echo "Waiting for /amcl_pose..."
for attempt in 1 2 3 4 5; do
  if timeout 5s ros2 topic echo /amcl_pose --once >/tmp/grand_challenge_amcl.txt 2>/dev/null; then
    cat /tmp/grand_challenge_amcl.txt
    break
  fi
  if [ "$attempt" -eq 5 ]; then
    echo "ERROR: AMCL did not publish a pose."
    exit 1
  fi
  sleep 1
done

echo "Clearing costmaps after localization reset..."
ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1 || true
ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1 || true

sleep 2

echo "Waiting for fresh map -> base_link TF..."
python3 "$SCRIPT_DIR/wait_for_tf.py" map virtual_hand_solo/base_link 30

echo "LOCALIZATION_READY"
exit 0
