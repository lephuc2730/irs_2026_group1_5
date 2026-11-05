#!/usr/bin/env python3
"""Regression tests for PLC event classification without robot movement."""
import json
import rclpy
from std_msgs.msg import String
from pa_warehouse_status.warehouse_mission_controller import WarehouseMissionController


def plc(node, counts=None, weight=None, location='ready'):
    payload = {'box': {'weight_raw': weight, 'location': location}}
    if counts is not None:
        payload['counts'] = counts
    msg = String()
    msg.data = json.dumps(payload)
    node._plc_callback(msg)


def main():
    rclpy.init()
    node = WarehouseMissionController()
    # Never move the robot in this test. Capture only the queue.
    node._maybe_start_next = lambda: None
    try:
        initial = {'big': 0, 'medium': 0, 'small': 0, 'total': 0}
        plc(node, initial)
        assert list(node.pending) == [], 'First counter sample should set baseline'
        plc(node, initial)
        assert list(node.pending) == [], 'Unchanged counts must not duplicate'
        plc(node, {'big': 1, 'medium': 0, 'small': 0, 'total': 1})
        plc(node, {'big': 1, 'medium': 1, 'small': 0, 'total': 2})
        plc(node, {'big': 1, 'medium': 1, 'small': 1, 'total': 3})
        assert list(node.pending) == ['large', 'medium', 'small'], list(node.pending)
        plc(node, {'big': 1, 'medium': 1, 'small': 1, 'total': 3}, 20)
        assert len(node.pending) == 3, 'Weight changes must not duplicate counter events'
        plc(node, {'big': 0, 'medium': 0, 'small': 0, 'total': 0})
        assert len(node.pending) == 3, 'Counter reset must not enqueue'
        plc(node, {'big': 1, 'medium': 0, 'small': 0, 'total': 1})
        assert len(node.pending) == 4 and node.pending[-1] == 'large'
        node.pending.clear()
        node.last_counts = None
        plc(node, None, '12.5 kg')
        plc(node, None, '12.5 kg')
        plc(node, None, '7.0 kg')
        plc(node, None, '3.0 kg')
        assert list(node.pending) == ['large', 'medium', 'small'], list(node.pending)
        print('PLC_CLASSIFICATION_PASS')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
