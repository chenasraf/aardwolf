import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle

class GraphRenderer:
    def __init__(self, rooms, exits, positions):
        self.rooms = rooms
        self.exits = exits
        self.positions = positions
        self.graph = nx.DiGraph()

    def generate_graph(self):
        """Generate a NetworkX graph from rooms and exits."""
        for room in self.rooms:
            self.graph.add_node(room.uid, label=room.name, area=room.area)

        for exit in self.exits:
            self.graph.add_edge(exit.from_room, exit.to_room, direction=exit.direction)

    def draw_graph(self):
        """Draw the graph using matplotlib, with rectangular room nodes."""
        rect_width = 0.8
        rect_height = 0.4

        labels = nx.get_node_attributes(self.graph, 'label')
        pos = self.positions  # Pre-calculated positions

        # Draw edges
        valid_edges = [edge for edge in self.graph.edges if edge[0] in pos and edge[1] in pos]
        plt.figure(figsize=(10, 10))
        nx.draw_networkx_edges(self.graph, pos, edgelist=valid_edges, edge_color='gray')

        # Draw rectangular nodes
        ax = plt.gca()
        for node, (x, y) in pos.items():
            room = next((r for r in self.rooms if r.uid == node), None)
            color = 'lightblue' if not room.data.get('outside', False) else 'lightcoral'
            rect = Rectangle((x - rect_width / 2, y - rect_height / 2), rect_width, rect_height,
                             facecolor=color, edgecolor="black")
            ax.add_patch(rect)
            label = labels.get(node, node)
            ax.text(x, y, label, verticalalignment='center', horizontalalignment='center', fontsize=10)

        plt.axis("equal")
        plt.autoscale()
        plt.show()
