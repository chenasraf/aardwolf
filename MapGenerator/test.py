from parser import MapParser
from position_calculator import PositionCalculator
from graph_renderer import GraphRenderer
import os
import json

if __name__ == "__main__":
    areas = os.sys.argv[1:]
    parser = MapParser("Aardwolf.db")
    out_dir = f"outputs"
    os.makedirs(out_dir, exist_ok=True)

    for area in areas:
        rooms, exits = parser.parse_area(area)
        # map_file = f"{out_dir}/{area}.txt"
        cache_file = f"{out_dir}/{area}.raw.json"
        with open(cache_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "rooms": [r.to_dict() for r in rooms],
                        "exits": [e.to_dict() for e in exits],
                    },
                    indent=4,
                )
            )
            print(f"Saved {cache_file}")

        calculator = PositionCalculator(rooms, exits)
        calculator.assign_positions()
        calculator.ensure_no_collisions()
        positions = calculator.get_positions()

        renderer = GraphRenderer(rooms, exits, positions)
        renderer.generate_graph()
        renderer.draw_graph()

