import argparse
import sys
import traceback

from .surfscan_module import SurfScanModule
from .input import InputImportError, ParamType
from .param_analyzer import ParamAnalyzerObserverBase
from .core import ScaError

class CLIParamAnalyzerObserver(ParamAnalyzerObserverBase):
    def __init__(self, iteration: int, update_frequence: int):
        super().__init__()
        self.__iteration = iteration
        self.__freq = update_frequence
    
    def __clear_lines(self, n: int) -> None:
        sys.stdout.write(f"\033[F\033[K" * n)
    
    def update_status(self, status):
        self.__clear_lines(6)
        uri = status.current_input.get_param_of_type_or_default(ParamType.URI, default="NO URI")
        print(f"PARAM USAGE ANALYSIS (iteration {self.__iteration}):")
        print(f"- new inputs discovered: {status.new_cnt}")
        print(f"- unique param usages: {status.unique_params_cnt} / {status.unique_params_total}")
        print(f"- current param: {status.current_param.name} ({status.current_param.param_type})")
        print(f"- current URI: {uri}")
        print(f"- current candidates: {status.new_candidates_tested} / {status.new_candidates}")

    def update_frequence(self):
        return self.__freq


class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, val = value.split('=')
            getattr(namespace, self.dest)[key] = val

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("project", help="Project anme", type=str)
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    parser_init = subparsers.add_parser("init", help="Init project")

    parser_import = subparsers.add_parser("import", help="Import intputs")

    import_subparsers = parser_import.add_subparsers(dest="import_command", required=True, help="Import commands")
    import_list_parser = import_subparsers.add_parser("list", help="List importers")
    import_do_parser = import_subparsers.add_parser("run", help="Run import")
    import_do_parser.add_argument("importer", help="importer name", type=str)
    import_do_parser.add_argument("-p", "--params", nargs='*', action=ParseKwargs)

    parser_scan = subparsers.add_parser("scan", help="Run input scan")

    parser_cov = subparsers.add_parser("cov", help="Coverage")
    parser_cov_subparsers = parser_cov.add_subparsers(dest="cov_command", required=True, help="Coverage commands")
    
    parser_cov_list = parser_cov_subparsers.add_parser("list", help="List available exporters")
    parser_cov_export = parser_cov_subparsers.add_parser("export", help="Export coverage")
    parser_cov_export.add_argument("exporter_name", help="Exporter name", type=str)
    parser_cov_export.add_argument("output_path", help="Output path", type=str)
    
    parser_cov_stats = parser_cov_subparsers.add_parser("stats", help="Get coverage stats")

    parser_notes = subparsers.add_parser("notes", help="Code notes")
    parser_notes_subparsers = parser_notes.add_subparsers(dest="notes_command", required=True, help="Notes commands")

    parser_notes_list = parser_notes_subparsers.add_parser("list", help="List available exporters")
    parser_notes_export = parser_notes_subparsers.add_parser("export", help="Export notes")
    parser_notes_export.add_argument("exporter_name", help="Exporter name", type=str)
    parser_notes_export.add_argument("output_path", help="Output path", type=str)
    
    parser_analyze = subparsers.add_parser("analyze", help="Param usage analysis")
    
    parser_trigger = subparsers.add_parser("trigger", help="Trigger line by input")
    parser_trigger.add_argument("file", help="File path", type=str)
    parser_trigger.add_argument("line", help="Line in file", type=int)
    
    param_usages_parser = subparsers.add_parser("param_usages", help="Analzye param usages")
    param_usages_subparses = param_usages_parser.add_subparsers(dest="param_usages_command", help="Param usages command", required=True)
    param_usages_graph_parser = param_usages_subparses.add_parser("graph", help="Get param usages traces graph (in DOT format)")
    param_usages_graph_parser.add_argument("out", help="Output path for DOT file", type=str)
    param_usages_subparses.add_parser("wrappers", help="Get param usage wrapper candidates")
    param_usages_subparses.add_parser("note", help="Add param usages to code notes")

    return parser.parse_args() 

def get_surf_scan_module(project: str) -> SurfScanModule:
    surf_scan_module = SurfScanModule(project)
    return surf_scan_module

def do_import(surf_scan_module: SurfScanModule, args: argparse.Namespace) -> int:
    if args.import_command == "list":
        importers = surf_scan_module.InputManger.get_importers()
        print(f"Available importers:")
        for importer in importers:
            print(f"\t- {importer.Name}")
        return 0
    elif args.import_command == "run":
        importers = surf_scan_module.InputManger.get_importers()
        selected_importer = [i for i in importers if i.Name == args.importer]
        if len(selected_importer) != 1:
            print(f"[!] Invalid importer name")
            return 1
        importer = selected_importer[0]
        params = {} if args.params is None else args.params
        try:
            surf_scan_module.InputManger.import_inputs(importer, params)
        except InputImportError as ie:
            print(f"[!] Importer params error: {ie.Message}")
            return 1
        return 0
    else:
        print(f"Invalid import command")
        return 1
    
def do_scan(surf_scan_module: SurfScanModule, args: argparse.Namespace) -> int:
    surf_scan_module.run()
    return 0

def do_cov(surf_scan_module: SurfScanModule, args: argparse.Namespace) -> int:
    if args.cov_command == "export":
        surf_scan_module.CoverageManager.export_coverage(args.exporter_name, args.output_path)
        return 0
    elif args.cov_command == "list":
        exporters = surf_scan_module.CoverageManager.get_exporters()
        print(f"[*] Coverage exporters:")
        for exporter in exporters:
            print(f"\t- {exporter.Name}")
        return 0
    elif args.cov_command == "stats":
        stats = surf_scan_module.CoverageManager.get_stats()
        print(f"[*] Coverage stats:")
        print(f"\t- FILES: {stats.files_cnt}")
        print(f"\t- LINES: {stats.lines_cnt}")
        return 0
    else:
        print(f"Invalid cov command")
        return 1
    return 0

def do_notes(surf_scan_module: SurfScanModule, args: argparse.Namespace) -> int:
    if args.notes_command == "export":
        surf_scan_module.CodeNoteModule.export(args.exporter_name, args.output_path)
        return 0
    elif args.notes_command == "list":
        exporters = surf_scan_module.CodeNoteModule.get_exporters()
        print(f"[*] Notes exporters:")
        for exporter in exporters:
            print(f"\t- {exporter.Name}")
        return 0
    else:
        print(f"Invalid notes command")
        return 1
    return 0

def do_analyze(surf_scan_module: SurfScanModule, args: argparse.Namespace) -> int:
    iteration = 1
    print("\n"*6)
    while True:
        observer = CLIParamAnalyzerObserver(iteration, 10)
        new_cnt = surf_scan_module.ParamAnalyzerModule.analyze(observer)
        if new_cnt == 0:
            break
        iteration += 1
    return 0

def do_trigger(surf_scan_module: SurfScanModule, args: argparse.Namespace) -> int:
    if not surf_scan_module.trigger_line(args.file, args.line):
        print(f"[!] No inputs covered the given line")
        return 1
    else:
        print(f"[+] Sent input to trigger line")
        return 0
    
def param_usages_get_trace_graph(surf_scan_module: SurfScanModule, args: argparse.Namespace) -> int:
    param_usages = surf_scan_module.ParamUsagesModule
    
    dot_source = param_usages.get_param_usage_traces_dot_graph()
    
    with open(args.out, 'w', encoding='utf-8') as fp:
        fp.write(dot_source)
        
    print(f"[+] Saved dot graph into '{args.out}'")
    return 0
    
def param_usages_get_wrapper_candidates(surf_scan_module: SurfScanModule) -> int:
    param_usages = surf_scan_module.ParamUsagesModule
    
    candidates = param_usages.get_param_getter_wrapper_candidates()
    
    if not len(candidates):
        print(f"[*] No param usage wrapper candidates found")
        return 0
    
    print(f"[*] {len(candidates)} param usage wrapper candidates found:")
    for candidate, param_types in candidates.items():
        param_types_str = ','.join(param_types)
        print(f"\t- {candidate} - wrappes access to parameters of types: {param_types_str}")
    return 0

def param_usages_add_to_notes(surf_scan_module: SurfScanModule) -> int:
    param_usages = surf_scan_module.ParamUsagesModule
    added = param_usages.add_param_usages_to_notes()
    print(f"[+] Added {added} param usages to code notes.")
    return 0

def do_param_usages(surf_scan_module: SurfScanModule, args: argparse.Namespace) -> int:
    if args.param_usages_command == "graph":
        return param_usages_get_trace_graph(surf_scan_module, args)
    elif args.param_usages_command == "wrappers":
        return param_usages_get_wrapper_candidates(surf_scan_module)
    elif args.param_usages_command == "note":
        return param_usages_add_to_notes(surf_scan_module)
    
def main() -> int:
    args = parse_args()

    try:
        surf_scan_module = get_surf_scan_module(args.project)
        surf_scan_module.init()

        if args.command == "init":
            return 0
        elif args.command == "import":
            return do_import(surf_scan_module, args)
        elif args.command == "scan":
            return do_scan(surf_scan_module, args)
        elif args.command == "cov":
            return do_cov(surf_scan_module, args)
        elif args.command == "notes":
            return do_notes(surf_scan_module, args)
        elif args.command == "analyze":
            return do_analyze(surf_scan_module, args)
        elif args.command == "param_usages":
            return do_param_usages(surf_scan_module, args)
        elif args.command == "trigger":
            return do_trigger(surf_scan_module, args)
    except ScaError as sca_error:
        print(f"[!] Error: {sca_error.Message}")
        surf_scan_module.Logger.log_error(f"Exception ({type(sca_error)}): {sca_error.Message}. Traceback:\n{traceback.format_exc()}")
        
    finally:
        surf_scan_module.deinit()

def cli_run() -> None:
    sys.exit(main())

