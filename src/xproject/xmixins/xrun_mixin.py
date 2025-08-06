from abc import ABC, abstractmethod
from typing import Any

from xproject.xlogger import Logger


class RunMixin(ABC):
    logger: Logger

    @abstractmethod
    def action(self, *args, **kwargs) -> Any:
        pass

    def run_ok_method(self, result: Any) -> Any:
        pass

    def run_error_method(self, exception: Exception) -> bool | None:
        """

        :param exception:
        :return: None => raise exception
                 True => ignore exception and no logger
                 False => ignore exception and logger
        """
        pass

    def run(self, *args: Any, **kwargs: Any, ) -> Any:
        try:
            result = self.action(*args, **kwargs)
        except Exception as e:
            ret = self.run_error_method(e)
            if ret is None:
                raise e
            if ret is True:
                pass
            if ret is False:
                self.logger.exception(e)
        else:
            self.run_ok_method(result)
            return result
        return None

    def loop_run(self, *args: Any, **kwargs: Any) -> None:
        run_times = 0
        while True:
            run_times += 1
            self.logger.debug(f"loop_run run_times: {run_times} start")
            self.run(*args, **kwargs)
            self.logger.debug(f"loop_run run_times: {run_times} end")
