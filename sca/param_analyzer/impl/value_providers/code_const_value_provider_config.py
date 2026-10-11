from ....config import ConfigBase

class CodeConstValueProviderConfig(ConfigBase):
    """Configuration for code const value provider.
    
    Attributres:
        only_param_usage_file (bool) - limits code analysis to a single file (at the top of param usage call stack)
        min_const_length (int), max_const_length (int) - limits extracted consts by string length
        forbidden_chars (str) - blacklist of symbols to filter extracted consts
        use_re (bool) - use provdied regular expression to filter extracted consts
        re (str) - regular expression to filter extracted consts
    """
    
    only_param_usage_file: bool
    min_const_length: int
    max_const_length: int
    forbidden_chars: str
    use_re: bool
    re: str
    
    @staticmethod
    def default() -> 'CodeConstValueProviderConfig':
        return CodeConstValueProviderConfig(only_param_usage_file=True,\
            min_const_length=4,\
            max_const_length=12,\
            forbidden_chars="",\
            use_re=False,\
            re="")
    
    