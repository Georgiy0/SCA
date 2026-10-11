import os
from pydantic import TypeAdapter, BaseModel
from typing import Dict

coverage_type_adapter = TypeAdapter(Dict[str, Dict[str, int]])

from ....input import InputParam, ParamType
from ....config import ConfigModuleBase
from ....coverage import CoverageManagerModuleBase, CoverageInfo
from ....input import InputInfo, InputParam
from ....core import ScaError

from ...scan_instrumentation_module_base import ScanInstrumentationModuleBase
from ...entity import InstrumentationCapability, Stand
from ...sender_base import SenderBase

from .php_instrumentation_config import PhpInstrumentationConfig

class PhpCovReport(BaseModel):
    """PHP coverage report model.
    
    Attributes:
        URI (str) - request URI that triggered coverage collection
        coverage (str) - coverage id
        id (str) - report id
    """
    
    URI: str
    coverage: str
    id: str
    
    
class PhpCoverageCollectionInstrumentationModule(ScanInstrumentationModuleBase):
    """Coverage collection instrumentation module.
    
    Prepares request for coverage collection via SCA PHP implant.
    
    Collects coverage report.
    """
    
    cInstrumentationModuleName = "PHPCOV"
    cInputIdParamName = "__php_iid"
    cCovCollectParamCanaryName = "__php_cov"
    cCovReportSuffix = ".cov"
    cCovReportType = "cov_report"
    cCovType = "cov"

    def __init__(self):
        super().__init__()
        self.__config: PhpInstrumentationConfig = None
        self.__cov_manager: CoverageManagerModuleBase = None

    @property
    def Name(self) -> str:
        return PhpCoverageCollectionInstrumentationModule.cInstrumentationModuleName
    
    @property
    def Capabilities(self):
        return [InstrumentationCapability.COV]
    
    def init_module(self):
        super().init_module()
        config_module = self.Injector.get_module(ConfigModuleBase)
        self.__cov_manager = self.Injector.get_module(CoverageManagerModuleBase)
        self.__config = config_module.get_config_or_default(PhpInstrumentationConfig, PhpInstrumentationConfig.default())
        if self.__config.fetch_reports_locally:
            path_error = False
            if not os.path.isdir(self.__config.coverage_path):
                path_error = True
                self.Logger.log_error(f"Invalid coverage dir path ({self.__config.coverage_path})")
            if not os.path.isdir(self.__config.report_path):
                path_error = True
                self.Logger.log_error(f"Invalid reports dir path ({self.__config.report_path})")
            if path_error:
                raise ScaError(f"Invalid directory path")
    
    def deinit_module(self):
        pass

    def pre_send_action(self, input_id, input, sender, stand) -> None:
        input_id_value = input.get_param_or_default(ParamType.QUERY, PhpCoverageCollectionInstrumentationModule.cInputIdParamName)
        if input_id_value is None:
            input.params.append(InputParam(
                param_type=ParamType.QUERY, 
                name=PhpCoverageCollectionInstrumentationModule.cInputIdParamName,
                value=input_id))
        input.params.append(InputParam(
            param_type=ParamType.QUERY,
            name=PhpCoverageCollectionInstrumentationModule.cCovCollectParamCanaryName,
            value="1"
        ))
        
    def __load_report(self, input_id, report_suffix: str) -> PhpCovReport | None:
        report_path = os.path.join(self.__config.report_path, f"{input_id}{report_suffix}.json")
        report = None
        if os.path.isfile(report_path):
            with open(report_path, 'rb') as fp:
                report = PhpCovReport.model_validate_json(fp.read())
        return report
    
    def __download_report(self, stand: Stand, sender: SenderBase, input_id, report_type: str) -> PhpCovReport | None:
        dl_input = InputInfo(params=[
            InputParam(param_type=ParamType.METHOD, name="", value="GET"),
            InputParam(param_type=ParamType.URI, name="", value=self.__config.php_implant_uri),
            InputParam(param_type=ParamType.QUERY, name="__php_dl_type", value=report_type),
            InputParam(param_type=ParamType.QUERY, name="__php_dl_id", value=input_id)
        ])
        status, report = sender.send_raw(stand, dl_input)
        if status != 200:
            return None
        report = PhpCovReport.model_validate_json(report)
        return report
        
    def __collect_coverage(self, coverage_id, input_id) -> None:
        coverage_path = os.path.join(self.__config.coverage_path, f"{coverage_id}.json")
        if os.path.isfile(coverage_path):
            with open(coverage_path, 'rb') as fp:
                try:
                    coverage_report = coverage_type_adapter.validate_json(fp.read())
                    coverage_info = CoverageInfo(
                        coverage_id=coverage_id, 
                        input_id=input_id,
                        coverage=coverage_report)
                    self.__cov_manager.add_coverage(coverage_info)
                except Exception as e:
                    self.Logger.log_warning(f"[!] Failed to process coverage report '{coverage_path}'")
                    
    def __download_coverage(self, coverage_id, input_id, sender, stand) -> None:
        dl_input = InputInfo(params=[
            InputParam(param_type=ParamType.METHOD, name="", value="GET"),
            InputParam(param_type=ParamType.URI, name="", value=self.__config.php_implant_uri),
            InputParam(param_type=ParamType.QUERY, name="__php_dl_type", value=PhpCoverageCollectionInstrumentationModule.cCovType),
            InputParam(param_type=ParamType.QUERY, name="__php_dl_id", value=coverage_id)
        ])
        status, report = sender.send_raw(stand, dl_input)
        if status != 200:
            return
        try:
            coverage_report = coverage_type_adapter.validate_json(report)
            coverage_info = CoverageInfo(
                coverage_id=coverage_id, 
                input_id=input_id,
                coverage=coverage_report)
            self.__cov_manager.add_coverage(coverage_info)
        except Exception as e:
            self.Logger.log_warning(f"[!] Failed to process coverage report for input id '{input_id}'")
        
    def post_send_action(self, input_id, input, output, sender, stand) -> None:
        if self.__config.fetch_reports_locally:
            report = self.__load_report(input_id, PhpCoverageCollectionInstrumentationModule.cCovReportSuffix)
        else:
            report = self.__download_report(stand, sender, input_id, PhpCoverageCollectionInstrumentationModule.cCovReportType)
        if report is None:
            self.Logger.log_warning(f"no coverage report for iid '{input_id}'")
            return
        if self.__config.fetch_reports_locally:
            self.__collect_coverage(report.coverage, input_id)
        else:
            self.__download_coverage(report.coverage, input_id, sender, stand)

    def populate_scan_report(self, input_id, input, output, report, sender, stand):
        if self.__config.fetch_reports_locally:
            cov_report = self.__load_report(input_id, PhpCoverageCollectionInstrumentationModule.cCovReportSuffix)
        else:
            cov_report = self.__download_report(stand, sender, input_id, PhpCoverageCollectionInstrumentationModule.cCovReportType)
        if cov_report is None:
            return
        report.coverage_id = cov_report.coverage
        
        