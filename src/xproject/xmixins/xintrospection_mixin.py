from inspect import currentframe


class IntrospectionMixin:
    def __repr__(self) -> str:
        return self.__class__.__name__

    __str__ = __repr__

    @property
    def method_name(self) -> str:
        frame = currentframe().f_back
        return frame.f_code.co_name

    @property
    def method_qualname(self) -> str:
        frame = currentframe().f_back
        method_name = frame.f_code.co_name
        method = getattr(self, method_name)
        return method.__qualname__
