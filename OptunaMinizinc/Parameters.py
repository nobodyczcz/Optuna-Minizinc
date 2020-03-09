import sys, os, re, time, json
from subprocess import Popen, PIPE, TimeoutExpired
from random import randint
from abc import ABC, abstractmethod
from typing import Optional


class Parameters(ABC):
    """
    The abstrac representation of parameter classes
    """
    parameter_space = {}

    def __init__(self):
        super().__init__()
        return

    @classmethod
    def load_param_from_pcs_file(cls, pcs_path):
        with open(pcs_path) as file:
            params = json.load(file)
        if params["name"] == "gurobi":
            instance = GurobiParam()
        elif params["name"] == "cplex":
            instance = CplexParam()
        elif params["name"] == "osicbc":
            instance = OsicbcParam()
        else:
            raise Exception("Do not support solver: " + params["name"])
        instance.parameter_space = params
        return instance

    def suggest_params(self, trial):
        params = {}
        for key, value in self.parameter_space["parameters"].items():
            use_default = trial.suggest_categorical(key + "##use_default", [True, False])
            if use_default:
                params[key] = value["default"]

            else:
                if value["type"] == "integer":
                    params[key] = trial.suggest_int(key, value["range"][0], value["range"][1])

                if value["type"] == "ordinal":
                    params[key] = trial.suggest_categorical(key, value["range"])

                if value["type"] == "categorical":
                    params[key] = trial.suggest_categorical(key, value["range"])

                if value["type"] == "real":
                    params[key] = trial.suggest_uniform(key, value["range"][0], value["range"][1])
        return params

    def extract_json_objects(self, text, decoder=json.JSONDecoder()):
        """Find JSON objects in text, and yield the decoded JSON data

        Does not attempt to look for JSON arrays, text, or other JSON types outside
        of a parent JSON object.

        """
        pos = 0
        while True:
            match = text.find('{', pos)
            if match == -1:
                break
            try:
                result, index = decoder.raw_decode(text[match:])
                if len(result) >= 1:
                    yield result
                pos = match + index
            except ValueError:
                pos = match + 1

    def get_current_timestamp(self):
        '''
        Get current timestamp
        '''
        return time.strftime('[%Y%m%d%H%M%S]', time.localtime(time.time()))

    @abstractmethod
    def process_param(self, params, outputdir=None, randomSeed=None):
        pass

    def generate_param_args(self, params):
        param_string = self.process_param(params)

        args = {'readParam': param_string}

        return args


class CplexParam(Parameters):
    """
    Process cplex parameters
    """

    def __init__(self):
        super().__init__()
        self.param_in_file = True

    def process_param(self, params, outputdir=None, randomSeed=None):
        # Prepare temp parameter file
        tempParam = 'CPLEX Parameter File Version 12.6\n'
        for name, value in params.items():
            if name == 'MinizincThreads':
                self.threads = value
            else:
                tempParam += str(name) + '\t' + str(value) + '\n'
        if randomSeed is not None:
            tempParam += "CPX_PARAM_RANDOMSEED" + '\t' + str(randomSeed) + '\n'
        if outputdir is not None:
            paramfile = outputdir + "cplex_cfg"
        else:
            paramfile = self.get_current_timestamp() + str(randint(1, 999999))
        with open(paramfile, 'w') as f:
            f.write(tempParam)
        return paramfile


class OsicbcParam(Parameters):
    """
    process osicbc params
    """

    def __init__(self):
        super().__init__()
        self.param_in_file = False

    def process_param(self, params, outputdir=None, randomSeed=None):
        # Prepare temp parameter file
        tempParam = ''
        for name, value in params.items():
            if name == 'MinizincThreads':
                self.threads = value
            else:
                tempParam += ' -' + str(name) + ' ' + str(value)
        if randomSeed is not None:
            tempParam += ' ' + '-RandomC' + ' ' + str(randomSeed)

        if outputdir is not None:
            with open(outputdir + 'cbc_cfg', 'w') as f:
                f.write(tempParam)
        return tempParam

    def generate_param_args(self, params):
        param_string = self.process_param(params)
        args = {'cbcArgs': param_string}

        return args


class GurobiParam(Parameters):
    """
    Process gurobi params
    """

    def __init__(self):
        super().__init__()
        self.param_in_file = True

    def process_param(self, params, outputdir=None, randomSeed=None):
        # Prepare temp parameter file
        tempParam = '# Parameter Setting for Gruobi\n'
        for name, value in params.items():
            if name == 'MinizincThreads':
                self.threads = value
            else:
                tempParam += str(name) + '\t' + str(value) + '\n'
        if randomSeed is not None:
            tempParam += "Seed" + '\t' + str(randomSeed) + '\n'
        if outputdir is not None:
            paramfile = outputdir + "gurobi_cfg"
        else:
            paramfile = self.get_current_timestamp() + str(randint(1, 999999))
        with open(paramfile, 'w') as f:
            f.write(tempParam)
        return paramfile
