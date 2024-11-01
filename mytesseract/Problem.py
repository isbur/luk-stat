import re
from typing import overload
from .Geometry import Rectangle
from .TesseractRowList import TesseractRowList, TesseractRow


class Problem:

    def default_init(self, number: int = -1, extra: bool = False) -> None:
        self.number: int = number
        self.extra: bool = extra
        self.rows: TesseractRowList = TesseractRowList()
        self.Rect: Rectangle | None = None
    
    def tess_init(self, row: TesseractRow) -> None:
        children = row.getChildren()
        if children[0].marked_as_detached:
            self.default_init()
            return
        problem_number_re_str = r'\d{1,3}\S?.?'
        extra_problem_number_re_str = r'[дД]\.?'
        problem_number_match = re.match(problem_number_re_str, children[0].text)
        if problem_number_match is not None:
            problem_label = problem_number_match.group(0)
            problem_label = problem_label.replace(".", "")
            self.default_init(int(problem_label))
            return
        if len(children) > 1:
            d_literal_match = re.match(extra_problem_number_re_str, children[0].text)
            extra_problem_number_match = re.match(problem_number_re_str, children[1].text)
            if d_literal_match is not None and extra_problem_number_match is not None:
                problem_label = extra_problem_number_match.group(0)
                problem_label = problem_label.replace(".", "")
                self.default_init(int(problem_label), True)
                return
        self.default_init()

    @overload
    def __init__(self): ...

    @overload
    def __init__(self, number: int = -1, extra: bool = False): ...

    @overload
    def __init__(self, number: TesseractRow): ...

    def __init__(self, number: int | TesseractRow = -1, extra: bool = False) -> None:
        if isinstance(number, int) and isinstance(extra, bool):
            self.default_init()
        elif isinstance(number, TesseractRow):
            self.tess_init(number)
    
    def __repr__(self) -> str:
        return f"Problem № {"Д"*int(self.extra)+str(self.number)}"