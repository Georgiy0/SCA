# SCA (Surface Coverage Analyzer)

SCA is a tool that automates analysis of web application attack surface via dynamic code instrumentation and coverage collection.

Currently PHP web applications are supported via:

|stack|coverage|params collection|state|
|-|-|-|-|
|PHP|[XDebug coverage mode](https://xdebug.org/docs/code_coverage)|[source code instrumentation + uopz extension](./php_implant/README.md)|PoC|

## DEVGUIDE

_NOTE:_ latest python should be used (python 3.12+)

1. use `init.sh` to setup python venv
2. prepare test stand with PHP web application integrated with SCA via [`php_sca`](./php_sca/README.md) implant

## [CODE OVERVIEW](./sca/README.md)

## USAGE

0. in order to interact with target application with authentication implement a class that extends [`RequestsSender`](./sca/scanner/requests_sender_base.py) and place it in [`requests_senders`](./sca/scanner/impl/request_senders/) folder (update [`__init__.py`](./sca/scanner/impl/request_senders/__init__.py) in `requests_senders` folder in order to export newly created class in `get_requset_senders` function) OR `postauthcookie` may be [configured](./sca/scanner/impl/request_senders/post_auth_sender_config.py) for web application with simple html form authentication

1. initialize new project:

```bash
python3 sca_cli.py proj.json init
```

`proj.json` file with project configuration template will be created.

2. update configuration

- set stand base uri in [`ScannerConfig`](./sca/scanner/impl/scanner_config.py)
- set credentials in [`ScannerConfig`](./sca/scanner/impl/scanner_config.py). Use the following format:

```json
{
    "name" : "credentials_set_name",
    "username" : "username",
    "password" : "password"
}
```

- add `"PHPCOV"` instrumentation module into [`ScannerConfig`](./sca/scanner/impl/scanner_config.py) in order to trigger PHP SCA implent coverage collection functionality
- add `"PHPPARAMS"` instrumentation module into [`ScannerConfig`](./sca/scanner/impl/scanner_config.py) in order to trigger PHP SCA implent param usages collection functionality
- configure project folder path in [`FolderProjectConfig`](./sca/project_reader/impl/foler_project_config.py) and path mapping
- configure path mappings in [`CodeNotesConfig`](./sca/code_notes_module/impl/code_notes_config.py) and [`CoverageManagerConfig`](./sca/coverage/impl/coverage_manager_config.py) if working directory of running application does not match with code directory (_e.g._ when the app runs in docker container)
- configure param value provider modules (_e.g._ `code_consts`, `flags`) in [`ParamAnalyzerConfig`](./sca/param_analyzer/impl/param_analyzer_config.py)
- configure param value configs ([`CodeConstValueProviderConfig`](./sca/param_analyzer/impl/value_providers/code_const_value_provider_config.py), [`FlagValueProviderConfig`](./sca/param_analyzer/impl/value_providers/flag_value_provider_config.py))

3. import some input requests via import command. _E.g._ the following command will import inputs from a text file `in.txt` with line seperated relative URI list (the URIs will be imported as `GET` requests that will use `admin` credentials set):

```bash
python3 sca_cli.py proj.json import run uri_list -p filepath=./in.txt method=GET creds=admin
```

4. run sca with the `scan` command:

```bash
python3 sca_cli.py proj.json scan
```

5. run sca in param discovery mode (`analyze` command)

```bash
python3 sca_cli.py proj.json analyze
```

6. export coverage in LCOV fromat (for [Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) VSCode extension):

```bash
python3 sca_cli.py proj.json cov export lcov lcov.info
```

7. detect potential input getter wrapper functions:

```
python3 sca_cli.py proj.json param_usages wrappers
```

8. add wrapper function location (if any were detected and manually verified) to [`ParamUsagesConfig`](./sca/param_analyzer/impl/param_analyzer_config.py) for more readable code notes export

9. export detected param usages (for [Code Review](https://marketplace.visualstudio.com/items?itemName=d-koppenhagen.vscode-code-review) VSCode extension):

```bash
python3 sca_cli.py proj.json param_usages note # syncs param usages with code notes
python3 sca_cli.py proj.json notes export codereview code-review.csv # exports code notes
```