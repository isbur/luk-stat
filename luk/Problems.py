import statistics
from typing import Iterator, overload
from .mytesseract.TesseractRowList import TesseractRowList
from .Problem import Problem


#### TODO сделать дженерик? чтобы можно было указывать подкласс Problem: LukProblem, AtanProblem
class Problems:

    def __init__(self, problems: list[Problem], src: TesseractRowList):

        self.problems: list[Problem] = problems
        self.src: TesseractRowList = src
    
    def __iter__(self) -> Iterator[Problem]:
        return self.problems.__iter__()
    
    @overload
    def __getitem__(self, index: int) -> Problem: ...

    @overload
    def __getitem__(self, index: slice) -> 'Problems': ...

    def __getitem__(self, index: int | slice) -> 'Problem | Problems':
        subproblems = self.problems.__getitem__(index)
        if isinstance(subproblems, list):
            return Problems(subproblems, self.src)
        else:
            return subproblems
    
    def __setitem__(self, index: int, value: Problem):

        self.problems[index] = value
    
    def __len__(self) -> int:

        return len(self.problems)
    
    def __repr__(self) -> str:

        return self.problems.__repr__()
    
    def append(self, item: Problem):

        self.problems.append(item)

    
    def check_sequence(self) -> bool:
        A = [p.number for p in self.problems]
        A.sort()
        answer = True
        for i, n in enumerate(A):
            if i == len(A) - 1:
                continue
            if (A[i + 1] - n) != 1:
                answer = False
                break
        return answer
    
    def truncateNumbers(self):
        if any(0 < p.number < 100 for p in self.problems):
            raise Exception("Detected 1 or 2-digital numbers, not tested yet")
        elif list(p.number >= 1000 for p in self.problems).count(True) > 3:
            raise Exception("Detected more than one 4-digital number, you need to manually investigate this page and possibly comment out this 'elif' branch")
        median_str_len = int(statistics.median(len(str(p.number)) for p in self.problems))
        for p in self.problems:
            p.number = int(str(p.number)[:median_str_len])