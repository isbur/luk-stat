import json
from config import workdir, number


problem_ranges: dict[int, tuple[int, int]] = {}
# for i in range(1, 2):
for i in range(1, number + 1):
    problem_ranges[i] = (0, 0)

json_object = json.dumps(problem_ranges, indent=4)
with open(f"{workdir}/problem_ranges.json", "w") as outfile:
    outfile.write(json_object)
