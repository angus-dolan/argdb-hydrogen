### Datasets

The datasets can be downloaded [here]() and should be placed in this directory.

- argsme_corpus.json
  - Open source dataset of 387,692 arguments that are compiled down to 59,637k by the importer.
  - Used to populate search engine.
- summary_dataset.json
  - Summaries of each SADFAce argument compiled by the importer
- embeddings_dataset.json
  - Vector embeddings of all the summaries.
  - Used by elasticsearch to provide semantic hybrid search.
  - Note: Cloud GPU hardware was used to generate the dataset. GPU hardware is generally required to generate such a large volume of embeddings. See `generate_embeddings.py` for script used.

