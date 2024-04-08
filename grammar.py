from dataclasses import dataclass, field
from typing import TypeAlias
import re

@dataclass(frozen=True)
class Terminal:
    pattern: str
    
    def match(self, token: str) -> bool:
        return re.match(f'^{self.pattern}$', token) is not None
    
    def __str__(self) -> str:
        return f'"{self.pattern}"'
        
Symbol: TypeAlias = str | Terminal

@dataclass(frozen=True)
class Rule:
    lhs: str
    rhs: tuple[Symbol, ...]

@dataclass
class Grammar:
    start_symbol: str
    rules: list[Rule]
    rule_map: dict[str, list[Rule]] = field(init=False)
    
    def __post_init__(self):
        self.rule_map = {}
        for rule in self.rules:
            self.rule_map.setdefault(rule.lhs, []).append(rule)
