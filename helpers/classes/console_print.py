import os
import sys
import traceback


class ConsolePrint:
    class Style:
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        UNDERLINE = '\033[4m'
        RESET = '\033[0m'

    def _make_print(self, title, message, color=None):
        os.system("")

        if color is None:
            color = self.Style.RESET

        if isinstance(message, str):
            print(f'{color}{title}: {self.Style.RESET}{message}')
        else:
            try:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(f'{color}{title}: {self.Style.RESET}{message} | line: {exc_tb.tb_lineno}')
            except Exception:
                print(f'{color}{title}: {self.Style.RESET}{message}')
            print(traceback.format_exc())

    def log(self, title, message):
        return self._make_print(title, message)

    def success(self, title, message):
        return self._make_print(title, message, self.Style.GREEN)

    def info(self, title, message):
        return self._make_print(title, message, self.Style.BLUE)

    def error(self, title, message):
        return self._make_print(title, message, self.Style.RED)

    def warning(self, title, message):
        return self._make_print(title, message, self.Style.YELLOW)
