from dataclasses import dataclass
from typing import Optional
import typer
import json

STAGGER = [0.2, 0.1, 0.0, 0.1, 0.2]
ROWS = 3
THUMB_ANGLES = [11.0, 22.0]
THUMB_ROW = 3
THUMB_COL = 4
THUMB_PIVOT = [3, 4]
# THUMB_SIZES = [0.7, 1.0]
THUMB_SIZES = [1.0, 1.0]


@dataclass
class Key:
    x: float = 0.0
    y: float = 0.0
    col: int = 0
    row: int = 0
    w: float = 1.0
    h: float = 1.0
    name: Optional[str] = None
    r: Optional[float] = None

    def to_obj(self):
        obj = {"x": self.x, "y": self.y, "col": self.col, "row": self.row}
        if self.name is not None:
            obj["name"] = self.name
        if self.w != 1.0:
            obj["w"] = self.w
        if self.h != 1.0:
            obj["h"] = self.h
        if self.r is not None:
            obj["r"] = self.r
            obj["rx"] = self.x + self.w / 2
            obj["ry"] = self.y + self.h / 2
        return obj

    def flip_x(self, flipx, col_off=12):
        return Key(
            x=flipx + (flipx - self.x),
            y=self.y,
            col=col_off + col_off - self.col,
            row=self.row,
            w=self.w,
            h=self.h,
            r=360.0 - self.r if self.r is not None else None,
        )

    def change(
        self, x=None, y=None, col=None, row=None, name=None, r=None, rx=None, ry=None
    ):
        _x = self.x
        _y = self.y
        _col = self.col
        _row = self.row
        _name = self.name
        _r = self.r

        if x is not None:
            _x = self.x + x
        if y is not None:
            _y = self.y + y
        if col is not None:
            _col = self.col + col
        if row is not None:
            _row = self.row + row
        if name is not None:
            _name = name
        return Key(x=_x, y=_y, col=_col, row=_row, name=_name, w=self.w, h=self.h, r=_r)


def central(stagger=STAGGER, rows=ROWS):
    return [
        Key(col=c, row=r, x=float(c), y=float(r + col))
        for r in range(rows)
        for (c, col) in enumerate(stagger)
    ]


def thumbs(start_col=THUMB_COL, angles=THUMB_ANGLES, row=ROWS + 1, sizes=THUMB_SIZES):
    return [
        Key(
            col=start_col + i,
            row=row,
            x=start_col + i + (1.0 - sizes[i]) / 2 - 0.25,
            y=THUMB_ROW + i * 0.2 + (1.0 - sizes[i]) / 2,
            r=a,
            w=sizes[i],
            h=sizes[i],
        )
        for (i, a) in enumerate(angles)
    ]


def rotenc():
    return [
        # Key(col=5, row=1, x=5.15, y=1.15, r=THUMB_ANGLES[-1], w=0.7, h=0.7)
        Key(col=5, row=1, x=5.15, y=1.15, r=THUMB_ANGLES[-1])
    ]


def joystick():
    return [
        Key(col=1, row=5, x=1.0, y=4.0),
        Key(col=0, row=6, x=0.0, y=5.0),
        Key(col=1, row=6, x=1.0, y=5.0),
        Key(col=2, row=6, x=2.0, y=5.0),
        Key(col=1, row=7, x=1.0, y=6.0),
    ]


def mirror(keys):
    return keys + [k.change(x=12.0, col=6).flip_x(12.0) for k in keys]


def keyboard(
    stagger=STAGGER, rows=ROWS, thumb_angles=THUMB_ANGLES, thumb_row=THUMB_ROW
):
    return mirror(central() + thumbs() + rotenc() + joystick())


def sensors():
    return [
        {
            "ref": "left_encoder",
            "name": "encoder_left",
            "identifier": "encoder_left",
            "compatible": "alps,ec11",
            "label": "LEFT_ENCODER",
        },
        {
            "ref": "right_encoder",
            "name": "encoder_right",
            "identifier": "encoder_right",
            "compatible": "alps,ec11",
            "label": "RIGHT_ENCODER",
        },
    ]


def main(stagger=STAGGER, rows=ROWS):
    skeleton = {
        "id": "2nd_ideal",
        "name": "2nd_ideal",
        "layouts": {
            "default_transform": {
                "2nd_ideal": "default_transform",
                "layout": [o.to_obj() for o in keyboard()],
                "sensors": sensors(),
            }
        },
    }
    print(json.dumps(skeleton))


if __name__ == "__main__":
    typer.run(main)
