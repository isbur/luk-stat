from .Problems import Problems

class LukProblems(Problems):

    def splitMainExtra(self) -> tuple['LukProblems', 'LukProblems']:
        main = LukProblems([p for p in self.problems if not p.extra], self.src)
        extra = LukProblems([p for p in self.problems if p.extra], self.src)
        return (main, extra)
    