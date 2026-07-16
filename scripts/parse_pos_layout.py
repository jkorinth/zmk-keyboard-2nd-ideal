from pathlib import Path
import typer
import re
import json


def parse(data):
    return [
        re.split(r"\s+", l)
        for l in data.splitlines()
        if not l.strip().startswith("#") and len(re.split(r"\s+", l)) > 4
    ]


def construct_keys(data):
    groups = {sw[-1] for sw in data}
    groups.add("joystick")

    def make_group(group):
        if group == "joystick":
            base_x = 2.0
            base_y = 3.5
            w = 0.5
            row = 4
            return [
                {
                    "name": "joy_l",
                    "x": base_x - w,
                    "y": base_y,
                    "w": w,
                    "h": w,
                    "row": row,
                    "col": 0,
                },
                {
                    "name": "joy_c",
                    "x": base_x,
                    "y": base_y,
                    "w": w,
                    "h": w,
                    "row": row,
                    "col": 1,
                },
                {
                    "name": "joy_r",
                    "x": base_x + w,
                    "y": base_y,
                    "w": w,
                    "h": w,
                    "row": row,
                    "col": 2,
                },
                {
                    "name": "joy_u",
                    "x": base_x,
                    "y": base_y - w,
                    "w": w,
                    "h": w,
                    "row": row,
                    "col": 3,
                },
                {
                    "name": "joy_d",
                    "x": base_x,
                    "y": base_y + w,
                    "w": w,
                    "h": w,
                    "row": row,
                    "col": 4,
                },
            ]
        else:
            switches = [
                sw for sw in data if re.match(r"SW_?\S*\d*", sw[0]) and sw[-1] == group
            ]
            if not switches:
                return []
            min_x = min([float(sw[3]) for sw in switches])
            min_y = min([-float(sw[4]) for sw in switches])

            def rowcol(name):
                s = name[2:]
                col = 0
                row = 0
                if s == "ROT1":
                    row = 2
                elif s == "13" or s == "17":
                    row = 3
                elif s.isdigit():
                    row = (int(s) - 1) % 3
                    col = (int(s) - 1) // 3
                return (col, row)

            for d in switches:
                print(d)
            return [
                {
                    "name": sw[0],
                    "x": (float(sw[3]) - min_x) / 19.05,
                    "y": (-float(sw[4]) - min_y) / 19.05,
                    # "r": 180.0 - float(sw[5]),
                    "row": rowcol(sw[0])[
                        0
                    ],  # (int(sw[0][2:]) - 1) % 3 if sw[0][2:].isdigit() else 0,
                    "col": rowcol(sw[0])[
                        1
                    ],  # (int(sw[0][2:]) - 1) // 3 if sw[0][2:].isdigit() else 0
                }
                for sw in switches
            ]

    def mod(key):
        if key["name"] == "SW_ROT1":
            key["w"] = 0.7
            key["h"] = 0.7
            key["x"] = key["x"] + key["w"] / 2
            key["y"] = key["y"] - key["h"] / 2

            if key.get("r"):
                key["r"] = key["r"] - 180.0
        elif key["name"] == "SW13":
            key["w"] = 0.7
            key["h"] = 0.7
            key["x"] = key["x"] + key["w"] / 2.0
            key["y"] = key["y"] + key["h"] / 2.0
        elif key["name"] == "SW17":
            key["x"] = key["x"] - key.get("w", 1.0) / 2
            key["y"] = key["y"] - key.get("h", 1.0) / 2

        return key

    lh = [mod(sw) for g in groups for sw in make_group(g)]
    return lh + mirror(lh)


def mirror(data):
    return [
        {
            "x": 14 - key["x"],
            "y": key["y"],
            "w": key.get("w", 1.0),
            "h": key.get("h", 1.0),
            "r": -key.get("r", 0.0),
            "col": key.get("col", 0) + 5,
            "row": key.get("row", 0),
        }
        for key in data
    ]


def write_json(data, filename, identifier, name, transform):
    out = {
        "id": identifier,
        "name": name,
        "layouts": {
            transform: {
                name: transform,
                "layout": [
                    sw  # { "row": 0, "col": 0, "x": sw["x"] / 19.05, "y": sw["y"] / 19.05, "r": sw["r"] }
                    for sw in data
                ],
            }
        },
    }
    with open(filename, "w+") as f:
        f.write(json.dumps(out))


def main(filename: Path):
    name = Path(filename).stem
    with open(filename, "r") as f:
        write_json(
            construct_keys(parse(f.read())),
            f"{name}.json",
            name,
            name,
            "default_transform",
        )


if __name__ == "__main__":
    typer.run(main)
