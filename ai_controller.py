
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
    def __call__(self, action):
        kind = action.data.get["kind", "use"]
        if self.current is not action:
            self.current = action
            self.phase = "walk"
            self.timer = 0.0
            if kind =="move":
                target = self.anchors.get(action.data["goto_room"])
            else:
                obj = self._object(action)
                target = self.grid.stand_point(obj) if obj else None
            if target is None:
                return self._fail()
            self.walker.goto(target)
        if self.phase == "walk":
            status = self.walker.status()
            if status == "failed":
                return self._fail()
            if status != "arrived":
                return "running"
            self.walker.stop()
            if kind == "move":
                self.current = None
                return True
            self.phase = "do"
        if self.phase =="do":
            obj = self._object(action)
            if kind =="give":
                msg = obj.on_give(self.character, obj, self.castle, item=action.dta.get("object"))
            else:
                msg = obj.search(self.character, self.castle)
            print(f"[{self.character.name}] {msg}")
            self.phase = "wait"
            self.timer = 0.0
        return self._fail()