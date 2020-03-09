from dataclasses import InitVar, dataclass
from typing import List

from minizinc import Instance, Model, Solver

cbc = Solver.lookup("gurobi")
model = Model()
model.add_file("./models/mapping.mzn")

inst = Instance(cbc, model)
inst.add_file("./models/full2x2_mp3.dzn")

result = inst.solve()
sol = result.statistics
print(result.solution)
print(sol["flatTime"])
print(sol["solveTime"])
print(sol["time"])
