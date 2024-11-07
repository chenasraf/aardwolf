import os
import sqlite3

# cp "~/Library/Application Support/CrossOver/Bottles/MushClient/drive_c/users/crossover/MUSHclient/Aardwolf.db" Aardwolf.db


class MapGenerator:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.grid = []

    rooms = []
    exits = []
    visited = {}

    def generate_map(self, area, out_type="ascii"):
        self.area = area
        self.rooms = []
        print(f"Generating map of {self.area}...")
        for row in self._get_all_rooms(self.area):
            uid, name, area, *rdata = row
            data = RoomData(*rdata)
            room = Room(uid, name, area, data)
            self.rooms.append(room)
        for room in self.rooms:
            exits = self._get_exits_for_room(room.uid)
            for ex in exits:
                direction, from_uid, to_uid, level = ex
                rexit = Exit(direction, from_uid, to_uid, level)
                room.exits.append(rexit)
                self.exits.append(rexit)
            # print(dict(room))
        outfile = f"outputs/{self.area}.txt"
        # make dir if not exists
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        self.assign_coordinates_shove()

        with open(outfile, "w") as f:
            self._write_map(self.rooms, f, out_type)

    def _get_all_rooms(self, area):
        self.cursor.execute(
            "SELECT uid, name, area, building, terrain, info, notes, x, y, z, norecall, noportal, ignore_exits_mismatch FROM rooms WHERE area = ?",
            (area,),
        )
        return self.cursor.fetchall()

    def _get_exits_for_room(self, uid):
        self.cursor.execute(
            "SELECT dir, fromuid, touid, level FROM exits WHERE fromuid = ?", (uid,)
        )
        return self.cursor.fetchall()

    def _write_map(self, rooms, f, out_type):
        if out_type == "ascii":
            self._write_ascii_map(rooms, f)
        # elif out_type == 'json':
        #   self._write_json_map(rooms, f)
        else:
            raise ValueError(f"Unknown output type: {out_type}")
        print(f"Map of {self.area} generated successfully.")

    def get_map_rect(self):
        visited = self.visited
        min_x = min(coord[0] for coord in visited.values()) - 1
        max_x = max(coord[0] for coord in visited.values()) + 1
        min_y = min(coord[1] for coord in visited.values()) - 1
        max_y = max(coord[1] for coord in visited.values()) + 1
        return (min_x, min_y), (max_x, max_y)

    def get_map_size(self):
        min, max = self.get_map_rect()
        return w, h

    def _write_ascii_map(self, rooms, f):
        visited = self.visited
        if not self.visited or not self.rooms:
            return
        min_x = min(coord[0] for coord in visited.values()) - 1
        max_x = max(coord[0] for coord in visited.values()) + 1
        min_y = min(coord[1] for coord in visited.values()) - 1
        max_y = max(coord[1] for coord in visited.values()) + 1

        # Adjust values to start indexing from 0
        range_x = max_x - min_x + 1
        range_y = max_y - min_y + 1

        # Prepare the grid
        grid = [["X" for _ in range(range_x)] for _ in range(range_y)]

        # Place Rooms
        for room_uid, (x, y) in visited.items():
            shifted_x = x - min_x  # Shift x to start from 0
            shifted_y = y - min_y  # Shift y to start from 0
            grid[shifted_y][shifted_x] = " "  # Mark room as ' '

        # Print grid
        for row in grid:
            f.write("".join(row) + "\n")

    def dfs(self, room, x, y):
        if not room:
            return
        # Base case: If the room is visited, return.
        if room.uid in self.visited:
            return self.visited[room.uid]

        # Conflict detection: Someone already here
        if (x, y) in self.visited.values():
            # Depending on the direction of the conflict, either a row or column needs to be shoved
            x, y = self.resolve_conflict(x, y)

        # Assign current room's position
        self.visited[room.uid] = (x, y)

        # Process exits
        for ex in room.exits:
            direction = ex.direction
            neighbor = self.find_room_by_uid(
                ex.to_uid
            )  # Helper function to find the room

            # Calculate its tentative new position based on the direction
            if direction == "n":
                new_x, new_y = x, y - 1
            elif direction == "s":
                new_x, new_y = x, y + 1
            elif direction == "e":
                new_x, new_y = x + 1, y
            elif direction == "w":
                new_x, new_y = x - 1, y
            elif direction == "u":  # Diagonal for upward connections
                new_x, new_y = x + 1, y - 1
            elif direction == "d":  # Diagonal for downward connections
                new_x, new_y = x - 1, y + 1
            else:
                new_x, new_y = x + 1, y - 1

            # Recursively call dfs on the neighboring room
            self.dfs(neighbor, new_x, new_y)

    def resolve_conflict(self, conflict_x, conflict_y):
        """
        Handle conflict when a room already exists at (x, y)
        by expanding the grid and shifting occupied rooms.
        """
        conflict_direction = self.get_conflict_direction(conflict_x, conflict_y)

        # Use a strategy based on row/column expansion
        if conflict_direction in ["n", "s"]:
            # Conflict moving north/south -> Insert a row
            return self.shove_and_add_row(conflict_x, conflict_y)
        elif conflict_direction in ["e", "w"]:
            # Conflict moving east/west -> Insert a column
            return self.shove_and_add_col(conflict_x, conflict_y)

    def get_conflict_direction(self, conflict_x, conflict_y):
        # Helper function to determine in which direction the conflict occurs.
        # You could use more logic to know what direction the shove is.
        # For simplicity in this example, let's prioritize rows first.
        return "s"  # We'll assume a row shove; expand to multiple cases.

    def shove_and_add_row(self, conflict_x, conflict_y):
        """
        Insert a new row to resolve a conflict at (x, y) for the north/south direction.
        Moves y-components of relevant rows.
        """
        # Shift all rows below (and including) conflict_y one space downwards
        for room_uid, (x, y) in self.visited.items():
            if y >= conflict_y:
                self.visited[room_uid] = (x, y + 1)

        # Now you can safely place the new room in the conflict_y position
        return conflict_x, conflict_y

    def shove_and_add_col(self, conflict_x, conflict_y):
        """
        Insert a new column to resolve conflict for an east/west movement.
        Moves x-components of relevant columns.
        """
        # Shift all columns at or to the right of (conflict_x) by 1
        for room_uid, (x, y) in self.visited.items():
            if x >= conflict_x:
                self.visited[room_uid] = (x + 1, y)

        # Now you can safely place the new room in the conflict_x position
        return conflict_x, conflict_y

    def assign_coordinates_shove(self):
        self.visited = {}  # Dictionary to track coordinates of each room by its uid.

        if not self.rooms:
            print(f"No rooms to generate map for {self.area}.")
            return self.visited

        # Start DFS from an initial room (the root room at position (0, 0))
        root_room = self.rooms[0]  # Assuming rooms is a list of Room objects
        self.dfs(root_room, 0, 0)

        for room in self.rooms[1:]:
            x, y = self.find_first_empty_spot()
            self.dfs(room, 0, 0)

        return self.visited  # Dictionary mapping room uid to (x, y) positions

    def find_first_empty_spot(self):
        # Helper function to find the first empty spot in the grid.
        w, h = self.get_map_size()
        for x in range(w):
            for y in range(h):
                if (x, y) not in self.visited.values():
                    return x, y

    def find_room_by_uid(self, uid):
        # Helper function to find a room based on its UID.
        for room in self.rooms:
            if room.uid == uid:
                return room
        return None


class RoomData:
    def __init__(
        self,
        building,
        terrain,
        info,
        notes,
        x,
        y,
        z,
        norecall,
        noportal,
        ignore_exits_mismatch,
    ):
        self.building = building
        self.terrain = terrain
        self.info = info
        self.notes = notes
        self.x = x
        self.y = y
        self.z = z
        self.norecall = norecall
        self.noportal = noportal
        self.ignore_exits_mismatch = ignore_exits_mismatch


class Room:
    def __init__(self, uid, name, area, data, exits=None):
        self.uid = uid
        self.name = name
        self.area = area
        self.data = data
        self.exits = exits or []

    def __iter__(self):
        yield from {
            **self.__dict__,
            "dir_exits": self.dir_exits,
            "cexits": self.cexits,
        }.items()

    @property
    def dir_exits(self):
        return {
            "n": self.exit_n.to_uid if self.exit_n else None,
            "s": self.exit_s.to_uid if self.exit_s else None,
            "e": self.exit_e.to_uid if self.exit_e else None,
            "w": self.exit_w.to_uid if self.exit_w else None,
            "u": self.exit_u.to_uid if self.exit_u else None,
            "d": self.exit_d.to_uid if self.exit_d else None,
        }

    @property
    def exit_n(self):
        return self._get_exit("n")

    @property
    def exit_s(self):
        return self._get_exit("s")

    @property
    def exit_e(self):
        return self._get_exit("e")

    @property
    def exit_w(self):
        return self._get_exit("w")

    @property
    def exit_u(self):
        return self._get_exit("u")

    @property
    def exit_d(self):
        return self._get_exit("d")

    def _get_exit(self, direction):
        for ex in self.exits:
            if ex.direction == direction:
                return ex
        return None

    def cexits(self):
        return [
            e for e in self.exits if e.direction not in ["n", "s", "e", "w", "u", "d"]
        ]


class Exit:
    def __init__(self, direction, from_uid, to_uid, level=0):
        self.direction = direction
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.level = level


DB_NAME = "Aardwolf.db"
generator = MapGenerator(DB_NAME)
generator.generate_map("ftii")
generator.generate_map("drageran")

