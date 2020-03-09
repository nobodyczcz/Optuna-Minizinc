import sys

sys.path.append("../")

from OptunaMinizinc.Tuning import Tuning
from minizinc import Model, Solver, Instance

tuning = Tuning()

cbc = Solver.lookup("osicbc")
model = Model()
model.add_file("./models/mapping.mzn")

instance = Instance(cbc, model)
instance.add_file("./models/full2x2_mp3.dzn")

tuning.load_instance(instance)
tuning.load_param_from_pcs_file("../pcsFiles/osicbc.json")

params = tuning.start(n_trials=50)
print(params)
