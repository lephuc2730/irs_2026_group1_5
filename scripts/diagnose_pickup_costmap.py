#!/usr/bin/env python3
"""Read-only Nav2 costmap reachability diagnostic. Never commands robot motion."""
import math
import time
from collections import deque
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

GOALS = [(4.3, -0.8), (5.0, 0.0), (31.0, -5.5)]

class Probe(Node):
    def __init__(self):
        super().__init__('grand_challenge_costmap_probe')
        self.grid = None
        self.pose = None
        self.create_subscription(OccupancyGrid, '/global_costmap/costmap', self.on_grid,
            QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=1,
                       reliability=ReliabilityPolicy.RELIABLE,
                       durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.on_pose, 10)
    def on_grid(self, msg):
        self.grid = msg
    def on_pose(self, msg):
        self.pose = msg.pose.pose.position

def main():
    rclpy.init()
    n = Probe()
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline and (n.grid is None or n.pose is None):
        rclpy.spin_once(n, timeout_sec=0.5)
    if n.grid is None or n.pose is None:
        print(f'DIAGNOSTIC INCOMPLETE: costmap={n.grid is not None}, AMCL={n.pose is not None}; refusing to guess a waypoint', flush=True)
        n.destroy_node()
        rclpy.shutdown()
        raise SystemExit(2)
    info = n.grid.info
    w, h = info.width, info.height
    res = info.resolution
    ox, oy = info.origin.position.x, info.origin.position.y
    data = n.grid.data
    def cell(x, y):
        return int(math.floor((x - ox)/res)), int(math.floor((y - oy)/res))
    def inside(i, j):
        return 0 <= i < w and 0 <= j < h
    def cost(i, j):
        return data[j*w+i] if inside(i, j) else None
    def free(i, j):
        return cost(i, j) == 0
    start = cell(n.pose.x, n.pose.y)
    print(f'Costmap {w}x{h} res={res} origin=({ox:.2f},{oy:.2f}); AMCL=({n.pose.x:.2f},{n.pose.y:.2f}) start_cell={start} cost={cost(*start)}')
    for x, y in GOALS:
        ij = cell(x,y)
        print(f'Goal ({x:.2f},{y:.2f}) cell={ij} cost={cost(*ij)}')
    if not free(*start):
        print('START BLOCKED OR UNKNOWN in costmap: cannot infer reachability safely.')
    else:
        visited = bytearray(w*h)
        q = deque([start])
        visited[start[1]*w+start[0]] = 1
        while q:
            i,j = q.popleft()
            for ni,nj in ((i+1,j),(i-1,j),(i,j+1),(i,j-1)):
                if inside(ni,nj):
                    k=nj*w+ni
                    if not visited[k] and free(ni,nj):
                        visited[k]=1
                        q.append((ni,nj))
        print(f'Free cells connected to robot: {sum(visited)}')
        for x,y in GOALS:
            gi,gj=cell(x,y)
            print(f'Goal ({x:.2f},{y:.2f}) connected={bool(inside(gi,gj) and visited[gj*w+gi])}')
            best=None
            radius=round(1.5/res)
            for j in range(max(0,gj-radius),min(h,gj+radius+1)):
                for i in range(max(0,gi-radius),min(w,gi+radius+1)):
                    if visited[j*w+i]:
                        d=math.hypot(i-gi,j-gj)
                        if best is None or d<best[0]:
                            best=(d,i,j)
            if best:
                _,i,j=best
                print(f'Closest CONNECTED free cell within 1.5m of ({x:.2f},{y:.2f}): ({ox+(i+0.5)*res:.2f},{oy+(j+0.5)*res:.2f}); candidate only, NOT arm-reach verified')
            else:
                print(f'No connected free cell within 1.5m of ({x:.2f},{y:.2f})')
    n.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
