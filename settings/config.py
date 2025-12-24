import json
from typing import Dict, List
from .settings import Settings

class Rule:

    def __init__(self,capacity:int,rate:float) -> None:
        self._capacity = capacity
        self._rate = rate

    @property
    def capacity(self) -> int:
        return self._capacity
    
    @property
    def rate(self) -> float:
        return self._rate

class Config:

    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Config()
        return cls._instance

    def __init__(self) -> None:
        data:dict | None = None
        with open(Settings.get_instance().JSON_CONFIG_FILE,'r') as f:
            data = json.loads(f.read())
        if not data:
            raise ValueError()
        self._rules:Dict[str,Rule] = {rule:Rule(value['capacity'],value['rate']) for rule,value in data['rules_def'].items()}
        self._cleanup_interval:int = data['cleanup_interval']
        self._endpoints:Dict[str,List[str]] = data['endpoints']
        self._operations_cost_factors:Dict[str,float] = data['operations_costs_factors']
        self._operations_costs:Dict[str,float] = data['operations_costs']

    @property
    def operations_costs(self) -> Dict[str,float]:
        return self._operations_costs

    @property
    def operations_costs_factors(self) -> Dict[str,float]:
        return self._operations_cost_factors

    @property
    def rules(self) -> Dict[str,Rule]:
        return self._rules
    
    @property
    def cleanup_interval(self) -> int:
        return self._cleanup_interval
    
    @property
    def endpoints(self) -> Dict[str,List[str]]:
        return self._endpoints