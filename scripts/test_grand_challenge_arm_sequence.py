#!/usr/bin/env python3
import sys
import time

import rclpy
from rclpy.action import ActionClient
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, Constraints, JointConstraint

JOINT_NAMES = ['joint_1','joint_2','joint_3','joint_4','joint_5','joint_6']
PLANNING_GROUP = 'tmr_arm'

POSES = [
    ('SAFE_ARM', [0.0, 0.0, 1.57, 0.0, 1.57, 0.0]),
    ('PICK_APPROACH', [0.785, -0.5, 1.2, 0.0, 1.0, 0.0]),
    ('PICK_GRASP', [0.785, -0.8, 1.4, 0.0, 0.8, 0.0]),
    ('PICK_RETRACT', [0.785, -0.3, 1.2, 0.0, 1.0, 0.0]),
    ('SAFE_ARM_RETURN', [0.0, 0.0, 1.57, 0.0, 1.57, 0.0]),
]


def make_goal(joints):
    goal = MoveGroup.Goal()
    req = MotionPlanRequest()
    req.group_name = PLANNING_GROUP
    req.num_planning_attempts = 10
    req.allowed_planning_time = 5.0
    req.max_velocity_scaling_factor = 0.35
    req.max_acceleration_scaling_factor = 0.30

    constraints = Constraints()
    for name, value in zip(JOINT_NAMES, joints):
        jc = JointConstraint()
        jc.joint_name = name
        jc.position = value
        jc.tolerance_above = 0.01
        jc.tolerance_below = 0.01
        jc.weight = 1.0
        constraints.joint_constraints.append(jc)

    req.goal_constraints.append(constraints)
    goal.request = req
    goal.planning_options.plan_only = False
    return goal


def main():
    rclpy.init()
    node = rclpy.create_node('grand_challenge_arm_sequence_test')
    client = ActionClient(node, MoveGroup, '/move_action')

    if not client.wait_for_server(timeout_sec=30.0):
        node.get_logger().error('/move_action unavailable')
        rclpy.shutdown()
        raise SystemExit(2)

    for label, joints in POSES:
        node.get_logger().info(f'SENDING {label}: {joints}')
        send_future = client.send_goal_async(make_goal(joints))
        rclpy.spin_until_future_complete(node, send_future, timeout_sec=20.0)
        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            node.get_logger().error(f'{label}: goal rejected')
            rclpy.shutdown()
            raise SystemExit(3)

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(node, result_future, timeout_sec=60.0)
        wrapped = result_future.result()
        if wrapped is None:
            node.get_logger().error(f'{label}: no result')
            rclpy.shutdown()
            raise SystemExit(4)

        moveit_code = wrapped.result.error_code.val
        node.get_logger().info(f'{label}: status={wrapped.status} moveit_error_code={moveit_code}')
        if moveit_code != 1:
            node.get_logger().error(f'{label}: FAILED')
            rclpy.shutdown()
            raise SystemExit(5)

        node.get_logger().info(f'{label}: PASS')
        time.sleep(0.5)

    node.get_logger().info('ARM_SEQUENCE_PASS')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
