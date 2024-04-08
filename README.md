# Constrained LLM Decoding with Earley Parser

Some fun weekend explorations to learn more about earley parsing and constrained decoding with LLMs. 


## Current Status
Early stage exploration and prototyping. 

- `earley.py` implements earley chart filling algorithm with extensions to support incremental parsing and backtracking. Example usage in `example_incremental_parsing.py` (using the `try_accept_tokens` function).
- `logits_processor.py` implements a hf transformers LogitProcessor which forces sampling/decoding to choose the token with highest predicted probablity that is permitted by the grammar. Example usage in `example_constrained_decoding.py`.

## Setup
- Developed with python 3.12. Though, python 3.10+ will likely work.
- Create an environment for this project. One way is using conda: `conda create -n earley-decoding python=3.12`
- Activate your environment: `conda activate earley-decoding`
- Install dependencies using `pip install -r requirements.txt` in your environment.

## Some TODOs
- Leo optimizations and support for nullable grammars.
- Token healing in constrained decoding similar to the `guidance` library. Currently we do not try alternate token sequences with the same prefix when sampling the next tokens. Without this, generation seems to often be degenerate.
- Logits processor implementation is very naive right now and slow -- there must be ways we can optimize (e.g. caching prefixes). We can probably use microsoft `aici` library for more low level control.
- ...
