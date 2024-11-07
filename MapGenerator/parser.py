from room import *
import json
import sqlite3

class MapParser:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.grid = []

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

    def parse_area(self, area):
        rooms = []
        exits = []
        for row in self._get_all_rooms(area):
            uid, name, area, *rdata = row
            data = dict(
                zip(
                    [
                        "building",
                        "terrain",
                        "info",
                        "notes",
                        "x",
                        "y",
                        "z",
                        "norecall",
                        "noportal",
                        "ignore_exits_mismatch",
                    ],
                    rdata,
                )
            )
            notes = data.pop("notes")

            room = Room(uid, name, area, notes, data)
            rooms.append(room)

        for room in rooms:
            rexits = self._get_exits_for_room(room.uid)
            for ex in rexits:
                direction, from_uid, to_uid, level = ex
                rexit = Exit(direction, from_uid, to_uid, level)
                room.add_exit(rexit.direction, rexit)
                exits.append(rexit)

        return rooms, exits

