import cv2
from cv2.typing import MatLike
from typing import Final, overload


class Point:

    @overload
    def __init__(self, x: int, y: int): ...

    @overload
    def __init__(self, x: tuple[int, int]): ...
        
    def __init__(self, x: int|tuple[int,int], y:int|None=None):
        if y is None and isinstance(x, tuple):
            self.x, self.y = x
        elif isinstance(x, int) and isinstance(y, int):
            self.x = x
            self.y = y
        else:
            raise Exception("Unable to initialize Point")
    
    def __repr__(self):
        return f"({self.x}, {self.y})"


class Rectangle:

    #### TODO Добавить проверку положительной ориентированности
    def __init__(self, A:Point|int, B:Point|int, u: int|None = None, v: int|None = None):
        if u is None and v is None and isinstance(A, Point) and isinstance(B, Point):
            _A = A
            _B = B
            _x = A.x
            _y = A.y
            _u = B.x
            _v= B.y
        elif isinstance(A, int) and isinstance(B, int) and isinstance(u, int) and isinstance(v, int):
            _A = Point(A, B)
            _B = Point(u, v)
            _x = A
            _y = B
            _u = u
            _v = v
        else:
            raise Exception("Unable to initialize Rectangle")
        self.A: Final = _A
        self.B: Final = _B
        self.x: Final = _x
        self.y: Final = _y
        self.u: Final = _u
        self.v: Final = _v
    
    def __iter__(self):
        for x in (self.A.x, self.A.y, self.B.x, self.B.y):
            yield x

    def __repr__(self):
        return f"Rect(A:{self.A},B:{self.B})"
    
    def __contains__(self, rect: 'Rectangle') -> bool:
        return rect.x >= self.x and rect.y >= self.y and rect.u <= self.u and rect.v <= self.v
    
    # По умолчанию проверяет на пересечение с "расширенной" на epsilon версией другого прямоугольника
    def isNear(self, rect: 'Rectangle', how: str | None = None, epsilon: int | None = None) -> bool:
        if epsilon is None:
            raise Exception("'epsilon' is not set.")
        x, y, u, v = rect
        if how is None:
            x, y, u, v = x - epsilon, y - epsilon, u + epsilon, v + epsilon
        elif how == "vertically":
            x, y, u, v = x, y - epsilon, u, v + epsilon
        elif how == "horizontally":
            x, y, u, v = x - epsilon, y, u + epsilon, v
        else:
            raise Exception("Wrong 'how' parameter.")
        
        return self.x < u and self.u > x and self.y < v and  self.v > y

    def getW(self) -> int:
        return self.B.x - self.A.x

    def getH(self) -> int:
        return self.B.y - self.A.y
    
    def show(self, img: MatLike, color: tuple[int,int,int] = (0,255,0)):
        cv2.rectangle(img, (self.A.x, self.A.y), (self.B.x, self.B.y), color, 2)