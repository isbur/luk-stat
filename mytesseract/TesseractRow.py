import cv2
from copy import deepcopy
from typing import Any, overload, TYPE_CHECKING
from .Geometry import Rectangle
# Imported one more time after TesseractRow definition to avoid circular import
if  TYPE_CHECKING:
    from .TesseractRowList import TesseractRowList, TesseractRow


class TesseractRowProto:

    # As stated in Tesseract TSV documentation
    # https://www.tomrochette.com/tesseract-tsv-format
    @overload
    def __init__(self, level: int,page_num: int,block_num: int,par_num: int,line_num: int,word_num: int,x: int,y: int,w: int,h: int,conf:float,text:str,src:'TesseractRowList'): ...

    @overload
    def __init__(self, level: int,page_num: int,block_num: int,par_num: int,line_num: int,word_num: int,x: int,y: int,w: int,h: int,conf:float,text:str): ...

    def __init__(self, level: int,page_num: int,block_num: int,par_num: int,line_num: int,word_num: int,x: int,y: int,w: int,h: int,conf:float,text:str, src=None):
        
        default_members = deepcopy(list(self.__dict__.items()))

        self.level: int = level
        self.page_num: int = page_num
        self.block_num: int = block_num
        self.par_num: int = par_num
        self.line_num: int = line_num
        self.word_num: int = word_num
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h
        self.conf: float = conf
        self.text: str = text

        self.obligatory_members: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if key == "obligatory_members":
                continue
            if key not in default_members:
                self.obligatory_members[key] = value

        self.src: TesseractRowList|None = src
        self.marked_as_detached = False

    def __repr__(self) -> str:
        if self.isword():
            return f"TesseractRow(text=\"{self.text}\",{self.getRect()})"
        else:
            return f"TesseractRow({self.getRect()})"
    
    def __contains__(self, r: 'TesseractRow') -> bool:
        return r.getRect() in self.getRect()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TesseractRowProto):
            return NotImplemented
        else:
            return all(value == other.__dict__[key] for key, value in self.__dict__.items() if key in self.obligatory_members)

    def ispage(self) -> bool:
        return self.level == 1

    def isblock(self) -> bool:
        return self.level == 2

    def ispar(self) -> bool:
        return self.level == 3
        
    def isline(self) -> bool:
        return self.level == 4
    
    def isword(self) -> bool:
        return self.level == 5
    
    def assertEpsilon(self) -> int:
        src = self.assert_src()
        return src.getMedianLineHeight()
    
    def isNear(self, r: 'TesseractRow', how: str | None = None, epsilon: int | None = None) -> bool:
        if epsilon is None:
            epsilon = self.assertEpsilon()
        return self.getRect().isNear(r.getRect(), how, epsilon)

    def assert_src(self, src = None):
        if src is None and self.src is None:
            raise Exception("Both internal and passed with arguments TessractRowList's are not set")
        if src is None:
            src = self.src
        if len(src) == 0:
            raise Exception("Source list of TesseractRows is empty.")
        return src
    
    @overload
    def getParent(self, src: 'TesseractRowList') -> 'TesseractRow': ...

    @overload
    def getParent(self) -> 'TesseractRow': ...

    def getParent(self, src = None) -> 'TesseractRow':

        src = self.assert_src(src)

        if len(src) == 0:
            raise Exception("Source list of TesseractRows is empty.")
        
        a: TesseractRow | None = None
        for r in src:
            if self.isword() and r.isline() and r.block_num == self.block_num and r.par_num == self.par_num and r.line_num == self.line_num:
                a = r
                break
            elif self.isline() and r.ispar() and r.block_num == self.block_num and r.par_num == self.par_num:
                a = r
                break
        
        if a is None:
            raise Exception("No parent is found")
        
        return a
        
    def getRect(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.x + self.w, self.y + self.h)
    
    #### TODO Too ineffective implementation
    def next(self) -> 'TesseractRow':
        parent = self.getParent()
        siblings = parent.getChildren()
        result = None
        for i, s in enumerate(siblings):
            if s == self:
                if i == len(siblings) - 1:
                    raise Exception("It's the last sibling")
                else:
                    result = siblings[i+1]
        if result is None:
            raise Exception("No sibling found")
        else:
            return result

    def setRect(self, rect: Rectangle):
        self.x = rect.A.x
        self.y = rect.A.y
        self.w = rect.getW()
        self.h = rect.getH()
    
    def show(self, img, color: tuple[int,int,int] = (0,255,0)):
        self.getRect().show(img, color)

