import statistics
import re
from typing import Any, Iterable, Iterator, SupportsIndex, overload
from .Geometry import Rectangle
from .TesseractRow import TesseractRowProto


class TesseractRow(TesseractRowProto):
    #### TODO Переписать, реализовав логику создания иерархии TesseractRows при инициализации TesseractRowsList списком
    @overload
    def getChildren(self, src: 'TesseractRowList') -> 'TesseractRowList': ...

    @overload
    def getChildren(self) -> 'TesseractRowList': ...

    def getChildren(self, src = None):
        
        src = self.assert_src(src)
        
        children = []
        if self.ispar():
            children = [r for r in src if r.level == 4 and r.par_num == self.par_num]
            raise Exception("Yet not implemented for paragraphs")
        elif self.isline():
            children = [r for r in src if r.level == 5 and r.page_num == self.page_num and r.block_num == self.block_num and r.par_num == self.par_num and r.line_num == self.line_num]
        else:
            raise Exception("Yet not implemented")
        return TesseractRowList(children)
    


class TesseractRowList(list):

    def __init__(self, *args: Iterable[TesseractRow] | dict[str, list[Any]] | None):
        if len(args) > 0 and args[0] is None: 
            super().__init__() 
        elif len(args) > 0 and isinstance(args[0], dict):
            d = args[0]
            n_boxes = len(d['level'])
            tesseract_rows = []
            for i in range(n_boxes):
                r = TesseractRow(d['level'][i],d['page_num'][i],d['block_num'][i],d['par_num'][i],d['line_num'][i],d['word_num'][i],d['left'][i],d['top'][i],d['width'][i],d['height'][i],d['conf'][i],d['text'][i],self)
                tesseract_rows.append(r)
            super().__init__(tesseract_rows)
        else:
            super().__init__(*args)
        if len([r for r in self if r.ispage()]) > 1:
            raise Exception("Tesseract detected that there are multiple pages in the image. Multipage functionality of mytesseract is not implemented yet, so please split the image into separate pages.")

    @overload
    def __getitem__(self, item: SupportsIndex) -> TesseractRow: ...

    @overload
    def __getitem__(self, item: slice) -> 'TesseractRowList': ...

    def __getitem__(self, item) -> 'TesseractRowList | TesseractRow':
        result = super().__getitem__(item)
        if isinstance(item, slice):
            result = TesseractRowList(result)
        return result
    
    def __iter__(self) -> Iterator[TesseractRow]:
        return super().__iter__()
    
    """
        Thin wrapper for built-in enumerate()
    """
    def enumerate(iterable: 'TesseractRowList', start: int = 0) -> Iterator[tuple[int, TesseractRow]]:
        return enumerate(iterable, start)

    def countWords(self) -> int:
        counter = 0
        for word in self:
            if re.match(r'[а-яА-Я]{3,20}', word.text):
                counter += 1
        return counter

    def envelope(self) -> Rectangle:
        x1: int = min(r.x for r in self)
        y1: int = min(r.y for r in self)
        x2: int = max(r.x + r.w for r in self)
        y2: int = max(r.y + r.h for r in self)
        return Rectangle(x1, y1, x2, y2)

    def find(self, s: str | TesseractRow) -> TesseractRow:
        if isinstance(s, str):
            for r in self:
                if r.isword() and s in r.text:
                    result = r
                    break
        elif isinstance(s, TesseractRow):
            candidates = [r for r in self if r == s]
            print(f"Экземпляров строки найдено: {len(candidates)}")
            result = candidates[0]
        else:
            raise Exception("Wrong 's' argument type.")
        return result
    
    # Забиваем на разбивку на блоки
    def getPars(self) -> 'TesseractRowList':
        return TesseractRowList(r for r in self if r.ispar() and r.page_num == 0)

    def getBlockLength(self) -> int:
        return len(self.getPars())
    
    def getLastPar(self) -> TesseractRow:
        return self.getPars()[-1]
    
    def getMedianLineHeight(self) -> int:
        return int(statistics.median(r.h for r in self if r.isline()))
    
    def getMedianSpaceLength(self) -> int:
        if not all(r in self[0].getParent().getChildren() for r in self):
            raise Exception("Похоже, TesseractRowList содержит более одной строки или вы пытаетесь применить метод к нестрокам.")
        elif len(self) == 1:
            raise Exception("Всего одно слово в строке, как тут определить интервал между словами?")
        return int(statistics.median(r.next().getRect().x - r.getRect().u for i, r in self.enumerate() if i != len(self) - 1))
    
    # WIP
    def tesscript(self, par_num: int, line_num: int = 0, word_num: int = 0) -> TesseractRow:
        filtered_by_par = [r for r in self if r.par_num == par_num]
        filtered_by_line = [r for r in filtered_by_par if r.line_num == line_num]
        filtered_by_word = [r for r in filtered_by_line if r.word_num == word_num]
        return filtered_by_word[0]
