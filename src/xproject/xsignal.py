import collections.abc as c
import typing as t
from inspect import iscoroutinefunction, signature

import blinker


class Signal(blinker.Signal):
    @staticmethod
    def _get_filter_kwargs(sender, receiver, **kwargs):
        kwargs.setdefault("sender", sender)
        sig = signature(receiver)
        return {k: v for k, v in kwargs.items() if k in sig.parameters}

    def send(
            self,
            sender: t.Any | None = None,
            /,
            *,
            _async_wrapper: c.Callable[
                                [c.Callable[..., c.Coroutine[t.Any, t.Any, t.Any]]], c.Callable[..., t.Any]
                            ]
                            | None = None,
            **kwargs: t.Any,
    ) -> list[tuple[c.Callable[..., t.Any], t.Any]]:
        """Call all receivers that are connected to the given ``sender``
        or :data:`ANY`. Each receiver is called with ``sender`` as a positional
        argument along with any extra keyword arguments. Return a list of
        ``(receiver, return value)`` tuples.

        The order receivers are called is undefined, but can be influenced by
        setting :attr:`set_class`.

        If a receiver raises an exception, that exception will propagate up.
        This makes debugging straightforward, with an assumption that correctly
        implemented receivers will not raise.

        :param sender: Call receivers connected to this sender, in addition to
            those connected to :data:`ANY`.
        :param _async_wrapper: Will be called on any receivers that are async
            coroutines to turn them into sync callables. For example, could run
            the receiver with an event loop.
        :param kwargs: Extra keyword arguments to pass to each receiver.

        .. versionchanged:: 1.7
            Added the ``_async_wrapper`` argument.
        """
        if self.is_muted:
            return []

        results = []

        for receiver in self.receivers_for(sender):
            filter_kwargs = self._get_filter_kwargs(sender, receiver, **kwargs)

            if iscoroutinefunction(receiver):
                if _async_wrapper is None:
                    raise RuntimeError("Cannot send to a coroutine function.")

                result = _async_wrapper(receiver)(**filter_kwargs)
            else:
                result = receiver(**filter_kwargs)

            results.append((receiver, result))

        return results

    async def send_async(
            self,
            sender: t.Any | None = None,
            /,
            *,
            _sync_wrapper: c.Callable[
                               [c.Callable[..., t.Any]], c.Callable[..., c.Coroutine[t.Any, t.Any, t.Any]]
                           ]
                           | None = None,
            **kwargs: t.Any,
    ) -> list[tuple[c.Callable[..., t.Any], t.Any]]:
        """Await all receivers that are connected to the given ``sender``
        or :data:`ANY`. Each receiver is called with ``sender`` as a positional
        argument along with any extra keyword arguments. Return a list of
        ``(receiver, return value)`` tuples.

        The order receivers are called is undefined, but can be influenced by
        setting :attr:`set_class`.

        If a receiver raises an exception, that exception will propagate up.
        This makes debugging straightforward, with an assumption that correctly
        implemented receivers will not raise.

        :param sender: Call receivers connected to this sender, in addition to
            those connected to :data:`ANY`.
        :param _sync_wrapper: Will be called on any receivers that are sync
            callables to turn them into async coroutines. For example,
            could call the receiver in a thread.
        :param kwargs: Extra keyword arguments to pass to each receiver.

        .. versionadded:: 1.7
        """
        if self.is_muted:
            return []

        results = []

        for receiver in self.receivers_for(sender):
            filter_kwargs = self._get_filter_kwargs(sender, receiver, **kwargs)

            if not iscoroutinefunction(receiver):
                if _sync_wrapper is None:
                    raise RuntimeError("Cannot send to a non-coroutine function.")

                result = await _sync_wrapper(receiver)(**filter_kwargs)
            else:
                result = await receiver(**filter_kwargs)

            results.append((receiver, result))

        return results


__all__ = [
    "Signal",
]
