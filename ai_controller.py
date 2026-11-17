
class WorldRunner:
    def __init__(self, character, walker,grid, castle, anchors):
        self.character = character
        self.walker = walker
        self.grid = grid
        self.castle = castle
        self.anchors = anchors
        self.current = None
        self.phase = None
        self.timer = 0.0

    def tick(self, dt):
        self.timer += dt
    def cancel(self):
        self.phase = None
        self.current = None
        self.walker.stop()
    def _fail(self):
        self.cancel()
        return False
    def _object(self, action):
        return next((o for o in self.castle.interactable if o.id == action.data["object"]), None)