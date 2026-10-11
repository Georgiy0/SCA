import os
from pydantic import BaseModel
from typing import Dict, List

from ....input import InputParam, ParamType, InputInfo
from ....config import ConfigModuleBase
from ....param_usage import ParamUsagesModuleBase, TraceFrame
from ....param_usage import ParamUsageInfo

from ...scan_instrumentation_module_base import ScanInstrumentationModuleBase
from ...entity import InstrumentationCapability, Stand
from ...sender_base import SenderBase

from .php_instrumentation_config import PhpInstrumentationConfig

class PhpParamsReport(BaseModel):
    """PHP params usage report model.
    
    Attributes:
        URI (str) - request URI that triggered coverage collection
        id (str) - report id
        used_input (dict[str,dict[str,dict[str,list[TraceFrame]]]]) - information about params used during input processing
    """
    
    URI: str
    id: str
    used_input: Dict[str, Dict[str, Dict[str, List[TraceFrame]]]]
    

class PhpParamsCollectionInstrumentationModule(ScanInstrumentationModuleBase):
    """Implements param usage collection instrumentation module.
    
    Prepares input for param usage collection (by adding marker parameters for SCA PHP implant).
    
    Retrieves and parses param usage report.
    """
    
    cInstrumentationModuleName = "PHPPARAMS"
    cInputIdParamName = "__php_iid"
    cPhpParams = "__php_params"
    cReportSuffix = ".params"
    cReportType = "params_report"

    cParamTypeMapping = {
        "REQUEST": ParamType.QUERY,
        "GET": ParamType.QUERY,
        "POST": ParamType.FORM,
        "COOKIE": ParamType.COOKIE,
        "HEADER": ParamType.HEADER,
        "FILE": ParamType.FORM_FILE,
        "URI": ParamType.URI,
        "QUERY_STRING": ParamType.QUERY,
        "PATH_INFO": ParamType.PATH_INFO,
        
        "AUTH_DIGEST": ParamType.AUTH_DIGEST,
        "HTTP_AUTH_USER": ParamType.HTTP_AUTH_USER,
        "HTTP_AUTH_PASSWORD": ParamType.HTTP_AUTH_PASSWORD,
        
        "SOCKET_ADDR": ParamType.SOCKET_ADDR,
        "SOCKET_PORT": ParamType.SOCKET_PORT
    }

    def __init__(self):
        super().__init__()
        self.__config: PhpInstrumentationConfig = None
        self.__param_usage_module: ParamUsagesModuleBase = None

    @property
    def Name(self) -> str:
        return PhpParamsCollectionInstrumentationModule.cInstrumentationModuleName
    
    @property
    def Capabilities(self):
        return [InstrumentationCapability.PARAM_USAGE]
    
    def init_module(self):
        super().init_module()
        config_module = self.Injector.get_module(ConfigModuleBase)
        self.__param_usage_module = self.Injector.get_module(ParamUsagesModuleBase)
        self.__config = config_module.get_config_or_default(PhpInstrumentationConfig, PhpInstrumentationConfig.default())
    
    def deinit_module(self):
        pass

    def pre_send_action(self, input_id, input, sender, stand):
        input_id_value = input.get_param_or_default(ParamType.QUERY, PhpParamsCollectionInstrumentationModule.cInputIdParamName)
        if input_id_value is None:
            input.params.append(InputParam(
                param_type=ParamType.QUERY, 
                name=PhpParamsCollectionInstrumentationModule.cInputIdParamName,
                value=input_id))
        input.params.append(InputParam(
            param_type=ParamType.QUERY,
            name=PhpParamsCollectionInstrumentationModule.cPhpParams,
            value="1"
        ))
        
    def __load_report(self, input_id: str, report_suffix: str) -> PhpParamsReport | None:
        report_path = os.path.join(self.__config.report_path, f"{input_id}{report_suffix}.json")
        report = None
        if os.path.isfile(report_path):
            with open(report_path, 'rb') as fp:
                try:
                    report = PhpParamsReport.model_validate_json(fp.read())
                except Exception as e:
                    self.Logger.log_error(f"[!] Error parsing params report '{report_path}'")
                    raise e
        return report
    
    def __download_report(self, input_id: str, report_type: str, sender: SenderBase, stand: Stand) -> PhpParamsReport | None:
        dl_input = InputInfo(params=[
            InputParam(param_type=ParamType.METHOD, name="", value="GET"),
            InputParam(param_type=ParamType.URI, name="", value=self.__config.php_implant_uri),
            InputParam(param_type=ParamType.QUERY, name="__php_dl_type", value=report_type),
            InputParam(param_type=ParamType.QUERY, name="__php_dl_id", value=input_id)
        ])
        status, report = sender.send_raw(stand, dl_input)
        if status != 200:
            return None
        try:
            report = PhpParamsReport.model_validate_json(report)
        except Exception as e:
            self.Logger.log_error(f"[!] Error parsing params report for iid '{input_id}'")
            raise e
        return report
            
    def __transform_php_header_name(self, header_in: str) -> str:
        header_parts = header_in[len("HTTP_"):].split("_")
        return '-'.join(hp.capitalize() for hp in header_parts)

    def __collect_param_usage(self, input_id: str, report: PhpParamsReport) -> None:
        param_usages = self.__format_param_usage(input_id, report)
        for pu in param_usages.values():
            self.__param_usage_module.add_param_usage(input_id, pu.param, pu.trace)
            
    def __format_param_usage(self, input_id: str, report: PhpParamsReport) -> Dict[str, ParamUsageInfo]:
            param_usages: Dict[str, ParamUsageInfo] = {}
            for ptype, pname_to_usage in report.used_input.items():
                if ptype in PhpParamsCollectionInstrumentationModule.cParamTypeMapping:
                    param_type = PhpParamsCollectionInstrumentationModule.cParamTypeMapping[ptype]
                    param_names = pname_to_usage.keys()
                    for pn in param_names:
                        orig_pn = pn
                        if param_type == ParamType.HEADER:
                            pn = self.__transform_php_header_name(pn)
                        input_param = InputParam(param_type=param_type, name=pn)
                        usages = pname_to_usage[orig_pn].values()
                        for usage_trace in usages:
                            param_usage_info = ParamUsageInfo(
                                analyzed=False,
                                param=input_param,
                                trace=usage_trace
                            )
                            param_id = param_usage_info.get_hash()
                            if param_id not in param_usages:
                                param_usages[param_id] = param_usage_info
            return param_usages

    def post_send_action(self, input_id, input, output, sender, stand) -> None:
        if self.__config.fetch_reports_locally:
            report = self.__load_report(input_id, PhpParamsCollectionInstrumentationModule.cReportSuffix)
        else:
            report = self.__download_report(input_id, PhpParamsCollectionInstrumentationModule.cReportType, sender, stand)
        if report is None:
            self.Logger.log_warning(f"no params report for iid '{input_id}'")
            return
        self.__collect_param_usage(input_id, report)

    def populate_scan_report(self, input_id, input, output, report, sender, stand):
        if self.__config.fetch_reports_locally:
            params_report = self.__load_report(input_id, PhpParamsCollectionInstrumentationModule.cReportSuffix)
        else:
            params_report = self.__download_report(input_id, PhpParamsCollectionInstrumentationModule.cReportType, sender, stand)
        if params_report is None:
            self.Logger.log_warning(f"no params report for iid '{input_id}'")
            return
        param_usages = self.__format_param_usage(input_id, params_report)
        report.param_usages = param_usages
        
        