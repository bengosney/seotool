# First Party
from processors import hookimpl_processor


class LogPrint:
    @hookimpl_processor(trylast=True)
    def log(self, line, style):
        print(f"{line}")
        return True
