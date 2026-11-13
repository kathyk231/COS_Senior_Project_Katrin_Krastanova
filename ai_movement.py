import pygame
import heapq

CELL = 16
DIRS = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
DOOR_REACH = 40
ARRIVE = 6
class Walker:
    def __init__(self, character, grid):
        self.character = character
        self.grid = grid
        self.status = "idle"
        self.target = None
        self.repaths = 0
        self.points = []
        self.doors = []
        self.stuck_time =0.0
        self.last_pos =pygame.Vector2(character.position)
    def go_to(self, point):
        self.target = pygame.Vector2(point)
        self.repaths = 0
        self._plan()
    def stop(self):
        self.status = "idle"
        self.points, self.doors = [], []
    def _plan(self):
        found = self.grid.find_path(self.character.position, self.target, self.character)
        if found is None:
            self.points, self.doors = [], []
            self.status ="failed"
            return
        self.points, self.doors = found
        self.status = "walking"
        self.stuck_time =0.0
        self.last_pos = pygame.Vector2(self.character.position)
    def update(self, dt, navmesh):
        if self.status != "walking":
            return self.status
        ch = self.character
        for door in self.doors:
            if not door.is_open and ch.position.distance_to(door.position) < DOOR_REACH:
                if not door.open_door(ch):
                    self.status = "failed"
                    return self.status
        while self.points and ch.position.distance_to(self.points[0]) < ARRIVE:
            self.points.pop(0)
        if not self.points:
            self.status = "arrived"
            return self.status
        ch.move(self.points[0] - ch.position, dt, navmesh)
        self.stuck_time += dt
        if ch.position.distance_to(self.last_pos) > 6:
            self.last_pos = pygame.Vector2(ch.position)
            self.stuck_time = 0.0
        elif self.stuck_time > 1.0:
            self.repaths += 1
            if self.repaths > 2:
                self.status = "failed"
            else:
                self._plan()
        return self.status

def door_ok(door, character):
    if door.hidden or door.locked:
        return False
    return door.is_open or door.can_open(character)

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
        c = self.cell
        for door, rect in self.navmesh.openings:
            for cy in range(rect.top // c, rect.bottom// c +1 ):
                for cx in range(rect.left // c, rect.right // c + 1):
                    cell =(cx,cy)
                    if cell in self.free or cell in self.gates:
                        continue
                    x, y = self.center(cx,cy)
                    if rect.collidepoint(x,y) and self.navmesh.body_free_through(x,y, self.radius, door):
                        self.gates[cell] = door
    def cell_of(self,p):
        return (int(p[0] // self.cell),int(p[1] // self.cell))
    def center(self,cx,cy):
        return ((cx+0.5)*self.cell,(cy+0.5)*self.cell)

    def passable(self, cell, character=None):
        if cell in self.free:
            return True
        door = self.gates.get(cell)
        return door is not None and character is not None and door_ok(door, character)
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
            if dx and dy and not (self.passable((cell[0] + dx, cell[1]), character), self.passable((cell[0], cell[1] + dy), character)):
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
                if new < cost.get(nxt, float('inf')):
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
        return self.simplify(cells), doors

    def simplify(self, cells):
        if len(cells) == 1:
            return [pygame.Vector2(self.center(*cells[0]))]
        keep = []
        for i in range(1, len(cells) - 1):
            d1 = (cells[i][0] - cells[i - 1][0], cells[i][1] - cells[i - 1][1])
            d2 = (cells[i + 1][0] - cells[i][0], cells[i + 1][1] - cells[i][1])
            if d1 != d2:
                keep.append(cells[i])
        keep.append(cells[-1])
        return [pygame.Vector2(self.center(*c)) for c in keep]