# -*- coding: utf-8 -*-
"""
    energy
    ~~~~~~

    Energy system for social games such as FarmVille or The Sims Social.

    :copyright: (c) 2012-2013 by Heungsub Lee
    :license: BSD, see LICENSE for more details.
"""
from calendar import timegm
from datetime import datetime, timedelta
import sys
from time import gmtime, struct_time


__version__ = '0.1.8'
__all__ = ['Energy']


def timestamp(time=None, default_time_getter=gmtime):
    """Makes some timestamp.

    1. If you pass a :class:`datetime` object, it makes a timestamp from the
       argument.
    2. If you pass a timestamp(`int` or `float`), it just returns that.
    3. If you call it without parameter, it makes a timestamp from the result
       of `default_time_getter`.
    """
    if time is None:
        time = default_time_getter()
    if isinstance(time, datetime):
        return timegm(time.timetuple())
    elif isinstance(time, struct_time):
        return timegm(time)
    return int(time)


if sys.version_info < (2, 6):
    # A fallback of property under Python 2.6. The code is from
    # http://blog.devork.be/2008/04/xsetter-syntax-in-python-25.html
    class property(property):
        def __init__(self, fget, *args, **kwargs):
            self.__doc__ = fget.__doc__
            super(property, self).__init__(fget, *args, **kwargs)
        def setter(self, fset):
            ns = sys._getframe(1).f_locals
            for k, v in ns.iteritems():
                if v == self:
                    propname = k
                    break
            ns[propname] = property(self.fget, fset, self.fdel, self.__doc__)
            return ns[propname]


if not hasattr(timedelta, 'total_seconds'):
    # A fallback of timedelta.total_seconds under Python 2.7 and Python 3.1.
    def total_seconds(timedelta):
        ms, s, d = timedelta.microseconds, timedelta.seconds, timedelta.days
        return (ms + (s + d * 24 * 3600) * (10 ** 6)) / (10 ** 6)


class Energy(object):
    """A consumable and recoverable stuff in social gamers. Think over
    reasonable energy parameters for your own game. Energy may decide return
    period of your players.

    :param max: maximum energy
    :param recovery_interval: an interval in seconds to recover energy
    :type recovery_interval: number or ``timedelta``
    :param recovery_quantity: a quantity of once energy recovery. Defaults to
                              ``1``.
    :param future_tolerance: near seconds to ignore exception when used at the
                             future
    :param used: set this when retrieve an energy, otherwise don't touch
    :param used_at: set this when retrieve an energy, otherwise don't touch
    :type used_at: timestamp number or ``datetime``

    :raise TypeError: some argument isn't valid type
    """

    #: Quantity of used energy.
    used = 0

    #: A time when using the energy first.
    used_at = None

    def __init__(self, max, recovery_interval, recovery_quantity=1,
                 future_tolerance=None, used=used, used_at=used_at):
        if not isinstance(max, int):
            raise TypeError('max should be int')
        if not isinstance(recovery_quantity, int):
            raise TypeError('recovery_quantity should be int')
        if isinstance(recovery_interval, timedelta):
            try:
                recovery_interval = recovery_interval.total_seconds()
            except AttributeError:
                recovery_interval = total_seconds(recovery_interval)
        if not isinstance(recovery_interval, (int, float)):
            raise TypeError('recovery_interval should be number')
        self._max = max
        #: The interval in seconds to recover energy.
        self.recovery_interval = recovery_interval
        #: The quantity of once energy recovery.
        self.recovery_quantity = recovery_quantity
        #: The near seconds to ignore exception when used at the future.
        #:
        #: .. versionadded:: 0.1.3
        self.future_tolerance = future_tolerance
        self.used = used
        if used_at is not None:
            self.used_at = timestamp(used_at)

    @property
    def max(self):
        """The maximum energy."""
        return self._max

    @max.setter
    def max(self, max):
        """Configurates the maximum energy."""
        self.config(max=max)

    def _current(self, time=None):
        """Calculates the current internal energy.

        >>> energy = Energy(10, 300)
        >>> energy.use()
        >>> energy._current()
        9

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        if not self.used:
            return self.max
        current = self.max - self.used + self.recovered(time)
        return current

    def current(self, time=None):
        """Calculates the current presentative energy. This equivalents to
        casting to ``int`` but can work with specified time.

        >>> energy = Energy(10, 300)
        >>> energy.use()
        >>> energy.current()
        9
        >>> int(energy)
        9

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        return max(0, self._current(time))

    def debt(self, time=None):
        """Calculates the current energy debt.

        >>> energy = Energy(10, 300)
        >>> energy.debt()
        >>> energy.use(11, force=True)
        >>> energy.debt()
        1
        >>> energy.use(2, force=True)
        3

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        current = self._current(time)
        if current >= 0:
            return
        return -current

    def use(self, quantity=1, time=None, force=False):
        """Consumes the energy.

        :param quantity: quantity of energy to be used. Defaults to ``1``.
        :param time: the time when using the energy. Defaults to the present
                     time in UTC.
        :param force: force to use energy even if there is not enough energy.
        :raise ValueError: not enough energy
        """
        time = timestamp(time)
        current = self._current(time)
        if current < quantity and not force:
            raise ValueError('Not enough energy')
        if current - quantity < self.max <= current or force:
            self.used = quantity - current + self.max
            self.used_at = time
        else:
            self.used = self.max - current + self.recovered(time) + quantity

    def recover_in(self, time=None):
        """Calculates seconds to the next energy recovery. If the energy is
        full or over the maximum, this returns ``None``.

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        passed = self.passed(time)
        if passed is None or passed / self.recovery_interval >= self.used:
            return
        diff = self.recovery_interval - (passed % self.recovery_interval)
        current = self._current(time)
        if current < 0:
            return diff - current * self.recovery_interval
        return diff

    def recover_fully_in(self, time=None):
        """Calculates seconds to be recovered fully. If the energy is full or
        over the maximum, this returns ``None``.

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.

        .. versionadded:: 0.1.5
        """
        recover_in = self.recover_in(time)
        if recover_in is None:
            return
        to_recover = self.max - self.current()
        return recover_in + self.recovery_interval * (to_recover - 1)

    def recovered(self, time=None):
        """Calculates the recovered energy from the player used energy first.

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        passed = self.passed(time)
        if passed is None:
            return 0
        recovered = (int(passed / self.recovery_interval) *
                     self.recovery_quantity)
        return min(recovered, self.used)

    def passed(self, time=None):
        """Calculates the seconds passed from using the energy first.

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        :raise ValueError: used at the future
        """
        if self.used_at is None:
            return
        seconds = timestamp(time) - self.used_at
        if seconds < 0:
            if self.future_tolerance is not None and \
               abs(seconds) <= self.future_tolerance:
                return 0
            raise ValueError('Used at the future (+%.2f sec)' % -seconds)
        return seconds

    def set(self, quantity, time=None):
        """Sets the energy to the fixed quantity.

        >>> energy = Energy(10, 300)
        >>> print energy
        <Energy 10/10>
        >>> energy.set(3)
        >>> print energy
        <Energy 3/10 recover in 05:00>

        You can also set over the maximum when give bonus energy.

        >>> energy.set(15)
        >>> print energy
        <Energy 15/10>

        :param quantity: quantity of energy to be set
        :param time: the time when setting the energy. Defaults to the present
                     time in UTC.
        """
        if quantity >= self.max:
            self.used = self.max - quantity
            self.used_at = None
        else:
            self.use(self.current(time) - quantity)

    def reset(self, time=None):
        """Makes the energy to be full. Most social games reset energy when the
        player reaches higher level.

        :param time: the time when setting the energy. Defaults to the present
                     time in UTC.
        """
        return self.set(self.max, time)

    def config(self, max=None, recovery_interval=None, time=None):
        """Updates :attr:`max` or :attr:`recovery_interval`.

        :param max: quantity of maximum energy to be set
        :param time: the time when setting the energy. Defaults to the present
                     time in UTC.
        """
        if max is not None:
            if self.recover_in(time):
                self.used += max - self._max
            self._max = max
        if recovery_interval is not None:
            self.recovery_interval = recovery_interval

    def __int__(self, time=None):
        """Type-casting to ``int``."""
        return self.current(time)

    def __float__(self, time=None):
        """Type-casting to ``float``."""
        return float(self.__int__(time))

    def __nonzero__(self, time=None):
        """Type-casting to ``bool``."""
        return bool(self.__int__(time))

    # Python 3 accepts __bool__ instead of __nonzero__
    __bool__ = __nonzero__

    def __eq__(self, other, time=None):
        """Is current energy equivalent to the operand.

        :param other: the operand
        :type other: :class:`Energy` or number
        """
        if isinstance(other, type(self)):
            return self.__getstate__() == other.__getstate__()
        elif isinstance(other, (int, float)):
            return float(self.current(time)) == other
        return False

    def __lt__(self, other, time=None):
        """Is current energy less than the operand.

        :param other: the operand
        :type other: number

        .. versionadded:: 0.1.3
        """
        return self.current(time) < other

    def __le__(self, other, time=None):
        """Is current energy less than or equivalent to the operand.

        :param other: the operand
        :type other: number

        .. versionadded:: 0.1.3
        """
        return self.current(time) <= other

    def __gt__(self, other, time=None):
        """Is current energy greater than the operand.

        :param number other: the operand
        :type other: number

        .. versionadded:: 0.1.3
        """
        return self.current(time) > other

    def __ge__(self, other, time=None):
        """Is current energy greater than or equivalent to the operand.

        :param other: the operand
        :type other: number

        .. versionadded:: 0.1.3
        """
        return self.current(time) >= other

    def __iadd__(self, other, time=None):
        """Increases by the operand.

        .. versionadded:: 0.1.1
        """
        self.set(self.current(time) + other, time)
        return self

    def __isub__(self, other, time=None):
        """Decreases by the operand.

        .. versionadded:: 0.1.1
        """
        return self.__iadd__(-other, time)

    def __getstate__(self):
        return {'used': self.used,
                'used_at': self.used_at,
                'max': self.max,
                'recovery_interval': self.recovery_interval,
                'recovery_quantity': self.recovery_quantity,
                'future_tolerance': self.future_tolerance}

    def __setstate__(self, state):
        if isinstance(state, tuple):
            # saved under 0.1.2
            self._max = state[0]
            self.recovery_interval = state[1]
            self.recovery_quantity = state[2]
            self.used = state[3]
            self.used_at = state[4]
            return
        self.used = state['used']
        self.used_at = state['used_at']
        self._max = state['max']
        self.recovery_interval = state['recovery_interval']
        self.recovery_quantity = state['recovery_quantity']
        self.future_tolerance = state['future_tolerance']

    def __repr__(self, time=None):
        current = self.current(time)
        rv = '<%s %d/%d' % (type(self).__name__, current, self.max)
        if current < self.max:
            recover_in = self.recover_in(time)
            rv += ' recover in %02d:%02d' % (recover_in / 60, recover_in % 60)
        return rv + '>'
