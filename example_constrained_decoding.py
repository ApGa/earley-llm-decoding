from grammar import Grammar, Rule, Terminal

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from logits_processor import CFGLogitsProcessor


if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


    model_name = "microsoft/phi-2"
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.generation_config.pad_token_id = model.generation_config.eos_token_id


    grammar = Grammar(
        start_symbol='root',
        rules= [
            Rule('root', (Terminal('y'), Terminal('e'), Terminal('a'))),
            Rule('root', (Terminal('n'), Terminal('a'), Terminal('h'))),
        ]
    )


    grammar_processor = CFGLogitsProcessor(grammar, 2, tokenizer)

    prefix1 = "<|startoftext|>Would you like ice cream? "
    prefix2 = "<|startoftext|>Do you want to buid a snowman? "
    input_ids = tokenizer([prefix1, prefix2], add_special_tokens=False, return_tensors="pt", padding=True)["input_ids"]

    output = model.generate(
        input_ids.to(device),
        logits_processor=[grammar_processor],
        num_return_sequences=1,
        max_new_tokens=5
    )


    generations = tokenizer.batch_decode(output, skip_special_tokens=True)
    print(generations)    
