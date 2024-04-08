from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Sequence

from grammar import Grammar, Rule, Symbol, Terminal

@dataclass(frozen=True)
class Node:
    symbol: Symbol
    children: list[Node] = field(default_factory=tuple)
    
    def __str__(self) -> str:
        return str(self.symbol) + ' -> ' + ' '.join(str(child) for child in self.children)

@dataclass(frozen=True)
class State:
    dot_pos: int
    start: int
    rule: Rule
    
    def __str__(self) -> str:
        dot = '•'
        symbols = []
        for i in range(len(self.rule.rhs)):
            if i == self.dot_pos:
                symbols.append(dot)
            symbols.append(self.rule.rhs[i])
        if self.dot_pos == len(self.rule.rhs):
            symbols.append(dot)
        return f'{self.rule.lhs}\t-> {" ".join(str(s) for s in symbols)} ({self.start})'
    
    def advance(self) -> State:
        return State(self.dot_pos + 1, self.start, self.rule)
    
    def is_complete(self) -> bool:
        return self.dot_pos == len(self.rule.rhs)
    
    def peek(self) -> Symbol | None:
        if self.dot_pos >= len(self.rule.rhs):
            return None
        return self.rule.rhs[self.dot_pos]
    
    def is_next_terminal(self) -> bool:
        return isinstance(self.peek(), Terminal)

@dataclass
class Column:
    index: int
    states: list[State]
    token: str
    state_set: set[State] = field(init=False)
    
    def __post_init__(self):
        self.state_set = set(self.states)
        
    def clear_states(self):
        self.states.clear()
        self.state_set.clear()
    
    def add_state(self, dot_pos: int, start: int, rule: Rule) -> State:
        state = State(dot_pos, start, rule)
        if state not in self.state_set:
            self.states.append(state)
            self.state_set.add(state)
        return state
    
    def __str__(self) -> str:
        return '\n'.join(
            (
                '-' * 30,
                f'Column {self.index} for token `{self.token}`:',
                '-' * 30,
                *(str(state) for state in self.states),
            )
        )

@dataclass
class Chart:
    columns: Optional[list[Column]] = field(default_factory=list)
    
    def add_column(self, token: str) -> Column:
        column = Column(len(self.columns), [], token)
        self.columns.append(column)
        return column
    
    def backtrack(self, num_steps: int):
        self.columns = self.columns[:-num_steps]
    
    def __str__(self) -> str:
        return 'Chart\n\n' \
        +  '\n\n'.join(str(column) for column in self.columns)

class EarleyParser:
    
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.chart = Chart()
        
    def _backtrack(self, num_steps: int):
        self.chart.backtrack(num_steps)
              
    def _complete(self, state: State, column: Column):
        start_column = self.chart.columns[state.start]
        for start_col_state in start_column.states:
            if start_col_state.peek() == state.rule.lhs:
                column.add_state(start_col_state.dot_pos + 1, start_col_state.start, start_col_state.rule)
    
    def _predict(self, state: State, column: Column):
        for rule in self.grammar.rule_map.get(state.peek(), []):
            column.add_state(0, column.index, rule)
    
    def _scan(self, state: State, next_column: Column, token: str):
        if state.peek().match(token):
            next_column.add_state(state.dot_pos + 1, state.start, state.rule)
            
    
    def try_accept_tokens(self, new_tokens: Sequence[str], start_symbol: str | None=None) -> bool:
        
        if start_symbol is None:
            start_symbol = self.grammar.start_symbol
        
        tokens_consumed = 0
        
        if len(self.chart.columns) == 0:
            self.chart.add_column('')
            for rule in self.grammar.rule_map[start_symbol]:
                self.chart.columns[0].add_state(0, 0, rule)
        else:
            column = self.chart.columns[-1]
            token = new_tokens[0]
            next_column = self.chart.add_column(token)
            for state in column.states:
                if state.is_next_terminal():
                        self._scan(state, next_column, token)
            
            tokens_consumed += 1
        
        for i in range(tokens_consumed, len(new_tokens) + 1):
            
            column = self.chart.columns[-1]
            
            if i < len(new_tokens):
                token = new_tokens[i]
                next_column = self.chart.add_column(token)
            
            it = 0
            while it < len(column.states):
                state = column.states[it]
                if state.is_complete():
                    self._complete(state, column)
                else:
                    if state.is_next_terminal() and i < len(new_tokens):
                        self._scan(state, next_column, token)
                    else:
                        self._predict(state, column)
                it += 1
        
        is_acceptable = len(self.chart.columns[-1].states) > 0
        
        if not is_acceptable:
            self._backtrack(len(new_tokens))
        
        return is_acceptable
        
    def _fill_chart(self, tokens: Sequence[str], start_symbol):
        # Initialize the chart with Column 0
        # Add an empty dummy token for Column 0
        self.chart.add_column('')
        for rule in self.grammar.rule_map[start_symbol]:
            self.chart.columns[0].add_state(0, 0, rule)
        
        # Fill the chart using the core Earley algorithm
        for i in range(len(tokens) + 1):
            if i < len(tokens):
                token = tokens[i]
                next_column = self.chart.add_column(token)
                
            column = self.chart.columns[i]
            
            it = 0
            while it < len(column.states):
                
                state = column.states[it]
                
                if state.is_complete():
                    self._complete(state, column)
                else:
                    if state.is_next_terminal() and i < len(tokens):
                        self._scan(state, next_column, token)
                    else:
                        self._predict(state, column)
                it += 1
        
    def parse(self, tokens, start_symbol: None) -> Node | None:
        if start_symbol is None:
            start_symbol = self.grammar.start_symbol
        self._fill_chart(tokens, start_symbol)
