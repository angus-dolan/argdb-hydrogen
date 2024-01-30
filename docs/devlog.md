## Sat 6th Jan 2024

#### sadface_translator

Worked on the data importer module, decided on the below structure inspired by [this blog](https://austinhenley.com/blog/teenytinycompiler1.html) and [crafting compilers](https://craftinginterpreters.com/contents.html).

input data --> Lexer --> Parser --> Validator --> Emitter

Lexer:
  - Generates tokens from a raw json file to map to sadface
  - Logs anything that isn't gathered
  - Needs to know what tokens to look for
  - Argument formats all have different tokens that can map to sadface, **strategy pattern** could accomidate this.

Parser:
  - Generates an argument tree from the tokens provides by the lexer
  - Needs to know the rules/structure of a sadface argument
  - Started with composite pattern, which adds a lot of complexity - builder probably simpler
  - Uses both strategy and sadface argument builder

Emitter:
  - Ideally, simply "flattens" the argument tree provided by the parser
  - Then "emmits" to a temporary data store that a pub/sub data importer will batch process arguments as they come in.
  - Could maybe use observer or repository pattern

Sadface Argument Builder:
  - Builder pattern to build a sadface argument
  - Can set `options` i.e. json keys or `flags`

Validator:
  - Not sure if needed, won't do any work on it until rest of code is built out

## Sun 7th Jan 2024
Focus: lexer
Built out the lexer based on a basic compiler design.

## Mon 8th Jan 2024
Focus: 
  - finishing compiler
  - Parser algorithms
    - LL Parser, LR Parser, SLR (Simple LR) Parser, LALR (Look-Ahead) Parser, Recursive Descent Parser, Predictive Parser, Early Parser, Packrat Parsing, CYK (Cocke-Younger-Kasami) Algorithm

Lexer design: Finite State Machines:
  - Finite Automata
  - We'll need a FA with output
  - Two options considered were a **Moore Machine** or a **Mealy Machine**
  - After looking at boilerplate code I realised I was already building a Moore Machine

## Tue 9th Jan 2024
Focus: Finished argsme lexer prototype
Ended up removing json lexical analysis code as it isnt the focus for the lexer, I just want to extract the argsme keywords and data.
Was going to do a valid parenthesis inspired validator but chose to leave that for the parser or emitter.

## Thu 11th Jan 2024
Focus: Parser
- Instead of storing tokens as a list in lexer, swapped to a deque. Popping a list had O(N) complexity, popleft on a deque has O(1)
- It seems the argsme json data is corrupt, ID's seem to point no where
- On further inspection, sourceId was the wrong thing to look at. I think that just provides a way to find where things were scraped from.
- I managed to extract a group of 9 chained arguments from the dataset using nextArgumentid
- I might need to use sourceId to build sadface document tree

### Sun 14th Jan
Focus: config system
- Refactored folder structure a bit.
- Implimented a config file system based off Simon's ArgDB.
- Originally used the config system to create a config file AND initialise database.
- Realised the database initialization would work better in the actual database layer.

### Tue 16th Jan
Focus: Data layer
- Implimented boilerplate database layer loosely following the repository pattern.
- Deciced to use sqlalchemy for data modelling.

### Sun 28th Jan
- Made rough parser but decided to spike out without building a tree
- Spike used the database repo to store 
- Hardest thing is retrieving and updating an existing sf doc
- Also bug was found in sadface metadata validation
- Originally thinking was to build the sf doc in the parser then pass to emitter to store in db.
- Now thinking, every parser func should call the emitter incrementally until the sf doc is ready.

### Mon 29th Jan
- Moved root > data_importer > models into root > models
- Moved Token and ArgsmeToken into Tokens
- Created a Sadface class to simplify builder and to use in adapters if needed
- Introduced DataHandler class to Parser to avoid handle_token becoming an god object if statement mess

### Tue 30th Jan
- Had a lot of circular import problems with db somehow
- Moved all database files into single root level database.py
- Created a BaseRepository for all repos to inherit from