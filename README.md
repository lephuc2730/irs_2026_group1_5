# Pine-Apple Grand Challenge — Group 5

This project connects the warehouse PLC and HMI to a ROS 2 mission controller. The controller receives box information, uses Nav2 to move the mobile base, and uses MoveIt to position the arm for pickup and delivery.

This guide covers setup, localisation, monitoring and the intended delivery sequence. Physical box attachment, transport and release must be confirmed in the simulator before treating a delivery as complete.

## 1. Update the repository

On the host machine, update the project:

```bash
cd ~/Clone
git pull origin main
```

The repository should be available inside the ROS workspace at:

```text
/workspace/irs_ws/src/Clone
```

The main project directories are:

- `pa_warehouse_status/` — PLC communication and mission control.
- `hand_solo_arm/` — arm and MoveIt work.
- `hand_solo_virtual_nav/` — mapping and navigation work.
- `scripts/` — startup and validation helpers.

## 2. Start the course Docker environment

On the host machine, open the directory containing the official course `compose.yaml`.

Check that the Hand Solo launch command enables the simulated TM arm and the required components:

```text
tm_use_simulation:=true use_arm:=true use_base:=true use_moveit:=true use_nav2:=true use_rviz:=true
```

If the file contains `tm_use_simulation:=false`, update it:

```bash
sed -i 's/tm_use_simulation:=false/tm_use_simulation:=true/' compose.yaml
```

Inspect the launch command:

```bash
grep -A2 'command: ros2 launch handsolo_ros' compose.yaml
```

Start the required services and check their status:

```bash
docker compose up -d irs-simulation irs-openplc-runtime omron-workspace omron_handsolo
docker compose ps
```

## 3. Enter the ROS workspace

From the same host directory, enter the workspace container:

```bash
docker compose exec omron-workspace bash
```

Inside the container, load ROS and open the workspace:

```bash
source /opt/ros/jazzy/setup.bash
cd /workspace/irs_ws
```

The commands in this guide use the ROS 2 Jazzy environment shown in the supplied setup.

## 4. Build the project packages

Run inside the workspace container:

```bash
colcon build --packages-select pa_warehouse_status hand_solo_virtual_nav hand_solo_arm
source install/setup.bash
```

Resolve any build errors before continuing.

## 5. Run the preflight checks

Check the required interfaces before starting the mission controller:

```bash
bash /workspace/irs_ws/src/Clone/scripts/grand_challenge_preflight.sh
```

The expected interfaces include:

| Interface | Role |
| --- | --- |
| `/hmi/unified_status` | PLC and box status topic |
| `/virtual_hand_solo/scan` | LiDAR topic |
| `/amcl_pose` | Estimated robot pose topic |
| `/move_action` | MoveIt action |
| `/navigate_to_pose` | Nav2 action |
| `/amcl` | Localisation node |
| `/move_group` | MoveIt node |

The expected completion message is:

```text
PRE-FLIGHT: core PLC + Nav2 + MoveIt interfaces are visible.
```

If an interface is missing, check the relevant container or node before proceeding. Interface visibility alone does not confirm that a complete mission will succeed.

## 6. Set the starting pose in RViz

Set the initial pose to match the robot's actual position, particularly when the judge chooses an arbitrary starting location.

1. Select **2D Pose Estimate** in RViz.
2. Click the robot's position on the map.
3. Drag the arrow to match its heading.

Check that AMCL is publishing a pose:

```bash
ros2 topic echo /amcl_pose --once
```

Receiving a message confirms that a pose is being published. Also inspect the map, robot pose and laser alignment in RViz before starting navigation.

For repeatable tests with the helper's configured starting pose, the repository provides:

```bash
bash /workspace/irs_ws/src/Clone/scripts/initialize_grand_challenge_localization.sh
```

Use RViz for the judged demonstration when the starting location differs from the helper configuration.

## 7. Start the mission controller

Run the startup helper inside the workspace container:

```bash
bash /workspace/irs_ws/src/Clone/scripts/start_grand_challenge.sh
```

The helper loads ROS and the workspace, applies the configured Nav2 tuning, and launches `warehouse_mission_controller`.

Keep this terminal open while the mission runs.

Do not run `hand_solo_virtual_nav/nav_launch.py` alongside the official Hand Solo Nav2 stack.

## 8. Monitor mission and PLC status

Open another host terminal in the course Docker directory and enter the workspace container:

```bash
docker compose exec omron-workspace bash
```

Load the environment:

```bash
source /opt/ros/jazzy/setup.bash
source /workspace/irs_ws/install/setup.bash
```

Monitor the mission state:

```bash
ros2 topic echo /warehouse/mission_status
```

To monitor PLC data simultaneously, open another terminal, repeat the container and environment setup, then run:

```bash
ros2 topic echo /hmi/unified_status
```

## 9. Run the full Grand Challenge

After confirming reliable individual deliveries, perform the complete demonstration:

1. Set the initial pose for the robot's actual starting location.
2. Deploy a Large box and confirm pickup, delivery and return.
3. Deploy a Medium box and confirm pickup, delivery and return.
4. Deploy a Small box and confirm pickup, delivery and mission completion.

The goal is minimal manual intervention after initial localisation. Confirm physical pickup and release for every delivery rather than relying only on mission-status messages.

## PLC classification

The preferred classification method uses increases in the PLC counters:

| PLC counter | Box category |
| --- | --- |
| `counts.big` | Large |
| `counts.medium` | Medium |
| `counts.small` | Small |

When usable counter information is unavailable, the documented weight fallback is:

| Weight | Box category |
| --- | --- |
| Greater than 10 kg | Large |
| 5–10 kg, inclusive | Medium |
| Less than 5 kg | Small |

## Validation status

The supplied project notes report successful checks for:

- Project build and core interface availability.
- AMCL localisation helper.
- Navigation from pickup to the Large shelf and back.
- MoveIt safe, approach, grasp and retract poses.
- MoveIt action-result and error-code checks.
- PLC Large, Medium and Small classification.
- The controller's stop behaviour when grasp verification is unavailable.

These are reported results from the project notes; this README revision does not constitute a new simulator test.

**Physical box attachment, transport and release remain unconfirmed in the supplied notes.** The controller publishes `CLOSE` and `OPEN` on `/warehouse/gripper_command`, but the notes do not identify a confirmed attach/detach or vacuum interface in the official runtime. Verify this connection before claiming a complete delivery demonstration.

## Troubleshooting commands

Run these commands inside the workspace container after sourcing ROS and the workspace.

### Warehouse services and topics

```bash
ros2 service list | grep '^/warehouse/'
ros2 topic list | grep '^/warehouse/'
```

### Navigation and arm actions

```bash
ros2 action list | grep navigate_to_pose
ros2 action list | grep move_action
```

### Latest PLC and localisation messages

```bash
ros2 topic echo /hmi/unified_status --once
ros2 topic echo /amcl_pose --once
```

## Main project files

| File | Purpose |
| --- | --- |
| `pa_warehouse_status/pa_warehouse_status/warehouse_mission_controller.py` | Integrated mission state machine |
| `pa_warehouse_status/config/grand_challenge_params.yaml` | Pickup and shelf configuration |
| `pa_warehouse_status/launch/grand_challenge.launch.py` | Mission controller launch |
| `scripts/grand_challenge_preflight.sh` | PLC, Nav2, MoveIt and LiDAR checks |
| `scripts/start_grand_challenge.sh` | Navigation tuning and controller startup |
| `scripts/initialize_grand_challenge_localization.sh` | Repeatable initial-pose helper |
| `scripts/test_grand_challenge_arm_sequence.py` | Isolated MoveIt validation |
| `scripts/test_grand_challenge_plc_events.py` | PLC classification validation |
| `scripts/test_grand_challenge_moveit_result.py` | MoveIt result-guard validation |

## Retained semester work

- `pa_warehouse_status` — PLC and ROS communication.
- `hand_solo_virtual_nav` — mapping and navigation lab work.
- `hand_solo_arm` — MoveIt arm lab work.
- `docs/evidence/` — previous runtime evidence.

See `docs/GRAND_CHALLENGE_READINESS.md` for the readiness checklist against the assessment rubric.
