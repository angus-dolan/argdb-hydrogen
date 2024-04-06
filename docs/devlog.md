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

### Tue 13th Feb

Turns out like I thought, it wasn't really my lexer and parser algorithm that was slow. But the database calls in the parser.
But I've rebuilt the parser as a recursive moore machine. It's more performant and easier to understand now.

Upon running pyinstrument I noticed that there was a performance increase but it was still slower than expected. After diagnosing I removed all database initialisation code and the compiler was able to run in 0.019s for 10 argsme json arguments.

Before removing database:
```
0.150 <module>  hydrogen.py:1
├─ 0.146 <module>  importer/__init__.py:1
│  ├─ 0.120 <module>  importer/emitter.py:1
│  │  └─ 0.120 <module>  database.py:1
│  │     ├─ 0.077 <module>  sqlalchemy/__init__.py:1
│  │     │     [43 frames hidden]  sqlalchemy, <built-in>, importlib, em...
│  │     ├─ 0.031 <module>  sqlalchemy/ext/declarative/__init__.py:1
│  │     │     [21 frames hidden]  sqlalchemy, <built-in>
│  │     ├─ 0.007 create_engine  <string>:1
│  │     │     [7 frames hidden]  <string>, sqlalchemy
│  │     └─ 0.004 Node.__init__  sqlalchemy/orm/decl_api.py:56
│  │           [9 frames hidden]  sqlalchemy, <string>
│  └─ 0.023 <module>  importer/batch.py:1
│     ├─ 0.015 <module>  importer/lexer.py:1
│     │  ├─ 0.012 <module>  importer/models/__init__.py:1
│     │  │  └─ 0.011 <module>  importer/models/sadface.py:1
│     │  │     └─ 0.011 <module>  sadface/__init__.py:1
│     │  │           [9 frames hidden]  sadface, configparser, datetime, <bui...
│     │  └─ 0.002 <module>  logging/__init__.py:1
│     ├─ 0.003 <module>  ijson/__init__.py:1
│     │     [2 frames hidden]  ijson
│     └─ 0.003 <module>  importer/parser.py:1
│        └─ 0.003 <module>  hashlib.py:1
│              [2 frames hidden]  hashlib, <built-in>
└─ 0.002 Database.initialize  database.py:104
   └─ 0.002 MetaData.create_all  sqlalchemy/sql/schema.py:4905
         [2 frames hidden]  sqlalchemy
```

After removing database from main and importer/__init__ which included the emitter:
```
0.019 <module>  hydrogen.py:1
├─ 0.017 <module>  importer/__init__.py:1
│  └─ 0.017 <module>  importer/batch.py:1
│     ├─ 0.012 <module>  importer/lexer.py:1
│     │  ├─ 0.010 <module>  importer/models/__init__.py:1
│     │  │  ├─ 0.009 <module>  importer/models/sadface.py:1
│     │  │  │  └─ 0.009 <module>  sadface/__init__.py:1
│     │  │  │        [39 frames hidden]  sadface, configparser, <frozen abc>, ...
│     │  │  └─ 0.001 len  <built-in>
│     │  └─ 0.002 <module>  logging/__init__.py:1
│     │        [12 frames hidden]  logging, re
│     ├─ 0.003 <module>  importer/parser.py:1
│     │  └─ 0.003 <module>  hashlib.py:1
│     │        [5 frames hidden]  hashlib, <built-in>
│     └─ 0.002 <module>  ijson/__init__.py:1
│           [9 frames hidden]  ijson, importlib, <built-in>, decimal...
├─ 0.001 open_code  <built-in>
└─ 0.001 ArgsmeBatchImporter.batch_import  importer/batch.py:34
   └─ 0.001 ArgsmeBatchImporter.load_argsme_batches  importer/batch.py:40
      └─ 0.001 ArgsmeBatchImporter.process_argsme_batch  importer/batch.py:80
         └─ 0.001 ArgsmeParser.parse  importer/parser.py:101
            └─ 0.001 ArgsmeParser.process  importer/parser.py:89
               └─ 0.001 ArgsmeParser.build_node  importer/parser.py:50
                  └─ 0.001 ArgsmeToken.__hash__  enum.py:1224
                        [2 frames hidden]  enum, <built-in>
```

Therefore, after the refactoring and performance improvements. The database was causing around 87% of the runtime. From this I can infer that the refactoring was worth it. Not only for the code quality improvements, but the move to a 1GB batch importer and memory only processing with no database calls means I can do an expensive database transaction once all the data has been performantly processed in memory.

Problem with argsme dataset found?
```
    def restore(self):
        prev_id = self._lexed_tokens[ArgsmeToken.CTX_PREV_ID]

        if not prev_id:
            self._current_state = 'new_doc'
            return

        src_id = self._lexed_tokens[ArgsmeToken.CTX_SRC_ID]
        document = self._batch['completed'][src_id]

        self._builder.with_existing_document(document)
        self._current_state = 'update_doc'
```
Using this as a means to update existing documents doesnt seem to be reliable with the dataset as ID's seem to jump around and arent in a linear fashion

I think a potential fix might be initialising the batch['completed'] with sourceIds extracted using jq before lexing and parsing.

But then that breaks the moore machine state transition logic as I'll probably need to use the tokens present in methods like build_edge etc.

Implimented the above
- Parser restore() is actually cleaner and I didn't need to change any state transition logic
- I simply look if the current value in batch['completed'] is none
- PyJQ was far too slow so instead set batch['completed'] as I'm streaming in the data with ijson
- The compiler seems to work fully now with 59k arguments processed.

Same dataset as previous examples for comparison, barely any performance drop.

```
0.024 <module>  hydrogen.py:1
├─ 0.022 <module>  importer/__init__.py:1
│  └─ 0.022 <module>  importer/batch.py:1
│     ├─ 0.014 <module>  importer/lexer.py:1
│     │  ├─ 0.012 <module>  importer/models/__init__.py:1
│     │  │  ├─ 0.010 <module>  importer/models/sadface.py:1
│     │  │  │  └─ 0.010 <module>  sadface/__init__.py:1
│     │  │  │        [32 frames hidden]  sadface, <built-in>, configparser, re...
│     │  │  ├─ 0.001 BufferedReader.read  <built-in>
│     │  │  └─ 0.001 [self]  importer/models/__init__.py
│     │  ├─ 0.001 loads  <built-in>
│     │  └─ 0.001 <module>  logging/__init__.py:1
│     │        [11 frames hidden]  logging, re
│     ├─ 0.003 <module>  ijson/__init__.py:1
│     │     [9 frames hidden]  ijson, decimal, <built-in>, importlib
│     ├─ 0.002 <module>  importer/parser.py:1
│     │  └─ 0.002 <module>  hashlib.py:1
│     │        [5 frames hidden]  hashlib, <built-in>
│     ├─ 0.001 BufferedReader.read  <built-in>
│     └─ 0.001 <module>  pyjq.py:1
├─ 0.001 setup_logging  log_config.py:4
│  └─ 0.001 basicConfig  logging/__init__.py:1953
│        [3 frames hidden]  logging
└─ 0.001 ArgsmeBatchImporter.batch_import  importer/batch.py:35
   └─ 0.001 ArgsmeBatchImporter.load_argsme_batches  importer/batch.py:41
      └─ 0.001 ArgsmeBatchImporter.process_argsme_batch  importer/batch.py:85
         └─ 0.001 ArgsmeParser.parse  importer/parser.py:100
            └─ 0.001 SadfaceBuilder.validate  importer/builder.py:31
               └─ 0.001 Sadface.validate  importer/models/sadface.py:44
                  └─ 0.001 verify  sadface/validation.py:254
                        [4 frames hidden]  sadface, uuid, <built-in>
```

41 seconds to import entire argsme dataset, not bad.
```
41.081 <module>  hydrogen.py:1
└─ 41.056 ArgsmeBatchImporter.batch_import  importer/batch.py:35
   └─ 41.056 ArgsmeBatchImporter.load_argsme_batches  importer/batch.py:41
      ├─ 34.758 ArgsmeBatchImporter.process_argsme_batch  importer/batch.py:85
      │  ├─ 26.485 ArgsmeParser.parse  importer/parser.py:100
      │  │  ├─ 23.915 SadfaceBuilder.validate  importer/builder.py:31
      │  │  │  └─ 23.830 Sadface.validate  importer/models/sadface.py:44
      │  │  │     └─ 23.731 verify  sadface/validation.py:254
      │  │  │           [15 frames hidden]  sadface, uuid, <built-in>
      │  │  └─ 2.314 ArgsmeParser.process  importer/parser.py:88
      │  │     ├─ 0.764 ArgsmeParser.build_node  importer/parser.py:50
      │  │     ├─ 0.482 ArgsmeParser.build_edge  importer/parser.py:61
      │  │     └─ 0.464 ArgsmeParser.restore  importer/parser.py:76
      │  ├─ 5.570 ArgsmeLexer.tokenize  importer/lexer.py:95
      │  │  └─ 5.480 ArgsmeLexer._process  importer/lexer.py:62
      │  │     ├─ 3.858 ArgsmeLexer._process  importer/lexer.py:62
      │  │     │  ├─ 1.226 ArgsmeLexer._process  importer/lexer.py:62
      │  │     │  │  └─ 0.646 ArgsmeLexer._process  importer/lexer.py:62
      │  │     │  ├─ 0.970 [self]  importer/lexer.py
      │  │     │  ├─ 0.761 ArgsmeLexer._get_token_value  importer/lexer.py:76
      │  │     │  │  └─ 0.657 [self]  importer/lexer.py
      │  │     │  └─ 0.566 property.__get__  enum.py:193
      │  │     ├─ 0.716 ArgsmeLexer._get_token_value  importer/lexer.py:76
      │  │     │  └─ 0.681 [self]  importer/lexer.py
      │  │     └─ 0.476 [self]  importer/lexer.py
      │  ├─ 1.022 print  <built-in>
      │  ├─ 0.632 [self]  importer/batch.py
      │  ├─ 0.511 ArgsmeParser.__init__  importer/parser.py:36
      │  └─ 0.489 ArgsmeLexer.__init__  importer/lexer.py:35
      │     └─ 0.438 [self]  importer/lexer.py
      ├─ 3.575 [self]  importer/batch.py
      └─ 2.522 dumps  json/__init__.py:183
            [3 frames hidden]  json
```

### Sat 24th Feb
- Prototype vector index [#1](https://github.com/angus-dolan/argdb-hydrogen/pull/1)
- Improved importer and emitter [#2](https://github.com/angus-dolan/argdb-hydrogen/pull/2)

### Sun 3rd March

[#3](https://github.com/angus-dolan/argdb-hydrogen/pull/3)

Worked on the search engine parser.


- `remove_links`
  - Uses regex to remove all links (argsme dataset tends to have a lot)
- `remove_stopwords`
  - Uses the nltk english stopwords dataset without the nltk dependency 
- `remove_punctuation`
  - Uses the same punctuations as `string.punctuation`
  - Used a single pointer
  - Decided better approach was adding spaces before/after punc characters before splitting, then its a simple removal of punc tokens.
  - Was useful for handling text like: "Exercise(the prime" => ["exercise", "(", "the"]
  - I'm hoping n-grams will be the way to handle bad formatting, e.g. "exercisetheprime" (with no spaces)
- Next:
  - Decide size of N-Grams
  - Build N-Gram sliding window
  - Inverted index

### Thu 7th March

[#4](https://github.com/angus-dolan/argdb-hydrogen/pull/4/)

- Investigated building a redis database clone from scratch, decided it wasn't worth the extra effort.
- Added a docker-compose to start a redis service for the inverted index.
- Built a `SearchEngine` class with `add_document` and `search` methods.
- Implimented edge n-grams in the search indexer.

Search results still return the best documents first with edge n-grams compared to just concordance. But more documents are returned and they are irellevant. This was expected, since n-grams will generate 100s of terms for a document, so its more likely to get matched. I'm hoping this will fix itself with more documents than just 7. Then it can be a case of tweaking the size of N and limiting results or using a relevance scoring algorithm like Okapi BM25.

Example search results comparison:

**Concordance**:
```shell
Enter Search Term: Captcha
Relevance: 0.19245008972987526, Document: Why You Shouldnt roll your own CAPTCHA At a TechEd I attended a few years ago I was watching a prese...
Relevance: 0.13130643285972254, Document: Why CAPTCHA Never Use Numbers 0 1 5 7 Interestingly this sort of question pops up a lot in my referr...
```
**Edge n-grams:**
```shell
Enter Search Term: Captcha
# Same docs as concordance
Relevance: 0.3030457633656632, Document: Why CAPTCHA Never Use Numbers 0 1 5 7 Interestingly this sort of question pops up a lot in my referr...
Relevance: 0.17560468218497577, Document: Why You Shouldnt roll your own CAPTCHA At a TechEd I attended a few years ago I was watching a prese...
# Search pollution
Relevance: 0.08754693987147766, Document: The Great Benefit of Test Driven Development Nobody Talks About The feeling of productivity because ...
Relevance: 0.044086671417740544, Document: Richard Stallman to visit Australia Im not usually one to promote events and the like unless I feel ...
Relevance: 0.04300329525375306, Document: At Scale You Will Hit Every Performance Issue I used to think I knew a bit about performance scalabi...
Relevance: 0.030556616567607043, Document: Setting up GIT to use a Subversion SVN style workflow Moving from Subversion SVN to GIT can be a lit...
Relevance: 0.016356122383769687, Document: MySQL Backups Done Easily One thing that comes up a lot on sites like Stackoverflow and the like is ...
```

Edge n-grams will be great for building an autocomplete. As mentioned I think this results pollution will fix itself with more data.

Next:
- Persist inverted index in redis
- Sharding larger documents
- Relevance/Boosting
- Build a dockerized API service
- Search method performance improvements, see line 35 of `engine.py` in this PR
- Connect importer to search engine, I want to follow IBM research and mark arguments > 210 characters as low quality, maybe not even index them. Would make a good discussion point about argsme dataset in write up.

### Sat 9th March
- Connected search engine prototype to importer.
- Indexed all 58k arguments.
- Took the approach of having each sadface id as the redis key
- e.g. `"search_index:c67482ba-2019-04-18T13:32:05Z"`
- with each sadface doc id key having many indexed texts
- N-Grams way too big.
- This is already a naive and CPU intensive implimentation, but N=2 generates way too many terms and causes insane results pollution.
- Takes 145 seconds to return a simple search query.
- And it has 32k results (search pollution did not fix itself).
- This is with n grams size set to 2.
- Going to experiment with larger n grams and see if it improves the speed. 
- If not look at the bigger picture (maybe ditch vector index).

```shell
query = "Something about high school"
Number of results: 327517
```

```shell
  _     ._   __/__   _ _  _  _ _/_   Recorded: 19:56:07  Samples:  107963
 /_//_/// /_\ / //_// / //_'/ //     Duration: 145.463   CPU time: 61.677
/   _/                      v4.6.2

145.461 profile_search_engine  engine.py:44
└─ 145.350 main  engine.py:33
   └─ 144.457 SearchEngine.search  engine.py:26
      └─ 144.457 SearchIndex.get_matches  index.py:18
         ├─ 106.995 Redis.smembers  redis/commands/core.py:3394
         │     [17 frames hidden]  redis, <built-in>
         │        79.238 socket.recv  <built-in>
         ├─ 21.117 loads  json/__init__.py:299
         │     [3 frames hidden]  json
         └─ 14.900 SearchIndex.relation  index.py:49
            └─ 14.020 SearchIndex.magnitude  index.py:38
               └─ 13.906 [self]  index.py

```

# Tue 12th Mar
- Started building a frontend
- Debated between simple templating and a reactive frontend framework
- Decided on nuxt
- Decided I need to ditch sqlite for storing the arguments
- Can use sqlite for basic (in between) data storage

# Wed 13th Mar
- Want to make emitter an interface to chose between elastic and sqlite in future
- 1-1 indexing is too slow with elastic
  - Needs refactoring to use bulk api
- File system emitter was problematic due to read/write permissions
- Used redis
- Still had a lot of issues
- 100mb limit on elastic search required new batch system
- creating a vector embedding with naive solution was too slow and crashed
- Switched to focus on tackling full text first
- added kibana service to view data easier

# Fri 5th April
- importer/emitter
  - Refactored redis emitter
  - Main focus was changing chunk data from string to a set
  - search/engine/reindex() was messy getting data from redis as string
  - Emitter is also more readable now
- api
  - Moved elastic search logic into new engine
  - Also cleaned up routes
- search/engine
  - Refactored
  - Uses bridge pattern
  - Removed filters, aggs etc. for clarity
  - Full-text back and working but still needs semantic/hybrid
- frontend
  - utils was missing from git due to gitignore

- semantic search
  - summary system for esler model 
  - generating summaries broke the 100mb elastic limit that were avoided with redis chunks 
  - edges were left out as they arent relevant
  - nodes had to be stemmed to just node text

- semantic search inference
  - https://www.elastic.co/guide/en/elasticsearch/reference/8.3/start-trained-model-deployment.html
    - Needed timout
      - self.es.ingest.put_pipeline(='elser-ingest-pipeline' timeout='60s')
    - Needed queue capacity of 100k, tried 10k first
      - self.es.ml.start_trained_model_deployment(model_id=model_id, queue_capacity=10000)
    - Almost got it working but it needed more threads
      - self.es.ml.start_trained_model_deployment(model_id=model_id, queue_capacity=10000, threads_per_allocation=4)
      - 4 was the max available on my hardware/docker container
    - Had a bug with inference timing out:
    - https://github.com/elastic/elasticsearch/issues/94490
    - Upgraded to >=8.11.1 to fix
    - It works but times out due to hardware limitations when inference on the summary
    - Added a parser to search engine to reduce data
    - Going to try cloud inference as a potential workaround