# -*- coding: utf-8 -*-
# Copyright (C) Duncan Macleod (2013)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.

"""Boolean array representing the state of some data

Such states are typically the comparison of a `TimeSeries` against some
threshold, where sub-threshold is good and sup-threshold is bad,
for example.

Single `StateTimeSeries` can be bundled together to form `StateVector`
arrays, representing a bit mask of states that combine to make a detailed
statement of instrumental operation
"""

from math import (ceil, log)
import sys

if sys.version_info[0] < 3:
    range = xrange

import numpy

from glue.segmentsUtils import from_bitstream
from astropy.units import Quantity

from .core import (TimeSeries, TimeSeriesDict, ArrayTimeSeries,
                   NDS2_FETCH_TYPE_MASK)
from ..detector import Channel
from ..time import Time
from ..segments import *
from ..utils import update_docstrings
from ..io import reader
from .. import version
__version__ = version.version
__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

__all__ = ['StateTimeSeries', 'StateVector', 'StateVectorDict', 'BitMask']


@update_docstrings
class StateTimeSeries(TimeSeries):
    """Boolean array representing a good/bad state determination
    of some data.

    Parameters
    ----------
    data : `numpy.ndarray`, `list`
        Data values to initialise TimeSeries
    times : `numpy.ndarray`, optional
        array of time values to accompany data, these are required for
        StateTimeSeries with un-even sampling
    epoch : `float` GPS time, or :class:`~gwpy.time.Time`, optional
        StateTimeSeries start time
    channel : :class:`~gwpy.detector.Channel`, or `str`, optional
        Data channel for this TimeSeries
    unit : :class:`~astropy.units.Unit`, optional
        The units of the data
    sample_rate : `float`, optional
        number of samples per second for this StateTimeSeries
    name : `str`, optional
        descriptive title for this StateTimeSeries

    Returns
    -------
    statebit : `StateTimeSeries`
        A new `StateTimeSeries`
    """
    def __new__(cls, data, times=None, epoch=None, channel=None,
                sample_rate=None, name=None, **kwargs):
        """Generate a new StateTimeSeries
        """
        if isinstance(data, (list, tuple)):
            data = numpy.asarray(data)
        if not isinstance(data, cls):
            data = data.astype(bool)
        return super(StateTimeSeries, cls).__new__(cls, data, name=name,
                                                   epoch=epoch, channel=channel,
                                                   sample_rate=sample_rate,
                                                   times=times)

    def to_dqflag(self, name=None, minlen=1, dtype=float, round=False,
                  label=None, description=None):
        """Convert this `StateTimeSeries` into a `DataQualityFlag`.

        Each contiguous set of `True` values are grouped as a `Segment`
        running from the start of the first found `True`, to the end of
        the last.

        Parameters
        ----------
        minlen : `int`, optional, default: 1
            minimum number of consecutive `True` values to identify as a
            `Segment`. This is useful to ignore single bit flips,
            for example.
        dtype : `type`, `callable`, default: `float`
            output segment entry type, can pass either a type for simple
            casting, or a callable function that accepts a float and returns
            another numeric type
        round : `bool`, optional, default: False
            choose to round each `Segment` to its inclusive integer
            boundaries

        Returns
        -------
        dqflag : :class:`~gwpy.segments.flag.DataQualityFlag`
            a segment representation of this `StateTimeSeries`, the span
            defines the `valid` segments, while the contiguouse `True`
            sets defined each of the `active` segments
        """
        start = self.x0.value
        dt = self.dx.value
        active = from_bitstream(self.data, start, dt, minlen=int(minlen))
        if dtype is not float:
            active = active.__class__([Segment(dtype(s[0]), dtype(s[1])) for
                                       s in active])
        valid = SegmentList([self.span])
        out = DataQualityFlag(name=name or self.name, active=active,
                              valid=valid, label=label or self.name,
                              description=description)
        if round:
            out = out.round()
        return out.coalesce()

    def to_lal(self, *args, **kwargs):
        """Bogus function inherited from superclass, do not use.
        """
        raise NotImplementedError("The to_lal method, inherited from the "
                                  "TimeSeries, cannot be used with the "
                                  "StateTimeSeries because LAL has no "
                                  "BooleanTimeSeries structure")

    def spectrogram(self, *args, **kwargs):
        """Bogus function inherited from parent class, do not use.
        """
        raise NotImplementedError("The spectrogram method, inherited from the "
                                  "TimeSeries, cannot be used with the "
                                  "StateTimeSeries because LAL has no "
                                  "BooleanTimeSeries structure")



class BitMask(list):
    """Definition of the bits in a `StateVector`.

    Parameters
    ----------
    bits : `list`
        list of bit names
    channel : `Channel`, `str`, optional
        data channel associated with this BitMask
    epoch : `float`, optional
        defining GPS epoch for this `BitMask`
    description : `dict`, optional
        (bit, desc) `dict` of longer descriptions for each bit
    """
    def __init__(self, bits, channel=None, epoch=None, description=None):
        list.__init__(self, bits)
        if channel is not None:
            self.channel = channel
        if epoch is not None:
            self.epoch = epoch
        self.description = description
        for i,bit in enumerate(bits):
            if bit is None or bit in self.description:
                continue
            elif channel:
                self.description[bit] = '%s bit %d' % (self.channel, i)
            else:
                self.description[bit] = None

    @property
    def epoch(self):
        """Starting GPS time epoch for this `Array`.

        This attribute is recorded as a `~gwpy.time.Time` object in the
        GPS format, allowing native conversion into other formats.

        See `~astropy.time` for details on the `Time` object.
        """
        try:
            return Time(self._epoch, format='gps')
        except AttributeError:
            return None

    @epoch.setter
    def epoch(self, epoch):
        if isinstance(epoch, Time):
            self._epoch = epoch.gps
        elif isinstance(epoch, Quantity):
            self._epoch = epoch.value
        else:
            self._epoch = float(epoch)

    @property
    def channel(self):
        """Data channel associated with this `TimeSeries`.
        """
        try:
            return self._channel
        except AttributeError:
            return None

    @channel.setter
    def channel(self, ch):
        self._channel = Channel(ch)

    @property
    def description(self):
        """(key, value) dictionary of long bit descriptions.
        """
        return self._description

    @description.setter
    def description(self, desc):
        if desc is None:
            self._description = {}
        else:
            self._description = desc

    def __repr__(self):
        indent = " " * len('<%s(' % self.__class__.__name__)
        mask = ('\n%s' % indent).join(['%d: %s' % (idx, repr(bit)) for
                                       idx,bit in enumerate(self)
                                       if bit])
        return ("<{1}({2},\n{0}channel={3},\n{0}epoch={4})>".format(
                    indent, self.__class__.__name__,
                    mask, repr(self.channel), repr(self.epoch)))

    def __str__(self):
        indent = " " * len('%s(' % self.__class__.__name__)
        mask = ('\n%s' % indent).join(['%d: %s' % (idx, str(bit)) for
                                       idx,bit in enumerate(self)
                                       if bit])
        return ("{1}({2},\n{0}channel={3},\n{0}epoch={4})".format(
                    indent, self.__class__.__name__,
                    mask, str(self.channel), str(self.epoch)))


@update_docstrings
class StateVector(TimeSeries):
    """Binary array representing a set of good/bad state determinations
    of some data.

    Each binary bit represents a single boolean condition, with the
    definitins of all the bits stored in the `StateVector.bitmask`
    attribute.

    Parameters
    ----------
    data : `numpy.ndarray`, `list`
        Binary data values to initialise `StateVector`
    bitmask : `BitMask`, `list`, optional
        list of bits defining this `StateVector`
    times : `numpy.ndarray`, optional
        array of time values to accompany data, these are required for
        `StateVector` with un-even sampling
    name : `str`, optional
        descriptive title for this StateTimeSeries
    epoch : `float` GPS time, or :class:`~astropy.time.core.Time`, optional
        starting GPS epoch for this `StateVector`
    channel : :class:`~gwpy.detector.Channel`, or `str`, optional
        data channel associated with this `StateVector`
    sample_rate : `float`, optional
        data rate for this `StateVector` in samples per second (Hertz).
    """
    _metadata_slots = TimeSeries._metadata_slots + ['bitmask']
    def __new__(cls, data, bitmask=[], times=None, epoch=None, channel=None,
                sample_rate=None, name=None, **kwargs):
        """Generate a new StateTimeSeries
        """
        if not isinstance(data, cls):
            data = numpy.asarray(data).astype(numpy.uint32)
        return super(StateVector, cls).__new__(cls, data, name=name,
                                               epoch=epoch, channel=channel,
                                               sample_rate=sample_rate,
                                               times=times, bitmask=bitmask,
                                               **kwargs)

    # -------------------------------------------
    # StateVector properties

    @property
    def bitmask(self):
        """The list of bit names for this `StateVector`.
        """
        try:
            return self.metadata['bitmask']
        except:
            self.bitmask = BitMask([])
            return self.bitmask

    @bitmask.setter
    def bitmask(self, mask):
        if not isinstance(mask, BitMask):
            mask = BitMask(mask, channel=self.channel,
                           epoch=self.metadata.get('epoch', None))
        self.metadata['bitmask'] = mask

    @property
    def boolean(self):
        """A mapping of this `StateVector` to a 2-D array containing all
        binary bits as booleans, for each time point.
        """
        try:
            return self._boolean
        except AttributeError:
            nbits = len(self.bitmask)
            boolean = numpy.zeros((self.size, nbits), dtype=bool)
            for i,d in enumerate(self.data):
                boolean[i,:] = [int(d)>>j & 1 for
                                j in range(nbits)]
            self._boolean = ArrayTimeSeries(boolean, name=self.name,
                                            epoch=self.epoch,
                                            sample_rate=self.sample_rate,
                                            y0=0, dy=1)
            return self.boolean

    @property
    def bits(self):
        """A list of `StateTimeSeries` for each of the individual
        bits in this `StateVector`.
        """
        try:
            return self._bits
        except AttributeError:
            self._bits = []
            for i,bit in enumerate(self.bitmask):
                if bit is None:
                    self._bits.append(None)
                else:
                    self._bits.append(StateTimeSeries(
                                          self.data >> i & 1, name=bit,
                                          epoch=self.x0.value,
                                          channel=self.channel,
                                          sample_rate=self.sample_rate))
            return self.bits

    # -------------------------------------------
    # StateVector methods

    # use input/output registry to allow multi-format reading
    read = classmethod(reader(doc="""
        Read data into a `StateVector`.

        Parameters
        ----------
        source : `str`, `~glue.lal.Cache`
            a single file path `str`, or a `~glue.lal.Cache` containing
            a contiguous list of files.
        channel : `str`, `~gwpy.detector.core.Channel`
            the name of the channel to read, or a `Channel` object.
        start : `~gwpy.time.Time`, `float`, optional
            GPS start time of required data.
        end : `~gwpy.time.Time`, `float`, optional
            GPS end time of required data.
        format : `str`, optional
            source format identifier. If not given, the format will be
            detected if possible. See below for list of acceptable formats.
        nproc : `int`, optional, default: ``1``
            number of parallel processes to use, serial process by
            default.

            .. note::

               Parallel frame reading, via the ``nproc`` keyword argument,
               is only available when giving a :class:`~glue.lal.Cache` of
               frames, or using the ``format='cache'`` keyword argument.

        Returns
        -------
        statevector : `StateVector`
            a new `StateVector` containing data for the given channel.

        Raises
        ------
        Exception
            if no format could be automatically identified.

        .. warning::

           The 'built-in' formats below may require third-party
           libraries in order to function. If the relevant libraries
           cannot be loaded at run-time, that format will be removed
           from the list.

        Notes
        -----"""))

    def to_dqflags(self, minlen=1, dtype=float, round=False):
        """Convert this `StateVector` into a `SegmentListDict`.

        The `StateTimeSeries` for each bit is converted into a `SegmentList`
        with the bits combined into a dict.

        Parameters
        ----------
        minlen : `int`, optional, default: 1
           minimum number of consecutive `True` values to identify as a
           `Segment`. This is useful to ignore single bit flips,
           for example.

        Returns
        -------
        DataQualityFlag list : `list`
            a list of :class:`~gwpy.segments.flag.DataQualityFlag`
            reprensentations for each bit in this `StateVector`

        See Also
        --------
        :meth:`StateTimeSeries.to_dqflag`
            for details on the segment representation method for
            `StateVector` bits
        """
        return [self.bits[i].to_dqflag(
                    name=bit, minlen=minlen, round=round, dtype=dtype,
                    description=self.bitmask.description[bit])
                for i,bit in enumerate(self.bitmask) if bit is not None]

    @classmethod
    def fetch(cls, channel, start, end, bitmask=[], host=None, port=None,
              verbose=False, connection=None, type=NDS2_FETCH_TYPE_MASK):
        """Fetch data from NDS into a `StateVector`.

        Parameters
        ----------
        channel : :class:`~gwpy.detector.channel.Channel`, or `str`
            required data channel
        start : `~gwpy.time.Time`, or float
            GPS start time of data span
        end : `~gwpy.time.Time`, or float
            GPS end time of data span
        bitmask : `BitMask`, `list`, optional
            definition of bits for this `StateVector`
        host : `str`, optional
            URL of NDS server to use, defaults to observatory site host.
        port : `int`, optional
            port number for NDS server query, must be given with `host`.
        verbose : `bool`, optional
            print verbose output about NDS progress.
        connection : :class:`~gwpy.io.nds.NDS2Connection`
            open NDS connection to use.
        type : `int`, `str`,
            NDS2 channel type integer or string name.

        Returns
        -------
        data : `StateVector`
            a new `StateVector` containing the data read from NDS
        """
        new = StateVectorDict.fetch(
            [channel], start, end, host=host, port=port,
            verbose=verbose, connection=connection)[channel]
        new.bitmask = bitmask
        return new

    def to_lal(self, *args, **kwargs):
        """Bogus function inherited from superclass, do not use.
        """
        raise NotImplementedError("The to_lal method, inherited from the "
                                  "TimeSeries, cannot be used with the "
                                  "StateTimeSeries because LAL has no "
                                  "BooleanTimeSeries structure")

    def plot(self, format='segments', **kwargs):
        """Plot the data for this `StateVector`

        Parameters
        ----------
        format : `str`, optional, default: ``'segments'``
            type of plot to make, either 'segments' to plot the
            SegmentList for each bit, or 'timeseries' to plot the raw
            data for this `StateVector`.
        **kwargs
            other keyword arguments to be passed to either
            :class:`~gwpy.plotter.segments.SegmentPlot` or
            :class:`~gwpy.plotter.timeseries.TimeSeriesPlot`, depending
            on ``format``.

        Returns
        -------
        plot : :class:`~gwpy.plotter.segments.SegmentPlot`, or
               :class:`~gwpy.plotter.timeseries.TimeSeriesPlot`
            output plot object, subclass of :class:`~gwpy.plotter.core.Plot`
        """
        if format == 'timeseries':
            return super(StateVector, self).plot(**kwargs)
        elif format == 'segments':
            kwargs.setdefault('facecolor', 'green')
            kwargs.setdefault('edgecolor', 'black')
            kwargs.setdefault('valid', {'facecolor': 'red',
                                        'edgecolor': 'black'})
            from ..plotter import SegmentPlot
            return SegmentPlot(*self.to_dqflags(), **kwargs)
        raise ValueError("'format' argument must be one of: 'timeseries' or "
                         "'segments'")

    def resample(self, rate):
        """Resample this `StateVector` to a new rate

        Because of the nature of a state-vector, downsampling is done
        by taking the logical 'and' of all original samples in each new
        sampling interval, while upsampling is achieved by repeating
        samples.

        Parameters
        ----------
        rate : `float`
            rate to which to resample this `StateVector`, must be a
            divisor of the original sample rate (when downsampling)
            or a multiple of the original (when upsampling).

        Returns
        -------
        vector : :class:`~gwpy.timeseries.statevector.StateVector`
            resampled version of the input `StateVector`
        """
        rate1 = self.sample_rate.value
        if isinstance(rate, Quantity):
            rate2 = rate.value
        else:
            rate2 = float(rate)
        # upsample
        if (rate2 / rate1).is_integer():
            raise NotImplementedError("StateVector upsampling has not "
                                      "been implemented yet, sorry.")
        # downsample
        elif (rate1 / rate2).is_integer():
            factor = int(rate1 / rate2)
            # reshape incoming data to one column per new sample
            newsize = self.size / factor
            old = self.data.reshape((newsize, self.size // newsize))
            # work out number of bits
            if len(self.bitmask):
                nbits = len(self.bitmask)
            else:
                max = self.data.max()
                nbits = max != 0 and int(ceil(log(self.data.max(), 2))) or 1
            bits = range(nbits)
            # construct an iterator over the columns of the old array
            it = numpy.nditer([old, None],
                              flags=['external_loop', 'reduce_ok'],
                              op_axes=[None, [0, -1]],
                              op_flags=[['readonly'],
                                        ['readwrite', 'allocate']])
            dtype = self.dtype
            type_ = self.dtype.type
            # for each new sample, each bit is logical AND of old samples
            # bit is ON,
            for x, y in it:
                y[...] = numpy.sum([type_((x >> bit & 1).all() * (2 ** bit)) for
                                   bit in bits], dtype=self.dtype)
            new = StateVector(it.operands[1])
            new.metadata = self.metadata.copy()
            new.sample_rate = rate2
            return new
        # error for non-integer resampling factors
        elif rate1 < rate2:
            raise ValueError("New sample rate must be multiple of input "
                             "series rate if upsampling a StateVector")
        else:
            raise ValueError("New sample rate must be divisor of input "
                             "series rate if downsampling a StateVector")

    def spectrogram(self, *args, **kwargs):
        """Bogus function inherited from parent class, do not use.
        """
        raise NotImplementedError("The spectrogram method, inherited from the "
                                  "TimeSeries, cannot be used with the "
                                  "StateTimeSeries because LAL has no "
                                  "BooleanTimeSeries structure")


@update_docstrings
class StateVectorDict(TimeSeriesDict):
    """Analog of the :class:`~gwpy.timeseries.core.TimeSeriesDict`
    for :class:`~gwpy.timeseries.statevector.StateVector` objects.

    See Also
    --------
    :class:`~gwpy.timeseries.core.TimeSeriesDict`
        for more object information.
    """
    EntryClass = StateVector

    read = classmethod(reader(doc="""
        Read data into a `StateVectorDict`.

        Parameters
        ----------
        source : `str`, `~glue.lal.Cache`
            a single file path `str`, or a `~glue.lal.Cache` containing
            a contiguous list of files.
        channels : `~gwpy.detector.channel.ChannelList`, `list`
            a list of channels to read from the source.
        start : `~gwpy.time.Time`, `float`, optional
            GPS start time of required data.
        end : `~gwpy.time.Time`, `float`, optional
            GPS end time of required data.
        format : `str`, optional
            source format identifier. If not given, the format will be
            detected if possible. See below for list of acceptable
            formats.
        nproc : `int`, optional, default: ``1``
            number of parallel processes to use, serial process by
            default.

            .. note::

               Parallel frame reading, via the ``nproc`` keyword argument,
               is only available when giving a :class:`~glue.lal.Cache` of
               frames, or using the ``format='cache'`` keyword argument.

        Returns
        -------
        dict : `StateVectorDict`
            a new `StateVectorDict` containing data for the given channel.

        Raises
        ------
        Exception
            if no format could be automatically identified.

        Notes
        -----"""))
