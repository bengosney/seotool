class EngineException(Exception):
    pass


class EngineUninitialized(EngineException):
    pass


class EngineResultFailed(EngineException):
    pass
