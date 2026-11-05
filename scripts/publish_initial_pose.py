#!/usr/bin/env python3
import time

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.duration import Duration


def main():
    rclpy.init()
    node = rclpy.create_node('grand_challenge_initialpose_publisher')
    pub = node.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)

    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = 'map'
    msg.pose.pose.position.x = 0.0
    msg.pose.pose.position.y = 0.0
    msg.pose.pose.position.z = 0.0
    msg.pose.pose.orientation.x = 0.0
    msg.pose.pose.orientation.y = 0.0
    msg.pose.pose.orientation.z = 0.0
    msg.pose.pose.orientation.w = 1.0

    msg.pose.covariance[0] = 0.25
    msg.pose.covariance[7] = 0.25
    msg.pose.covariance[35] = 0.0685

    # Publish several freshly-stamped messages. AMCL may still be finishing
    # lifecycle activation when the first one arrives.
    for _ in range(5):
        # Hand Solo base TF can lag wall/ROS time by a few hundred ms in Docker.
        # Stamp the initial pose slightly in the past so AMCL can transform it
        # immediately instead of rejecting it as an extrapolation into the future.
        msg.header.stamp = (node.get_clock().now() - Duration(seconds=1.0)).to_msg()
        pub.publish(msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.5)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
