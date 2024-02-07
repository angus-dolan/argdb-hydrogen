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
- Realised using source_id for document_id will work, was needed when updating an existing sadface document
- Instead of having to use `from database import Database, Raw` I should use an adapter - therefore I won't need to import Raw and can just ping sadface docs directly to repo without having to use Raw model, which could easily change.

### Wed 31st Jan
- Introduced logging system to help debug importer
- Fixed bug in parser match and handle
- Fixed bug in lexer:
  - 2024-01-31 16:37:35,300 - data_importer.lexer - ERROR - Lexing error: String not terminated properly | Argument ID: fbe6ad2-2019-04-18T11:12:36Z-00001-000
- The bug was occurring because the string_lookahead method failed to handle escaped quotes within strings, incorrectly interpreting them as the end of the string.
- Able to run the importer, wow it's slow - might need to be ran overnight.
- I estimate it might take 380hrs to complete 
- Number of performance improvement options I can think of
  - Reduce write intensive scenarios
    - Do checks in data_importer before invoking lexer, parser
    - Parser currently always writes to db.
  - Redis cache as batch processing db (faster in write intensive scenarios, sqlite is slow in writing)
  - Only compile node and edge data if the argument isn't the root argument
  - Problem with using redis is ultimately it would need to be cloud deployed in prod env, this goes against argdb ethos of being self contained and data privacy focused.
  - Will need to give this greater thought, as cloud is looking like an innevitable fact with need for vector db also.
  - I wanted it to be plug in and play - easy UX
  - But users might need to setup a local redis and vector db to access all features if they want data privacy?
- Encoutered Lexing error: String not terminated properly | Argument ID: 2e465d2c-2019-04-18T15:47:29Z-00003-000

### Sun 4th Feb
- Refactored data_importer > importer
- Uses strategy pattern and batch import system
- Considered new db schema:
  - Collections (Way to logically organise data, e.g "" and "" collections)  
  - Imports: ID, CollectionID, Successes, Failures (track importing into a collection)
  - But elastic search would index all collections to provide a global search

### Tue 6th Feb
When rebuilding lexer to be a recursive moore machine,
The argsme dataset structure provided quite difficult to access nested keys 
For example
    `print(self.json_data['premises'][0]['stance'])`
    `print(self.json_data['context']['sourceTitle'])`
    `print(self.json_data['id'])`

Premises needed integer access since it was an array, context needed string.

Ended up modifying ArgsmeTokens to store nested keys like:
```
PREMISES = ['premises']
PREMISES_TEXT = ['premises', 0, 'text']
PREMISES_STANCE = ['premises', 0, 'stance']
CTX = ['context']
CTX_SRC_ID = ['context', 'sourceId']
...
ID = ['id']
CONCLUSION = ['conclusion']
```

Another design choice I want to remember is why I actually chose to make the lexer work recursively.
If I didn't store STATE_TRANSITIONS AND STATE_TOKENS like below, I would have needed methods for each transition.
My thinking with this is, if I need to track a new token, I just need to add it to STATE_TRANSITIONS and STATE_TOKENS instead of needing a new method. Which keeps the lexer much smaller, also I won't need to write a test for every new method. 
```
self.STATE_TRANSITIONS = {
    'start': 'premises',
    'premises': 'context',
    'context': 'id',
    'id': 'conclusion',
    'conclusion': 'end',
}
self.STATE_TOKENS = {
    'premises': [
        ArgsmeToken.PREMISES_STANCE,
        ArgsmeToken.PREMISES_TEXT
    ],
    'context': [
        ArgsmeToken.CTX_ACQ_TIME,
        ArgsmeToken.CTX_SRC_ID,
        ArgsmeToken.CTX_PREV_ID,
        ArgsmeToken.CTX_TITLE
    ],
    'id': [ArgsmeToken.ID],
    'conclusion': [ArgsmeToken.CONCLUSION]
}
```

Lexer is much smaller and cleaner now.

But performance is becoming a pressing issue.

It took over 10 hours to compile 167/59,637 sadface arguments


### Wed 7th Feb
- Installed pyinstrument to understand performance problems
- At first glance: it seems around 60% of the runtime is coming from a database call in the **parser**.
- My initial thought is to focus on this. First idea being to store batches in memory rather than using the database in the parser.
- After refactoring the lexer yesterday, I feel the parser could do with some improvements anyway.
- The batch system is a good idea, but each 1k batch of args is only around 2.5MB
- In theory, I could fit the whole 900mb dataset into 1GB of memory easily.
- Instead of batching by num of args, lets try batching by size of file.
- e.g. batches of 1GB
- I dont think its my lexing and parsing algo's that are slow, its the bad memory allocation use of db.
```
  _     ._   __/__   _ _  _  _ _/_   Recorded: 18:17:15  Samples:  156
 /_//_/// /_\ / //_// / //_'/ //     Duration: 0.171     CPU time: 0.169
/   _/                      v4.6.2

0.170 <module>  hydrogen.py:1
├─ 0.116 <module>  importer/__init__.py:1
│  └─ 0.116 <module>  importer/batch.py:1
│     ├─ 0.103 <module>  importer/parser.py:1


│     │  └─ 0.102 <module>  database.py:1 
│     │     ├─ 0.066 <module>  sqlalchemy/__init__.py:1
│     │     │     [42 frames hidden]  sqlalchemy, importlib, email, socket,...
│     │     ├─ 0.025 <module>  sqlalchemy/ext/declarative/__init__.py:1
│     │     │     [22 frames hidden]  sqlalchemy, <built-in>
│     │     ├─ 0.005 create_engine  <string>:1
│     │     │     [7 frames hidden]  <string>, sqlalchemy
│     │     └─ 0.004 Raw.__init__  sqlalchemy/orm/decl_api.py:56
│     │           [9 frames hidden]  sqlalchemy, <string>


│     └─ 0.012 <module>  importer/lexer.py:1
│        ├─ 0.009 <module>  importer/models/__init__.py:1
│        │  └─ 0.008 <module>  importer/models/sadface.py:1
│        │     └─ 0.008 <module>  sadface/__init__.py:1
│        │           [6 frames hidden]  sadface, configparser
│        └─ 0.002 <module>  logging/__init__.py:1
├─ 0.045 ArgsmeBatchImporter.batch_import  importer/batch.py:53
│  ├─ 0.025 Emitter.emit  importer/emitter.py:17
│  │  ├─ 0.012 RawRepository.get  database.py:88
│  │  │  ├─ 0.010 Query.one_or_none  sqlalchemy/orm/query.py:2826
│  │  │  │     [30 frames hidden]  sqlalchemy, logging
│  │  │  └─ 0.002 Query.filter_by  sqlalchemy/orm/query.py:1773
│  │  │        [17 frames hidden]  sqlalchemy
│  │  ├─ 0.011 RawRepository.update  database.py:91
│  │  │  └─ 0.011 _GeneratorContextManager.__exit__  contextlib.py:141
│  │  │     └─ 0.011 RawRepository.managed_transaction  database.py:71
│  │  │        └─ 0.011 Session.commit  sqlalchemy/orm/session.py:1404
│  │  │              [26 frames hidden]  sqlalchemy, logging, <built-in>
│  │  └─ 0.002 RawRepository.add  database.py:51
│  │     └─ 0.002 _GeneratorContextManager.__exit__  contextlib.py:141
│  │        └─ 0.002 RawRepository.managed_transaction  database.py:71
│  │           └─ 0.002 Session.commit  sqlalchemy/orm/session.py:1404
│  │                 [2 frames hidden]  sqlalchemy
│  └─ 0.019 first  pyjq.py:65
│        [2 frames hidden]  pyjq
├─ 0.007 Database.initialize  database.py:104
│  └─ 0.007 MetaData.create_all  sqlalchemy/sql/schema.py:4905
│        [13 frames hidden]  sqlalchemy, <built-in>
└─ 0.002 ArgsmeBatchImporter.__init__  importer/batch.py:30
   └─ 0.002 ArgsmeBatchImporter.calculate_batch_parameters  importer/batch.py:47
      └─ 0.002 first  pyjq.py:65
            [2 frames hidden]  pyjq
```

- Rebuilt batch importer to open file as stream using ijson
- Takes less than 6 seconds to load.

Using json.load and jq is around 60% faster than streaming because it avoids streaming with ijson and
loads the data directly into memory and isn't buffered. Loading a 900MB file in 6 seconds is acceptable
for our use case. For files larger than the ArgsMe dataset, streaming and batching may be necessary
to manage memory usage and to accommodate larger datasets.