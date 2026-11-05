#!/usr/bin/env python3
import time

import rclpy
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener


def main():
    rclpy.init()
    node = rclpy.create_node('grand_challenge_tf_ready_check')
    buffer = Buffer()
    listener = TransformListener(buffer, node)

    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
        if buffer.can_transform('map', 'virtual_hand_solo/base_link', Time()):
            tf = buffer.lookup_transform('map', 'virtual_hand_solo/base_link', Time())
            print('TF_READY')
            print(f"x={tf.transform.translation.x:.3f}")
            print(f"y={tf.transform.translation.y:.3f}")
            node.destroy_node()
            rclpy.shutdown()
            return

    node.destroy_node()
    rclpy.shutdown()
    raise SystemExit('TF_NOT_READY')


if __name__ == '__main__':
    main()
