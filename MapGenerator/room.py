class Room:
    def __init__(self, uid, name, area, notes, data=None):
        self.uid = uid
        self.name = name
        self.area = area
        self.notes = notes
        self.data = data or {}
        self.exits = {}

    def add_exit(self, direction, ex):
        self.exits[direction] = ex

    def get_exit(self, direction):
        return self.exits.get(direction)

    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "area": self.area,
            "notes": self.notes,
            "data": self.data,
            "exits": {k: v.to_dict() for k, v in self.exits.items()},
        }


class Exit:
    def __init__(self, direction, from_room, to_room, level):
        self.direction = direction
        self.from_room = from_room
        self.to_room = to_room
        self.level = level

    def to_dict(self):
        return {
            "direction": self.direction,
            "from_room": self.from_room,
            "to_room": self.to_room,
            "level": self.level,
        }

