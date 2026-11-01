"""Instructor tool: rebuilds labs/ from solutions/ after you edit a solution.

The code between "# TODO" and "# END TODO" is removed for students. The hint comments
stay. Each gap stops the script with a clear message until the student fills it in.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
(ROOT / "labs").mkdir(exist_ok=True)

for solution in sorted((ROOT / "solutions").glob("lab*.py")):
    output, in_todo, in_answer, number = [], False, False, None
    for line in solution.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        indent = line[: len(line) - len(line.lstrip())]
        todo = re.match(r"# TODO (\d+):", stripped)
        if todo:
            number, in_todo, in_answer = todo.group(1), True, False
        elif stripped == "# END TODO":
            in_todo = False
            continue
        if in_todo and not (todo or (stripped.startswith("#") and not in_answer)):
            if not in_answer:  # first line of the answer: put the gap here
                output.append(f'{indent}raise SystemExit("TODO {number}: replace this line with your code")')
                in_answer = True
            continue
        output.append(line)
    (ROOT / "labs" / solution.name).write_text("\n".join(output) + "\n", encoding="utf-8")
    print("Built", solution.name)
