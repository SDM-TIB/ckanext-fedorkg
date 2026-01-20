[![Latest Release](http://img.shields.io/github/release/SDM-TIB/ckanext-fedorkg.svg?logo=github)](https://github.com/SDM-TIB/ckanext-fedorkg/releases)
[![License: GPL v3](https://img.shields.io/github/license/SDM-TIB/ckanext-fedorkg?color=blue)](LICENSE.md)

[![CKAN](https://img.shields.io/badge/ckan-2.9%20%7C%202.10-orange.svg?style=flat)](https://github.com/ckan/ckan)

# FedORKG

`ckanext-fedorkg` is a CKAN plugin that adds support to query open research knowledge graphs via SPARQL queries.
FedORKG uses [DeTrusty](https://github.com/SDM-TIB/DeTrusty/) as federated query engine.
The visual query editor connecting the frontend and DeTrusty is implemented using the JavaScript library [YASGUI](https://github.com/TriplyDB/yasgui).

## LLM-based Question Answering

> [!NOTE]
> This feature is experimental.

Powered by the LLM `o4-mini`, FedORKG is able to answer natural language questions over the federation by relying on the LLM to translate the question into a SPARQL query.
Check steps 3 and 4 in the post-install setup on how to configure this feature.

## Installation

Path variables used below:

- `$CKAN_STORAGE_PATH` (i.e., where CKAN stores files), e.g., `/var/lib/ckan`
- `$CKAN_INI` (i.e., the CKAN configuration file), e.g., `/etc/ckan/default/ckan.ini`

### Installing from Source

As usual for CKAN extensions, you can install `ckanext-fedorkg` as follows:

```bash
git clone git@github.com:SDM-TIB/ckanext-fedorkg.git
pip install -e ./ckanext-fedorkg
pip install -r ./ckanext-fedorkg/requirements.txt
```

### Post-install Setup

1. Copy your file for the source descriptions of DeTrusty to the following location:
   ```
   $CKAN_STORAGE_PATH/fedorkg/rdfmts.ttl
   ```
2. Add `fedorkg` to the list of plugins in your `$CKAN_INI`:
   ```ini
   ckan.plugins = ... fedorkg
   ```
   > [!NOTE]
   > If you have `ckanext-scheming` installed, you have to mention `fedorkg` before the scheming extension in your `$CKAN_INI`.
   > Otherwise the scheming extension overrides the changes of the FedORKG plugin.
3. Copy your file containing the instructions to be included in the prompt to the following location:
   ```
   $CKAN_STORAGE_PATH/fedorkg/prompt.txt
   ```
4. Provide your OpenAI API code in an environment variable called `OPENAI_API_KEY`.
5. Make sure that the CKAN background job workers are running.
   Without them, the federation management features of FedORKG, i.e., adding and deleting knowledge graphs, will not work.
   - CKAN 2.9: https://docs.ckan.org/en/2.9/maintaining/background-tasks.html
   - CKAN 2.10: https://docs.ckan.org/en/2.10/maintaining/background-tasks.html
6. Initialize the database table for the FedORKG federation management news:
   ```bash
   ckan -c $CKAN_INI fedorkg initdb
   ```
7. Start the FedORKG source description SPARQL endpoint the background:
   ```bash
   ckan -c $CKAN_INI fedorkg start &> $CKAN_STORAGE_PATH/fedorkg/fedorkg-metadata.log &
   ```

## Configuration Options

- `ckanext.fedorkg.query` the default query shown to the users
  - Default: SELECT DISTINCT ?c WHERE { ?s a ?c }
- `ckanext.fedorkg.query.name` a human-readable name for the default query
  - Default: Covered Concepts 
- `ckanext.fedorkg.timeout` query execution timeout in seconds
  - Default: 60

## Commands

`ckanext-fedorkg` offers the following commands, assuming `$CKAN_INI` is the path of your CKAN configuration file:

1. `initdb`: initializes the database table for the federation management news.
   ```bash
   ckan -c $CKAN_INI fedorkg initdb
   ```
2. `start`: starts the SPARQL endpoint serving the source description required for query decomposition and query planning.
   ```bash
   ckan -c $CKAN_INI fedorkg start
   ```
3. `version`: shows the current version of `ckanext-fedorkg` and DeTrusty.
   ```bash
   ckan -c $CKAN_INI fedorkg version
   ```

## Changelog

If you are interested in what has changed, check out the [changelog](CHANGELOG.md).

## License

`ckanext-fedorkg` is licensed under GPL-3.0, see the [license file](LICENSE).

## Development

The translations can be managed with the `Makefile`.
However, CKAN and its dependencies must be installed in the same environment for the commands to work.

## Publications

1. Philipp D. Rohde, Enrique Iglesias, Maria-Esther Vidal: _FedORKG: Accessing Federations of Open Research Knowledge Graphs_. In: 1. NFDI4Energy Conference. DOI [10.5281/zenodo.10591442](https://doi.org/10.5281/zenodo.10591442)
