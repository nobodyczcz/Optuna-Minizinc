from abc import ABC, abstractmethod
from typing import Optional
from .Parameters import *
from datetime import timedelta

from minizinc import Instance, Model, Solver, error
import optuna


class BaseTuning(ABC):
    """
    Abstract representation of a tuning job
    """
    instances = []
    parameter_space: Parameters = None

    @abstractmethod
    def __init__(self):
        super().__init__()


class Tuning(BaseTuning):
    """
    Representation of a tuning job.
    """

    def __init__(self):
        super().__init__()

    def load_instance(self, instance: Instance):
        """
        Add minizinc instance to instance list.
        :param instance:
        :return:
        """
        self.instances.append(instance)

    def load_param_from_pcs_file(self, pcs_path):
        """
        load pcs file and set parameter space
        :param pcs_path:
        :return:
        """
        self.parameter_space = Parameters.load_param_from_pcs_file(pcs_path)

    def minimize_time_objective(self, trial):
        params = self.parameter_space.suggest_params(trial)
        param_args = self.parameter_space.generate_param_args(params)
        print(param_args)

        total_time = timedelta()
        for instance in self.instances:
            result = instance.solve(**param_args);
            solve_time = result.statistics["solveTime"]
            total_time += solve_time
        print("Finish a run")
        return total_time.total_seconds()

    def start(self,
              n_trials: Optional[int] = None,
              timeout: Optional[int] = None):
        study = optuna.create_study()
        study.optimize(self.minimize_time_objective, n_trials=n_trials, timeout=timeout, catch=(error.MiniZincError,))
        return study.best_params
