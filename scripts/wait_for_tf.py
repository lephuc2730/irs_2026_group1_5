#!/usr/bin/env python3
import sys
import time

import rclpy
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: wait_for_tf.py TARGET_FRAME SOURCE_FRAME [timeout_sec]")

    target = sys.argv[1]
    source = sys.argv[2]
    timeout_sec = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0

    rclpy.init()
    node = rclpy.create_node("grand_challenge_wait_for_tf")
    buffer = Buffer()
    listener = TransformListener(buffer, node)

    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
        if buffer.can_transform(target, source, Time()):
            tf = buffer.lookup_transform(target, source, Time())
            print("TF_READY")
            print(f"{target} <- {source}")
            print(f"x={tf.transform.translation.x:.3f}")
            print(f"y={tf.transform.translation.y:.3f}")
            node.destroy_node()
            rclpy.shutdown()
            return

    node.destroy_node()
    rclpy.shutdown()
    raise SystemExit(f"TF_NOT_READY: {target} <- {source}")


if __name__ == "__main__":
    main()
