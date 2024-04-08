import math

from grammar import Grammar
from earley import EarleyParser
from transformers.generation import LogitsProcessor
from tokenizers import Tokenizer
import torch

class CFGLogitsProcessor(LogitsProcessor):
    def __init__(self, grammar: Grammar, batch_size: int, tokenizer: Tokenizer):
        self.grammar = grammar
        self.parsers = [EarleyParser(grammar) for _ in range(batch_size)]
        self.tokenizer = tokenizer
        
    def __call__(self, input_ids, logits):
        acceptable_indices = []
        _, idxs = torch.sort(logits, dim=1, descending=True)
        
        for n, parser in enumerate(self.parsers):
            found_idx = False
            for idx in idxs[n]:
                token = self.tokenizer.convert_ids_to_tokens([idx])[0]
                if token and parser.try_accept_tokens(token):
                    acceptable_indices.append(idx)
                    found_idx = True
                    break
            if not found_idx:
                acceptable_indices.append(self.tokenizer.eos_token_id)
                
        mask = torch.ones_like(logits, dtype=torch.bool)
        mask[list(range(len(self.parsers))), acceptable_indices] = 0
        logits[mask] = -math.inf
        
        return logits