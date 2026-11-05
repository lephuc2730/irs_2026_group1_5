#!/usr/bin/env python3
"""Ensure MoveIt errors cannot advance the mission after action SUCCEEDED."""
from types import SimpleNamespace
import rclpy
from action_msgs.msg import GoalStatus
from pa_warehouse_status.warehouse_mission_controller import WarehouseMissionController


def wrapped_result(status, code):
    return SimpleNamespace(status=status, result=SimpleNamespace(
        error_code=SimpleNamespace(val=code)))


def main():
    rclpy.init()
    node = WarehouseMissionController()
    scheduled = []
    failures = []
    node._schedule = lambda delay, callback: scheduled.append(callback)
    node._fail = lambda reason: failures.append(reason)
    try:
        for status, code in [
            (GoalStatus.STATUS_SUCCEEDED, -1),
            (GoalStatus.STATUS_SUCCEEDED, -4),
            (GoalStatus.STATUS_ABORTED, 1),
        ]:
            node._arm_result(
                SimpleNamespace(result=lambda: wrapped_result(status, code)),
                [[0.0] * 6], 0, lambda: None)
            assert failures, f'Accepted failure status={status}, code={code}'
            assert not scheduled, 'Failure advanced arm sequence'
            failures.clear()
        node._arm_result(
            SimpleNamespace(result=lambda: wrapped_result(
                GoalStatus.STATUS_SUCCEEDED, 1)),
            [[0.0] * 6], 0, lambda: None)
        assert len(scheduled) == 1, 'MoveIt SUCCESS did not advance'
        assert not failures, failures
        print('MOVEIT_RESULT_GUARD_PASS')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
