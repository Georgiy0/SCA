from typing import List

from ...config import ConfigBase

from ..entity import Stand, CredentialsSet

class ScannerConfig(ConfigBase):
    """Scanner module configuration.
    
    Attributes:
        stand (Stand) - target stand information
        sender_name (str) - sender module name
        insturmentation_modules (list[str]) - names of instrumentation modules to use
    """
    
    stand: Stand
    sender_name: str
    insturmentation_modules: List[str]

    @staticmethod
    def default() -> 'ScannerConfig':
        return ScannerConfig(
            stand=Stand(
                base_uri="http://base.uri",
                domain="base.uri",
                creds=[CredentialsSet(name="samplecreds", username="user", password="pwd")]
            ),
            sender_name="sample_sender_name",
            insturmentation_modules=["INST_MOD_1", "INST_MOD_2"]
        )

