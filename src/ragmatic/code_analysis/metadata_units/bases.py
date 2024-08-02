import typing as t
from abc import ABC, abstractmethod
import ast
from pydantic import BaseModel, Field


class StringTypes:
    ClassName = str
    FunctionName = str
    ModuleName = str

string = StringTypes


class FunctionMetrics(BaseModel):
    cyclomatic_complexity: t.Optional[int] = Field(default=None)


class FunctionData(BaseModel):
    params: t.Dict[str, str] = Field(default_factory=dict)
    return_type: t.Optional[str] = Field(default=None)
    calls: t.Set[string.FunctionName] = Field(default_factory=set)
    is_abstract: bool = False
    metrics: t.Dict[str, FunctionMetrics] = Field(default_factory=dict)
    call_types: t.List[str] = Field(default_factory=list)
    summary: t.Optional[str] = Field(default=None)
    docstring: t.Optional[str] = Field(default=None)


class ClassMetrics(BaseModel):
    CBO: t.Optional[int] = Field(default=None)  # Coupling between objects
    DIT: t.Optional[int] = Field(default=None)  # Depth of inheritance tree
    Ce: t.Optional[int] = Field(default=None)
    Ca: t.Optional[int] = Field(default=None)
    LCOM4: t.Optional[int] = Field(default=None)


class AttributeAccessData(BaseModel):
    getters: t.Set[string.FunctionName] = Field(default_factory=set)
    setters: t.Set[string.FunctionName] = Field(default_factory=set)
    deleters: t.Set[string.FunctionName] = Field(default_factory=set)
    public: t.Set[str] = Field(default_factory=set)
    non_public: t.Set[str] = Field(default_factory=set)


class ClassData(BaseModel):
    methods: t.Dict[string.FunctionName, FunctionData] = Field(default_factory=dict)
    bases: t.List[string.ClassName] = Field(default_factory=list)
    metrics: ClassMetrics = Field(default_factory=ClassMetrics)
    is_abstract: bool = False
    summary: t.Optional[str] = None
    docstring: t.Optional[str] = None
    attribute_access: AttributeAccessData = Field(default_factory=AttributeAccessData)
    type_info: t.Dict[str, str] = Field(default_factory=dict)


class ModuleMetrics(BaseModel):
    instability: t.Optional[float] = Field(default=None)
    abstractness: t.Optional[float] = Field(default=None)
    distance_from_main: t.Optional[int] = Field(default=None)


class ModuleData(BaseModel):
    name: str
    file_path: str
    imports: t.List[str] = Field(default_factory=list)
    classes: t.Dict[string.ClassName, ClassData] = Field(default_factory=dict)
    functions: t.Dict[string.FunctionName, FunctionData] = Field(default_factory=dict)
    summary: t.Optional[str] = Field(default=None)
    variables: t.Dict[str, str] = Field(default_factory=dict)
    metrics: ModuleMetrics = Field(default_factory=ModuleMetrics)
    pytree: t.Optional[ast.AST] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

class MetadataUnit(ABC):

    modules: t.Dict[string.ModuleName, ModuleData]

    @abstractmethod
    def __init__(self, modules: t.Dict[string.ModuleName, ModuleData]):
        pass

    @abstractmethod
    def analyze_file(self, module_data: ModuleData):
        pass

    @abstractmethod
    def get_data(self) -> t.Dict[string.ModuleName, ModuleData]:
        pass
