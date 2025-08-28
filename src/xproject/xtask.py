from abc import ABC

from xproject.xlogger import get_logger
from xproject.xmixins.xdir_path_mixin import DirPathMixin
from xproject.xmixins.xintrospection_mixin import IntrospectionMixin
from xproject.xmixins.xobject_mixins.xcontext_manager_object_mixin import ContextManagerObjectMixin
from xproject.xmixins.xrun_mixin import RunMixin


class Task(ContextManagerObjectMixin, RunMixin, DirPathMixin, IntrospectionMixin, ABC):
    logger = get_logger()
