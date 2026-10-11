# SCA

`sca` module is implemented as a set of modules (./core/module_base.py:ModuleBase) that perform vaios tasks:

|#|module|path|dependencies|description|
|-|-|-|-|-|
|1|ModuleBase|./core|-|provides core facilities for other modules - dependency injector (InjectorBase)|
|2|ConfigModuleBase|./config|-|provides configuration storage|
|3|LoggingModuleBase|./logging|2|logging API|
|4|BlobStoreBase|./blob_store|-|provides object storage|
|5|InputManagerModuleBase|./input|4|provides functionality for input (HTTP request) management (import)|
|6|CoverageManagerModuleBase|./coverage|3,4|implements code coverage tracing|
|7|ParamUsagesModuleBase|./param_usage|5|aggregates pram usages from instrumentation modules|
|8|ProjectReaderModuleBase|./project_reader|2|provides access to project code base|
|9|ParamAnalyzerModuleBase|./param_analyzer|5,7,8|implements analyzes of input parameter usage in application attack surface|
|10|CodeNotesModuleBase|./code_notes_module|4,5|assign notes (points of interests) to application code base (e.g. cases of input parameters usage)|
|11|ScannerModuleBase|./scanner|4,5|sends inputs into application stand|
|12|ScanInstrumentationModuleBase|./scanner|4,5,7,9,10|collects data from implants during scan process (integrates Scanner module with PHP implant via [PhpCoverageCollectionInstrumentationModule](./scanner/impl/scan_instarumentation_modules/php_coverage_collection_instrumentation_module.py))|
|13|SurfScanModule|./surfscan_module.py|6,7,10,11|a facade that provides access to the core capabilities of SCA|

## SCA [CLI](./CLI.py)

Implements CLI interface for SCA