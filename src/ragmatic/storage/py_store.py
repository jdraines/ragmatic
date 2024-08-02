import pickle
from joblib import Parallel, delayed
import difflib
import typing as t
import re

from .bases import MetadataStore
from ..code_analysis.metadata_units.bases import ModuleData


PARALLELIZATION_THRESHOLD = 1_000


class MapOp:
    def __init__(self, config):
        pass
    def map(self, callable, inputs_iterable):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass


class NoMap(MapOp):
    def map(self, callable, inputs_iterable):
        return [callable(*i) for i in inputs_iterable]


class JoblibParallelMap(MapOp):

    def __init__(self, config):
        self.config = config
        self.parallel = None

    def map(self, callable, inputs_iterable):
        with self.parallel as parallel:
            return parallel(delayed(callable)(*i) for i in inputs_iterable)

    def __enter__(self):
        self.parallel = Parallel(**self.config)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.parallel = None



class PyStore(MetadataStore):

    store_name = 'python'
    _allowed_query_keys = [
        "name",
        "imports",
        "classes",
        "metrics.instability",
        "metrics.abstractness",
        "metrics.distance_from_main",
        r"classes.{*}.methods",
        r"classes.{*}.methods.{*}.return_type",
        r"classes.{*}.bases",
        r"classes.{*}.metrics.CBO",
        r"classes.{*}.metrics.DIT",
        r"classes.{*}.metrics.Ce",
        r"classes.{*}.metrics.Ca",
        r"classes.{*}.metrics.LCOM4",
        r"classes.{*}.is_abstract",
        r"functions.{*}.metrics.cyclomatic_complexity",
        r"functions.{*}.return_type",
    ]
    _operators = {
        "eq": lambda x, y: x == y,
        "ne": lambda x, y: x != y,
        "gt": lambda x, y: x > y,
        "lt": lambda x, y: x < y,
        "gte": lambda x, y: x >= y,
        "lte": lambda x, y: x <= y,
        "countEq": lambda x, y: len(x) == y,
        "countNe": lambda x, y: len(x) != y,
        "countGt": lambda x, y: len(x) > y,
        "countLt": lambda x, y: len(x) < y,
        "countGte": lambda x, y: len(x) >= y,
        "countLte": lambda x, y: len(x) <= y,
        "in": lambda x, y: x in y,
        "nin": lambda x, y: x not in y,
        "regex": lambda x, y: bool(re.match(y, x)),
    }

    _collection_operators = [
        "countEq",
        "countNe",
        "countGt",
        "countLt",
        "countGte",
        "countLte",
        "in",
        "nin",
    ]

    _default_filepath = "data.pkl"

    def __init__(self, config):
        self.config = config
        self.always_parallel = config.get("always_parallel", False)
        self.filepath = config.get("filepath", self._default_filepath)
        self.__data = None

    @property
    def _data(self):
        if self.__data is None:
            self._load_module_data()
        return self.__data
    
    def get_mapper(self):
        if len(self._data) > PARALLELIZATION_THRESHOLD or self.always_parallel:
            return JoblibParallelMap({"n_jobs": -1})
        return NoMap({})

    def store_all_module_data(self, modules: dict[str, ModuleData]):
        if self.__data is None:
            self.__data = {}
        for _, module_data in modules.items():
            self.store_module_data(module_data)

    def store_module_data(self, module_data: ModuleData):
        if self.__data is None:
            self._load_module_data()
        self.__data[module_data.name] = module_data
        with open(self.filepath, "wb") as f:
            pickle.dump(self._data, f)
    
    def _load_module_data(self):
        try:
            with open(self.filepath, "rb") as f:
                self.__data = pickle.load(f)
        except FileNotFoundError:
            self.__data = {}

    def query_modules(self, query: list[tuple[str, str, t.Any]]):
        query_ops = []
        for line in query:
            self._validate_query_line(line)
            query_ops.append(line)
        first_op = query_ops[0]
        results = self._apply_query_op(first_op)
        if len(query_ops) == 1:
            return results
        for op in query_ops[1:]:
            results = results.intersection(self._apply_query_op(op))
        return results

    def _validate_query_line(self, query_line: tuple[str, str, t.Any]):
        key, op, value = query_line
        self._validate_query_key(key)
        self._validate_operator(op)
    
    def _extract_value_from_key(self, key, module_data: ModuleData):
        keyparts = key.split(".")
        return module_data.name, self._extract_value_from_keyparts(keyparts, module_data)

    def _extract_value_from_keyparts(self, keyparts, obj):
        value = obj
        for i, keypart in enumerate(keyparts):
            if keypart == "{*}":
                value = [
                    self._extract_value_from_keyparts(keyparts[i+1:], _v)
                    for _, _v in value.items()
                ]
                break
            elif hasattr(value, keypart):
                value = getattr(value, keypart)
            elif hasattr(value, "__getitem__") and keypart in value:
                value = value[keypart]
            else:
                raise ValueError(f"Key {keypart} not found in object")
        return self._flatten(value)

    def _flatten(self, value: t.Union[t.Any, t.List[t.Any], t.List[t.List[t.Any]]]):
        if isinstance(value, (list, dict, tuple)):
            new_value = []
            for v in value:
                if isinstance(v, (list, dict, tuple)):
                    new_value.extend(self._flatten(v))
                else:
                    new_value.append(v)
            return new_value
        return value
    
    def _validate_query_key(self, key):
        if key not in self._allowed_query_keys:
            suggested_keys = difflib.get_close_matches(key, self._allowed_query_keys)
            if suggested_keys:
                raise ValueError(f"Query key {key} not allowed. Did you mean one of these: {suggested_keys}")
            else:
                raise ValueError(f"Query key {key} not allowed")

    def _validate_operator(self, operator):
        if operator not in self._operators:
            suggested_ops = difflib.get_close_matches(operator, self._operators.keys())
            if suggested_ops:
                raise ValueError(f"Query operator {operator} not allowed. Did you mean one of these: {suggested_ops}")
            else:
                raise ValueError(f"Query operator {operator} not allowed")

    def _apply_query_op(self, query_op: tuple[str, str, t.Any]):
        key, op, value = query_op
        with self.get_mapper() as mapper:
            output_values = dict(mapper.map(self._extract_value_from_key, [(key, m) for m in self._data.values()]))
            output_results = dict(
                mapper.map(
                    self._apply_operator, 
                    [(module_name, op, value, mod_value) for module_name, mod_value in output_values.items()]
                )
            )
        return {k for k,v in output_results.items() if v}
    
    def _apply_operator(self, module_name, operator, value, mod_value):
        
        if isinstance(mod_value, list):
            if operator in self._collection_operators:
                return module_name, self._operators[operator](mod_value, value)
            else:
                if len(mod_value) == 0:
                    return module_name, False
                return module_name, all([self._operators[operator](m, value) for m in mod_value])
        else:
            return module_name, self._operators[operator](mod_value, value)

    def get_module(self, module_name: str):
        return self._data.get(module_name)
