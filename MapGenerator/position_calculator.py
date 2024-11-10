from room import Room

class PositionCalculator:
    compass_directions = {
        'n': (0, 1),   # Move up
        's': (0, -1),  # Move down
        'e': (1, 0),   # Move right
        'w': (-1, 0),  # Move left
        'ne': (1, 1),  # Diagonal top-right
        'nw': (-1, 1), # Diagonal top-left
        'se': (1, -1), # Diagonal bottom-right
        'sw': (-1, -1) # Diagonal bottom-left
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
                print(f"Warning: Room with UID '{next_room_uid}' not found. Adding a stub room.")
                # Create a stub room with some default properties
                stub_room = Room(uid=next_room_uid, name=f"Outside ({next_room_uid})",
                                 area=0, notes="This is a placeholder room", data={"outside": True})
                self.rooms.append(stub_room)
                next_room = stub_room

            # If the room is not in the visited set, continue positioning
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
        """Ensure there are no missing positions, using row/column shifting to manage collisions."""
        missing_positions = [room.uid for room in self.rooms if room.uid not in self.positions]
        if missing_positions:
            print(f"Missing positions: {missing_positions}")

            for room_uid in missing_positions:
                placed = False
                # Attempt to find a free space around existing placed rooms
                for (x, y) in self.positions.values():
                    free_position = self.find_free_position((x, y))
                    if free_position:
                        print(f"Placing Room '{room_uid}' at position {free_position}")
                        self.positions[room_uid] = free_position
                        self.grid[free_position] = room_uid
                        placed = True
                        break

                # If no free space, we need to shift rows/columns to make space
                if not placed:
                    first_existing_room_pos = next(iter(self.positions.values()))  # Get any position from placed rooms
                    print(f"Shifting grid to make room for Room '{room_uid}'...")
                    self._shift_grid(room_uid, first_existing_room_pos)

    def _shift_grid(self, room_uid, conflict_position):
        """Shift an entire row/column in the grid to create space."""
        # Let's focus on shifting rows first (you can expand to columns similarly)
        x, y = conflict_position

        # Decide based on whether there is more space up or down the grid
        if (x, y + 1) not in self.grid:  # Try shifting down
            self._shift_row(y, 1)  # Shift all rooms at y or below by 1 unit downwards
            new_position = (x, y + 1)
        elif (x, y - 1) not in self.grid:  # Try shifting up
            self._shift_row(y, -1)  # Shift all rooms at y or above by 1 unit upwards
            new_position = (x, y - 1)
        else:
            new_position = None  # In case shifting is impossible (fallback)

        if new_position is not None:
            print(f"Room '{room_uid}' moved to: {new_position}")
            self.positions[room_uid] = new_position
            self.grid[new_position] = room_uid
        else:
            print(f"Warning: Room '{room_uid}' could not find space after row shifting!")

    def _shift_row(self, y, shift_val):
        """Helper function to shift a row of rooms up or down in the grid."""
        # Gather all rooms in the row to be shifted
        row_rooms = {(x, ry): node for (x, ry), node in list(self.grid.items()) if ry >= y} if shift_val > 0 \
            else {(x, ry): node for (x, ry), node in list(self.grid.items()) if ry <= y}

        # Shift each room in the row by the shift_val
        for (x, old_y), node in row_rooms.items():
            new_position = (x, old_y + shift_val)
            self.grid[new_position] = node
            self.positions[node] = new_position
            del self.grid[(x, old_y)]  # Clear the old position in the grid

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
