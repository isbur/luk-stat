from cv2.typing import MatLike
import re
from typing import overload
from .mytesseract.Geometry import Rectangle
from .mytesseract.TesseractRowList import TesseractRowList, TesseractRow


class Problem:

    def default_init(self, number: int = -1, extra: bool = False) -> None:
        self.number: int = number
        self.extra: bool = extra
        self.rows: TesseractRowList = TesseractRowList()
        self.Rect: Rectangle | None = None
        self.statement_img: MatLike | None = None
    
    number_re_str = r'^\d{1,3}\S?[\.,]$'
    extra_number_prefix_re_str = r'^[дД]\.?$'

    def try_main_problem_init(self, row: TesseractRow, accum: TesseractRowList | None, median_indent: int = 0) -> bool:

        children = row.children
        if children is None:
            raise Exception("Row children are not initialized")
        epsilon = 4

        problem_number_match = re.match(Problem.number_re_str, children[0].text)
        if problem_number_match is not None:
            problem_label = problem_number_match.group(0)
            replaces: dict[str,str] = {
                ".": "",
                ",": "",
                "°": "",
                "*": "",
                "Ю": "1",
                "%": "",
                ")": "",
            }
            for key, value in replaces.items():
                problem_label = problem_label.replace(key, value)

            
            if accum is not None and len(accum) > 0:
                # print("#" * 40)
                # print(problem_label)
                # print(accum)
                # print(row)
                real_indent = row.getRect().x - accum[-1].getRect().x
                # print(real_indent, median_indent)
                if median_indent - epsilon < real_indent < median_indent + epsilon or abs(real_indent) > 2 * median_indent:
                    pass
                else:
                    return False

            self.default_init(int(problem_label))
            return True
        return False
    
    def try_extra_problem_init(self, row: TesseractRow) -> bool:
        
        children = row.children
        if children is None:
            raise Exception("Row children are not initialized")

        if len(children) > 1:
            d_literal_match = re.match(Problem.extra_number_prefix_re_str, children[0].text)
            extra_problem_number_match = re.match(Problem.number_re_str, children[1].text)
            if d_literal_match is not None and extra_problem_number_match is not None:
                problem_label = extra_problem_number_match.group(0)
                problem_label = problem_label.replace(".", "")
                self.default_init(int(problem_label), True)
                return True
        
        return False

    def tess_init(self, row: TesseractRow, accum: TesseractRowList | None = None, indent: int = 0) -> None:

        children = row.children
        if children is None:
            raise Exception("Row children are not initialized")
        if children[0].marked_as_detached:
            self.default_init()
            return
        
        if not self.try_main_problem_init(row, accum, indent):
            if not self.try_extra_problem_init(row):
                self.default_init()


    @overload
    def __init__(self, number: int = 0, extra: bool = False): ...

    @overload
    def __init__(self, number: TesseractRow): ...

    @overload
    def __init__(self, number: TesseractRow, extra: TesseractRowList, indent: int): ...

    def __init__(self, number: int | TesseractRow = 0, extra: bool | TesseractRowList = False, indent:int = 0) -> None:
        if isinstance(number, int) and isinstance(extra, bool):
            self.default_init()
        elif isinstance(number, TesseractRow) and extra == False:
            self.tess_init(number)
        elif isinstance(number, TesseractRow) and isinstance(extra, TesseractRowList):
            self.tess_init(number, extra, indent)
        else:
            raise Exception("Unsupported operand types")
    
    def __repr__(self) -> str:
        return f"Problem № {"Д"*int(self.extra)+str(self.number)}"