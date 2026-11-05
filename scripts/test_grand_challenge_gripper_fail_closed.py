#!/usr/bin/env python3
"""Verify the mission refuses to transport a box without an attach adapter."""
import rclpy
from pa_warehouse_status.warehouse_mission_controller import WarehouseMissionController


def main():
    rclpy.init()
    node = WarehouseMissionController()
    try:
        assert node.get_parameter('allow_unverified_gripper').value is False
        node.current_category = 'large'
        node.busy = True
        node._after_grasp_position()
        assert node.busy is False, 'Controller did not stop'
        assert node.failed_category == 'large', 'Failed box not retained'
        assert node.current_category is None
        assert not node._timers, 'Unverified box transport was scheduled'
        print('GRIPPER_FAIL_CLOSED_PASS', flush=True)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
