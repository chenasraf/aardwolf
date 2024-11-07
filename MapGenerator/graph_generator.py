from room import *
import networkx as nx
import json
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class GraphGenerator:
    def __init__(self, rooms, exits):
        self.rooms = rooms
        self.exits = exits
        self.graph = nx.DiGraph()  # Directed graph to represent rooms/exits
        self.positions = {}  # To store the node positions for plotting

    def direction_to_offset(self, direction):
        """Convert a compass direction into an (x, y) offset for positioning."""
        compass = {
            "n": (0, 1),  # North -> +y
            "s": (0, -1),  # South -> -y
            "e": (1, 0),  # East -> +x
            "w": (-1, 0),  # West -> -x
            # "u": (1, 1),  # Up can be displayed with a slight y axis bump
            # "d": (1, -1),  # Down - slight y axis drop
            "u": (0, 0.5),  # Up can be displayed with a slight y axis bump
            "d": (0, -0.5),  # Down - slight y axis drop
        }
        angular_default = {"ne": (1, 1), "nw": (-1, 1), "se": (1, -1), "sw": (-1, -1)}
        # Assuming directions beyond 'n', 's', 'e', 'w', 'u', 'd'
        if direction in compass:
            return compass[direction]
        return angular_default.get(direction, (0, 0))  # Default for odd directions

    def assign_positions(self):
        """Assign positions to rooms recursively based on their exits."""
        # Start with the first room at (0, 0)
        start_room = self.rooms[0]
        self._place_room(start_room, (0, 0), set())

    def _place_room(self, room, position, visited):
        """Place rooms recursively and assign positions based on their exits."""
        # If already positioned, return (to avoid cyclic references)
        if room.uid in self.positions:
            return

        # Assign the position for the current room
        self.positions[room.uid] = position
        visited.add(room.uid)

        # Explore each exit and assign the position of the connected room
        for direction, exit in room.exits.items():
            next_room_uid = exit.to_room

            # Search for the next room by UID
            next_rooms = [r for r in self.rooms if r.uid == next_room_uid]

            if not next_rooms:
                # Room is not found -- ignore the exit and continue
                print(
                    f"Warning: Room with UID '{next_room_uid}' not found. Ignoring this exit."
                )
                continue  # Move to the next exit

            # Since we found the room, continue placing it
            next_room = next_rooms[0]  # There should only be one room with this UID

            if next_room.uid not in visited:
                # Calculate the next room's coordinates based on the direction
                offset = self.direction_to_offset(direction)
                next_position = (position[0] + offset[0], position[1] + offset[1])

                # Recursively place the next room
                self._place_room(next_room, next_position, visited)

    def generate_graph(self):
        """Generate a NetworkX graph from rooms and exits."""
        # Add all rooms as nodes
        for room in self.rooms:
            self.graph.add_node(room.uid, label=room.name, area=room.area)

        # Add all exits as edges
        for exit in self.exits:
            self.graph.add_edge(
                exit.from_room, exit.to_room, direction=exit.direction, level=exit.level
            )

        # Assign positions to rooms based on their exits
        self.assign_positions()

    def draw_graph(self):
        """Draw the graph using rectangles for nodes, with compass-based spacing for missing nodes."""

        pos = self.positions  # Use pre-calculated positions
        labels = nx.get_node_attributes(self.graph, 'label')
        rect_width = 0.8   # Rectangle width for graph nodes
        rect_height = 0.4  # Rectangle height for graph nodes

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

        def find_free_position(existing_pos):
            """Find the closest available free position based on a compass direction."""
            for direction, (dx, dy) in compass_directions.items():
                new_pos = (existing_pos[0] + dx, existing_pos[1] + dy)
                # Check if this position is free (not occupied by any other node)
                if new_pos not in pos.values():
                    return new_pos
            return None  # No free position found in immediate compass directions

        # ---------------------
        # Step 1: Ensure all nodes have positions, using compass-based spacing
        # ---------------------
        missing_positions = [node for node in self.graph.nodes if node not in pos]

        if missing_positions:
            print(f"Warning: The following nodes do not have positions: {missing_positions}")

            for node in missing_positions:
                # Try to place near an existing node (first one in the list)
                for existing_node, existing_xy in pos.items():
                    free_pos = find_free_position(existing_xy)
                    if free_pos is not None:
                        pos[node] = free_pos
                        print(f"Node '{node}' assigned compass position near '{existing_node}': {free_pos}")
                        break
                # If none found near any nodes, apply some backup fallback strategy
                else:
                    # If could not find a position using compass within neighbors, place it far away
                    pos[node] = (random.uniform(-10, 10), random.uniform(-10, 10))
                    print(f"Node '{node}' could not find free compass position; assigned random position: {pos[node]}")

        # ---------------------
        # Step 2: Draw edges (only draw edges between nodes that both have positions)
        # ---------------------
        valid_edges = [(e[0], e[1]) for e in self.graph.edges if e[0] in pos and e[1] in pos]

        plt.figure(figsize=(10, 10))
        nx.draw_networkx_edges(self.graph, pos, edgelist=valid_edges, edge_color='gray')

        # ---------------------
        # Step 3: Draw rectangular nodes manually
        # ---------------------
        ax = plt.gca()  # Get the current axis
        for node, (x, y) in pos.items():
            rect = Rectangle((x - rect_width / 2, y - rect_height / 2), rect_width, rect_height,
                             facecolor='skyblue', edgecolor='black')
            ax.add_patch(rect)

            # Add the label inside the rectangle
            label = labels.get(node, node)
            ax.text(x, y, label, verticalalignment='center', horizontalalignment='center', fontsize=10)

        # ---------------------
        # Step 4: Display the graph
        # ---------------------
        ax.set_aspect('equal')
        plt.autoscale()  # Ensure everything fits in the plot from -10, 10 ranges.
        plt.show()
