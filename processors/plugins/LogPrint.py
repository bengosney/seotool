# First Party
from processors import hookimpl_processor


class LogPrint:
    @hookimpl_processor(trylast=True)
    def log(self, line):
        print(f"{line}")
        return True

    @hookimpl_processor(trylast=True)
    def log_error(self, line):
        return self.log(line)
