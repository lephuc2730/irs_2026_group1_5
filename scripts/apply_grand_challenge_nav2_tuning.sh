#!/usr/bin/env bash
set -euo pipefail

echo "=== Applying Grand Challenge Nav2 runtime tuning ==="

# Keep AMCL refreshing even for very small movements.
ros2 param set /amcl update_min_d 0.0
ros2 param set /amcl update_min_a 0.0

# The official Docker stack can be CPU-limited in CI. Lower loop rates reduce
# delayed paths and stale TF data while preserving normal navigation behavior.
ros2 param set /controller_server controller_frequency 10.0
ros2 param set /planner_server expected_planner_frequency 2.0
ros2 param set /local_costmap/local_costmap update_frequency 10.0
ros2 param set /local_costmap/local_costmap publish_frequency 5.0

# Allow the controller/costmaps to tolerate temporary TF lag in the simulator.
# The observed CI lag can exceed 4-5 seconds under load.
ros2 param set /controller_server FollowPath.transform_tolerance 10.0
ros2 param set /local_costmap/local_costmap transform_tolerance 10.0
ros2 param set /global_costmap/global_costmap transform_tolerance 10.0
ros2 param set /behavior_server transform_tolerance 10.0
ros2 param set /bt_navigator default_server_timeout 5000

echo
echo "=== Verify ==="
ros2 param get /amcl update_min_d
ros2 param get /amcl update_min_a
ros2 param get /controller_server controller_frequency
ros2 param get /planner_server expected_planner_frequency
ros2 param get /local_costmap/local_costmap update_frequency
ros2 param get /local_costmap/local_costmap publish_frequency
ros2 param get /controller_server FollowPath.transform_tolerance
ros2 param get /local_costmap/local_costmap transform_tolerance
ros2 param get /global_costmap/global_costmap transform_tolerance
ros2 param get /behavior_server transform_tolerance
ros2 param get /bt_navigator default_server_timeout

echo "Grand Challenge Nav2 tuning applied."
