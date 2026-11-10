import pygame
import heapq

CELL = 16
DIRS = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]

class NavGrid:
    def __init__(self, navmesh, width, height, cell=CELL, radius=12):
        self.cell = cell
        self.navmesh = navmesh
        self.cols = width // cell +1
        self.rows = height // cell +1
        self.radius = radius
        self.free= set()
        self.gates = {}
        self.build()

    def build(self):
        for cy in range(self.rows):
            for cx in range(self.cols):
                x,y = self.center(cx,cy)
                if self.navmesh.body_free(x, y, self.radius):
                    self.free.add((cx,cy))
    def cell_of(self,p):
        return (int(p[0] / self.cell),int(p[1] / self.cell))
    def center(self,cx,cy):
        return ((cx*0.5)*self.cell,(cy*0.5)*self.cell)

    def passable(self, cell, character=None):
        return cell in self.free
    def nearest_passable(self, cell, character=None, max_ring=6):
        if self.passable(cell, character):
            return cell
        for ring in range(1,max_ring+1):
            best =None
            for dx in range(-ring,ring+1):
                for dy in range(-ring,ring+1):
                    if max(abs(dx),abs(dy)) != ring:
                        continue
                    c = (cell[0] + dx, cell[1] + dy)
                    if self.passable(c, character):
                        d = dx*dx + dy*dy
                        if best is None or d < best[0]:
                            best = (d,c)
            if best:
                return best[1]
        return None

    def neighbors(self, cell, character):
        for dx,dy in DIRS:
            nxt = (cell[0] + dx, cell[1] + dy)
            if not self.passable(nxt, character):
                continue
            if dx and dy and not (self.passable((cell[0] + dx, cell[1] + dy), character)):
                continue
            yield nxt, (1.414 if dx and dy else 1.0)
    def find_path(self, start, goal, character=None):
        start = self.nearest_passable(self.cell_of(start), character)
        goal = self.nearest_passable(self.cell_of(goal), character)
        if start is None or goal is None:
            return None
        heap = [(0.0,0.0, start)]
        came = {start: None}
        cost = {start: 0.0}
        while heap:
            _, c0, current = heapq.heappop(heap)
            if current == goal:
                break
            if c0 > cost[current]:
                continue
            for nxt,step in self.neighbors(current, character):
                new = cost[current] + step
                if new < cost[nxt]:
                    cost[nxt] = new
                    came[nxt] = current
                    dx,dy= abs(nxt[0] - goal[0]), abs(nxt[1] - goal[1])
                    h = (dx+dy) - 0.586 *min(dx,dy)
                    heapq.heappush(heap,(new+h,new, nxt))
        if goal not in came:
            return None
        cells =[]
        current = goal
        while current is not None:
            cells.append(current)
            current = came[current]
        cells.reverse()
        doors= []
        for cell in cells:
            d = self.gates.get(cell)
            if d is not None and d not in doors:
                doors.append(d)
        return doors