Ragmatic
========

Ragmatic is a low-code tool for creating RAG applications.

Installation
------------

To install Ragmatic, clone this repo and use pip:

```bash
git clone https://github.com/jdraines/ragmatic.git
pip install -e "./ragmatic[hugging-face]"
```

Try it out
----------

> [!NOTE]
> In order to run these examples, you will need to have an OpenAI API key. We
> will set that key as an environment variable.

The `examples/` directory contains a couple of examples to get you started. The
first one to look at is [examples/winnie_the_pooh](./examples/winnie_the_pooh/).

First, cd into that directory:
    
```bash
cd examples/winnie_the_pooh
```

Ragmatic splits the RAG application into two main parts: A pipeline that
generates embeddings from text, and then a RAG agent that uses those embeddings
to answer questions.

We'll start by running the pipeline with the following command:

```bash
ragmatic run-pipeline -v local_documents_path=./book
```

This command will generate embeddings for the text in the `book` directory. The
embeddings will be saved in a newly created `./data/` directory.

Now, to run the actual RAG, you will need to set the `OPENAI_API_KEY` environment variable
to your OpenAI API key. For the purpose of this example, you can do that by
running the following command:

```bash
export OPENAI_API_KEY=your_openai_api_key
```

Now you can run the RAG agent with the following command:

```bash
ragmatic rag-query \
    -v local_documents_path=./book \
    -v n_nearest=3 \
    --query "Who found Eeyore's tail? Can you quote the text that describes the event?"
```

A few things to note about the command above. We've set the `local_documents_path` again
to the `book` directory. We've also set `n_nearest` to 3. This is a pretty low number, 
but our corpus only has 11 documents, so we want to demonstrate that the RAG agent can
still find relevant documents even with a small number of documents. Finally, we've set
the `query` parameter to the question we want to ask the RAG agent.

You should get a response that's something like:

```
Winnie-the-Pooh is the one who found Eeyore's tail. The text that describes the event is:

```txt
"Owl," said Pooh solemnly, "you made a mistake. Somebody did want it."

"Who?"

"Eeyore. My dear friend Eeyore. He was—he was fond of it."

"Fond of it?"

"Attached to it," said Winnie-the-Pooh sadly.
...
So with these words he unhooked it, and carried it back to Eeyore; and when Christopher Robin had nailed it on in its right place again, Eeyore frisked about the forest, waving his tail so happily that Winnie-the-Pooh came over all funny, and had to hurry home for a little snack of something to sustain him. And, wiping his mouth half an hour afterwards, he sang to himself proudly:
Who found the Tail?
"I," said Pooh,
"At a quarter to two
(Only it was quarter to eleven really),
I found the Tail!"
\```
```

Digging deeper
--------------

In the Winnie the Pooh example, we ran our rag agent using the default presets. (You can choose a preset by setting the
`--preset` parameter to one of the presets in the [`src/ragmatic/cli/configuration/presets/preset_factory.py`](./src/ragmatic/cli/configuration/presets/preset_factory.py) file. The
`local_docs` preset is the default one, and there is currently one other, `pycode`.)

There is a ton of configuration that you can do with Ragmatic, however, if you use a config file. You can see an example
of a project that uses a config file in the [examples/hello_printer](./examples/hello_printer) directory. The config file
in that directory is [example-config.yaml](./examples/hello_printer/example-config.yaml).

The Ragmatic configuration file is a yaml file that has the following top-level keys:

```yaml
project_name: ""
components: {}
pipelines: {}
rag_query_command: {}
```

The `project_name` key is a string that is the name of the project. The other keys deserve some attention.

### components

Ragmatic allows you to configure a number of reusable components. By declaring the components once in the `components`
section, you can use them in multiple pipelines (or multiple times in the same pipeline). The `components` that are
configured in Ragmatic are:

- `document_sources` - literally, the sources of the documents
- `storage` - storage abstractions that allow you to save and load data between pipeline steps and more long-term as well
- `llms` - adapters for different language models. (Currently `openai` and `anthropic` are supported.)
- `summarizers` - a component that allows you to generate new documents from existing ones (e.g. "describg this code file") using an llm
- `encoders` - a component that allows you to generate embeddings from text
- `rag_agents` - a component that puts together the RAG query process. In this component, you reference previously a defined llm, storage adapter, and encoder.

### pipelines

Ragmatic allows you to configure multiple pipelines and then invoke them with the `ragmatic run-pipeline [PIPELINE_NAME]` command.
A pipeline is a series of `Actions` that are executed in order. The `Actions` that are currently available are:
- `summarize` - use an llm to summarize documents
- `encode` - use an encoder model to generate embeddings from text
- `rag` - use a rag agent to answer questions about the documents

### rag_query_command

This key allows you to configure the `ragmatic rag-query` command by specifying the rag agent to use and the documents
to use.

### Running our hello_printer example

If you look at the configuration, you may notice that this RAG task is geared towards answering questions about a codebase.
In order to do this efficiently, we need to first use an llm to summarize the code files and then use and encoder to 
generate embeddings from the summaries. This is what the pipeline in the `example-config.yaml` file does. That pipeline
is named `ingest-python-codebase` in the config file.

To run the pipeline:

1. cd into the `examples/hello_printer` directory
2. ensure that you have the `OPENAI_API_KEY` environment variable set, and 
3. use the following command:

```bash
ragmatic run-pipeline ingest-python-codebase --config ./example-config.yaml
```

This will generate embeddings for the code files in the `./src` directory. The embeddings will be saved in the `./data/`
directory.

Now, to run a RAG query, use the following command:

```bash
ragmatic rag-query --config $SCRIPT_DIR/example-config.yaml \
    --query "What appears to be the main purpose of this code?"
```

What's next?
------------

- I'm hoping to add a FastAPI app that will serve the RAG agent.
- I'd like to write `DataSource` and `Storage` component adapters that will allow the use
  of a warehouse for documents and a key-value store like Redis for embeddings.
- To be viable at scale, Ragmatic will need to be stateful in order to allow DataSources
  to provide incremental updates to the pipeline.
