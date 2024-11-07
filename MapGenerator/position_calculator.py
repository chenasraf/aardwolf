class PositionCalculator:
    compass_directions = {
        'n': (0, 1),
        's': (0, -1),
        'e': (1, 0),
        'w': (-1, 0),
        'ne': (1, 1),
        'nw': (-1, 1),
        'se': (1, -1),
        'sw': (-1, -1),
    }

    def __init__(self, rooms, exits):
        self.rooms = rooms
        self.exits = exits
        self.positions = {}  # Store node positions (UID -> (x, y))
        self.grid = {}  # Track occupied grid positions

    def direction_to_offset(self, direction):
        """Convert a compass direction into an (x, y) offset for positioning."""
        return self.compass_directions.get(direction, (0, 0))

    def _place_room(self, room, position, visited):
        if room.uid in self.positions:
            return
        # Assign the position
        self.positions[room.uid] = position
        self.grid[position] = room.uid  # Track grid usage
        visited.add(room.uid)

        # Explore each exit and assign the position of the connected room
        for direction, exit in room.exits.items():
            next_room_uid = exit.to_room
            # Search for the next room to position it nearby in the grid
            next_room = next((r for r in self.rooms if r.uid == next_room_uid), None)
            if not next_room:
                print(f"Warning: Room with UID '{next_room_uid}' not found.")
                continue

            if next_room.uid not in visited:
                offset = self.direction_to_offset(direction)
                next_position = (position[0] + offset[0], position[1] + offset[1])
                # Recursively place the next room
                self._place_room(next_room, next_position, visited)

    def assign_positions(self):
        """Assign positions to all rooms using grid and compass directions."""
        start_room = self.rooms[0]
        self._place_room(start_room, (0, 0), set())

    def ensure_no_collisions(self):
        """Ensure there are no missing positions, using a structured grid."""
        missing_positions = [room.uid for room in self.rooms if room.uid not in self.positions]
        if missing_positions:
            print(f"Missing positions: {missing_positions}")
            for room_uid in missing_positions:
                existing_rooms = self.positions.values()
                for x, y in existing_rooms:
                    free_position = self.find_free_position((x, y))
                    if free_position:
                        self.positions[room_uid] = free_position
                        self.grid[free_position] = room_uid
                        break

    def find_free_position(self, position):
        """Find the first available adjacent position."""
        for direction, (dx, dy) in self.compass_directions.items():
            possible = (position[0] + dx, position[1] + dy)
            if possible not in self.grid:
                return possible
        return None

    def get_positions(self):
        """Return the calculated positions (useful for other components)."""
        return self.positions
