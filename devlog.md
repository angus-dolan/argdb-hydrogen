## Sat 6th June 2024

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

## Sat 6th June 2024
Focus: lexer