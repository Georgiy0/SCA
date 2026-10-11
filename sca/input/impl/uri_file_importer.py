import os
from typing import Dict
from urllib.parse import urlsplit, parse_qs

from ..input_importer_base import InputImporterBase
from ..error import InputImportError
from ..entity import InputInfo, InputParam, ParamType

class UriFileImporter(InputImporterBase):
    """Implements HTTP inputs import from text file with URI list.
    """
    
    cName = "uri_list"
    cFilePathParamName = "filepath"
    cHttpMethoParamName = "method"
    cCredsNameParamName = "creds"

    @property
    def Name(self):
        return UriFileImporter.cName
    
    def __get_param(self, params: Dict[str,str], pname: str) -> str:
        if pname not in params:
            raise InputImportError(f"missing '{pname}' param")
        return params[pname]

    def __get_param_or_default(self, params: Dict[str,str], pname: str, default: str | None = None) -> str:
        if pname not in params:
            return default
        return params[pname]

    def import_inputs(self, params):
        filepath = self.__get_param(params, UriFileImporter.cFilePathParamName)
        if not os.path.isfile(filepath):
            raise InputImportError(f"invalid file path '{filepath}'")

        method = self.__get_param_or_default(params, UriFileImporter.cHttpMethoParamName, "GET")
        creds_name = self.__get_param_or_default(params, UriFileImporter.cCredsNameParamName, None)
        creds_param = []
        if creds_name is not None:
            creds_param = [InputParam(param_type=ParamType.CREDS, name="", value=creds_name)]

        with open(filepath, 'r', encoding='utf-8') as fp:
            lines = fp.read().split('\n')
        results = []
        for i in range(len(lines)):
            cur_line = lines[i]
            if cur_line == "":
                continue
            uri = urlsplit(cur_line)
            uri_path = uri.path
            if uri_path.startswith("."):
                uri_path = uri_path.strip(".")
            uri_param = InputParam(param_type=ParamType.URI, name="", value=uri_path)

            parsed_dict = parse_qs(uri.query)
            params = [InputParam(param_type=ParamType.QUERY, name=e[0], value=e[1][0]) for e in parsed_dict.items()]

            results.append(InputInfo(id="None", params=[
                uri_param,
                InputParam(param_type=ParamType.METHOD, name="", value=method)
            ] + params + creds_param))
        return results
        

