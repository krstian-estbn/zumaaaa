from utils import overlap

def rect_overlap(ax: int, ay: int, ar: int,
                 bx: int, by: int, br: int) -> bool:
    return overlap((ax, ax + ar * 2), (bx, bx + br * 2)) and overlap(
        (ay, ay + ar * 2), (by, by + br * 2)
    )

def in_rect(x: float, y: float, rx: int, ry: int, size: int = 16) -> bool:
    return rx <= x <= rx + size and ry <= y <= ry + size