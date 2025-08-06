from abc import ABC

from xproject.xmixins.xobject_mixins.xcontext_manager_object_mixin import ContextManagerObjectMixin
from xproject.xmixins.xrun_mixin import RunMixin


class Handler(ContextManagerObjectMixin, RunMixin, ABC):
    pass
