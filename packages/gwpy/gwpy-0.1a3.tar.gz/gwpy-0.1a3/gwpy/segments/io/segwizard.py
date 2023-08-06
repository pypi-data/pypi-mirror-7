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

"""Read SegmentLists from seg-wizard format ASCII files
"""

from glue.lal import (CacheEntry, Cache, LIGOTimeGPS)
from glue import segmentsUtils

from astropy.io import registry

from ... import version
from .. import (Segment, SegmentList, DataQualityFlag)
from ...io.cache import file_list

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__version__ = version.version


def from_segwizard(f, coalesce=True, gpstype=LIGOTimeGPS, strict=True,
                   nproc=1):
    """Read segments from a segwizard format file into a `SegmentList`
    """
    if nproc != 1:
        return SegmentList.read(f, coalesce=coalesce, gpstype=gpstype,
                                strict=strict, nproc=nproc, format='cache')

    # format list of files and read in serial
    files = file_list(f)
    segs = SegmentList()
    for fp in files:
        with open(fp, 'r') as fobj:
            segs += SegmentList(map(Segment, segmentsUtils.fromsegwizard(
                        fobj, coltype=gpstype, strict=strict)))
    if coalesce:
        segs.coalesce()
    return segs


def flag_from_segwizard(filename, flag=None, coalesce=True, gpstype=float,
                        strict=True, nproc=1):
    if isinstance(flag, DataQualityFlag):
        out = flag
    else:
        out = DataQualityFlag(str(flag))
    if isinstance(filename, CacheEntry):
        out.valid = [filename.segment]
    elif isinstance(filename, Cache):
        try:
            out.valid = filename.to_segmentlistdict()[out.ifo]
        except KeyError:
            pass
    out.active = from_segwizard(filename, coalesce=coalesce, gpstype=gpstype,
                                strict=strict, nproc=nproc)
    return out


def identify_segwizard(*args, **kwargs):
    filename = args[3]
    if isinstance(filename, file):
        filename = filename.name
    elif isinstance(filename, CacheEntry):
        filename = filename.path
    if (isinstance(filename, (unicode, str)) and
            filename.endswith(('txt', 'dat'))):
        return True
    else:
        return False


def to_segwizard(segs, fobj):
    """Write the given `SegmentList` to the file object fobj

    Parameters
    ----------
    segs : :class:`~gwpy.segments.segments.SegmentList`
        segmentlist to print
    fobj : `file`, `str`
        open file object, or file path, to write to

    See Also
    --------
    :mod:`glue.segmentsUtils`
        for definition of the segwizard format, and the to/from functions
        used in this GWpy module
    """
    if isinstance(fobj, (unicode, str)):
        close = True
        fobj = open(fobj, 'w')
    else:
        close = False
    segmentsUtils.tosegwizard(fobj, segs)
    if close:
        fobj.close()


def flag_to_segwizard(flag, fobj):
    """Write the given `DataQualityFlag` to the file object fobj

    Parameters
    ----------
    flag : :class:`~gwpy.segments.flag.DataQualityFlag`
        data quality flag to print
    fobj : `file`, `str`
        open file object, or file path, to write to

    Notes
    -----
    In this format, only the
    :attr:`~gwpy.segments.flag.DataQualityFlag.active` segments are
    printed

    See Also
    --------
    :mod:`glue.segmentsUtils`
        for definition of the segwizard format, and the to/from functions
        used in this GWpy module
    """
    to_segwizard(flag.active, fobj)


registry.register_reader('segwizard', DataQualityFlag, flag_from_segwizard)
registry.register_writer('segwizard', DataQualityFlag, flag_to_segwizard)
registry.register_identifier('segwizard', DataQualityFlag, identify_segwizard)

registry.register_reader('segwizard', SegmentList, from_segwizard)
registry.register_writer('segwizard', SegmentList, to_segwizard)
registry.register_identifier('segwizard', SegmentList, identify_segwizard)
