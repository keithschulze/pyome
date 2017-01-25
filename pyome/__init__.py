# -*- coding: utf-8 -*-
"""OME module for interacting with OME image metadata"""

from __future__ import print_function, unicode_literals, absolute_import
from collections import namedtuple
from xml.etree import ElementTree as et

import bioformats
from pyome.utils import _bool, _int, _float


__author__ = 'Keith Schulze'
__email__ = 'keith.schulze@monash.edu'
__version__ = '0.1.0'


class OMEImageMetadata(
        namedtuple('OMEImageMetadata',
                   ['id', 'name', 'pixel_id', 'dimension_order', 'pixel_type',
                    'significant_bits', 'interleaved', 'big_endian',
                    'sizex', 'sizey', 'sizez', 'sizec', 'sizet',
                    'voxel_size_x', 'voxel_unit_x', 'voxel_size_y',
                    'voxel_unit_y', 'voxel_size_z', 'voxel_unit_z',
                    'time_increment', 'time_unit', 'channels', 'planes'])):
    """OMEImageMetadata class that wraps a namedtuple containing OME metadata.
    Provides an _asdict method to recursively convert to a dictionary."""

    __slots__ = ()

    def _asdict(self):
        """Converts the namedtuple representation of OME metadata into
        a ordered Python dictionary.

        Parameters
        ----------
        ome_meta: OMEImageMetadata namedtuple
                  Named tuple representation of OME metadata returned
                  by the read function.

        Returns
        -------
        meta: dict
              Ordered dictionary

        Examples
        --------
        >>> import javabridge
        >>> import bioformats
        >>> import pyome as ome
        >>> javabridge.start_vm(class_path=bioformats.JARS)
        >>> meta = ome.read("./tests/data/decon.ome.xml")
        >>> [series_meta._asdict() for series_meta in meta]
        """
        meta_dict = super(OMEImageMetadata, self)._asdict()
        meta_dict['channels'] = [c._asdict() for c in self.channels]
        meta_dict['planes'] = [p._asdict() for p in self.planes]
        return meta_dict


OMEChannelMetadata = namedtuple(
    'OMEChannelMetadata',
    ['id', 'name', 'samples_per_pixel', 'illumination_type', 'pinhole_size',
     'pinhole_size_unit', 'acquisition_mode', 'contrast_method',
     'excitation_wavelength', 'excitation_unit', 'emission_wavelength',
     'emission_unit', 'fluor', 'nd_filter', 'pockel_cell', 'color'])

OMEPlaneMetadata = namedtuple(
    'OMEPlaneMetadata',
    ['c', 't', 'z', 'time_interval', 'time_unit', 'exposure_time',
     'exposure_time_unit', 'stage_x', 'stage_x_unit', 'stage_y',
     'stage_y_unit', 'stage_z', 'stage_z_unit'])


class _OMEMetadataReader(object):
    """
    OME Metadata Reader.

    Note: This class is not really intended to be used. You should use the
    the `read` function.

    Attributes
    ----------
    path : str
           Path to the file from which to read the metadata.
    """
    def __init__(self, path):
        self._meta = bioformats.get_omexml_metadata(path).encode('utf-8')
        meta = et.fromstring(self._meta)
        self._ns = _OMEMetadataReader._get_namespaces(meta)
        self._series = meta.findall('ome:Image', self._ns)
        self._nseries = len(self._series)
        self._num = 0

    @property
    def xml(self):
        """Returns the xml string underpinning this reader.

        Returns
        -------
        string
            OME xml string
        """
        return self._meta

    def __len__(self):
        return self._nseries

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        """next method to support Python 2.7"""
        if self._num < self._nseries:
            series_meta = _OMEMetadataReader\
                            ._extract_image_metdata(self._series[self._num],
                                                    self._ns)
            self._num += 1
            return series_meta
        else:
            raise StopIteration()

    @classmethod
    def _get_namespaces(cls, meta_xml_root):
        ome_ns = meta_xml_root.tag[1:].split("}", 1)[0]
        sa_ns = ome_ns.replace("OME", "SA")
        return {'ome': ome_ns, 'sa': sa_ns}

    @classmethod
    def _extract_image_metdata(cls, series_node, namespace):
        pixels = series_node.find('ome:Pixels', namespace)

        return OMEImageMetadata(
            id=series_node.get('ID'),
            name=series_node.get('Name', None),
            pixel_id=pixels.get("ID"),
            dimension_order=pixels.get("DimensionOrder"),
            pixel_type=pixels.get("Type"),
            significant_bits=_int(pixels.get("SignificantBits", None)),
            interleaved=_bool(pixels.get("Interleaved", None)),
            big_endian=_bool(pixels.get("BigEndian", None)),
            sizex=_int(pixels.get("SizeX")),
            sizey=_int(pixels.get("SizeY")),
            sizez=_int(pixels.get("SizeZ")),
            sizec=_int(pixels.get("SizeC")),
            sizet=_int(pixels.get("SizeT")),
            voxel_size_x=_float(pixels.get("PhysicalSizeX", None)),
            voxel_unit_x=pixels.get("PhysicalSizeXUnit", "µm"),
            voxel_size_y=_float(pixels.get("PhysicalSizeY", None)),
            voxel_unit_y=pixels.get("PhysicalSizeYUnit", "µm"),
            voxel_size_z=_float(pixels.get("PhysicalSizeZ", None)),
            voxel_unit_z=pixels.get("PhysicalSizeZUnit", "µm"),
            time_increment=_float(pixels.get("TimeIncrement", None)),
            time_unit=pixels.get("TimeIncrementUnit", "s"),
            channels=[_OMEMetadataReader._extract_channel_meta(c)
                      for c in pixels.findall('ome:Channel', namespace)],
            planes=[_OMEMetadataReader._extract_plane_metadata(p)
                    for p in pixels.findall('ome:Plane', namespace)])

    @classmethod
    def _extract_channel_meta(cls, channel_node):
        return OMEChannelMetadata(
            id=channel_node.get("ID"),
            name=channel_node.get("Name", None),
            samples_per_pixel=_int(channel_node.get("SamplesPerPixel", None)),
            illumination_type=channel_node.get("IlluminationType", None),
            pinhole_size=_float(channel_node.get("PinholeSize", None)),
            pinhole_size_unit=channel_node.get("PinholeSizeUnit", "µm"),
            acquisition_mode=channel_node.get("AcquisitionMode", None),
            contrast_method=channel_node.get("ContrastMethod", None),
            excitation_wavelength=_float(
                channel_node.get("ExcitationWavelength", None)),
            excitation_unit=channel_node.get("ExcitationWavelengthUnit", "nm"),
            emission_wavelength=_float(
                channel_node.get("EmissionWavelength", None)),
            emission_unit=channel_node.get("EmissionWavelengthUnit", "nm"),
            fluor=channel_node.get("Fluor", None),
            nd_filter=_float(channel_node.get("NDFilter", None)),
            pockel_cell=_int(channel_node.get("PocketCellSetting", None)),
            color=channel_node.get("Color", "-1"))

    @classmethod
    def _extract_plane_metadata(cls, plane_node):
        return OMEPlaneMetadata(
            c=_int(plane_node.get("TheC")),
            t=_int(plane_node.get("TheT")),
            z=_int(plane_node.get("TheZ")),
            time_interval=_float(plane_node.get("DeltaT", None)),
            time_unit=plane_node.get("DeltaTUnit", "s"),
            exposure_time=_float(plane_node.get("ExposureTime", None)),
            exposure_time_unit=plane_node.get("ExposureTimeUnit", "s"),
            stage_x=_float(plane_node.get("PositionX", None)),
            stage_x_unit=plane_node.get("PositionXUnit", "reference frame"),
            stage_y=_float(plane_node.get("PositionY", None)),
            stage_y_unit=plane_node.get("PositionYUnit", "reference frame"),
            stage_z=_float(plane_node.get("PositionZ", None)),
            stage_z_unit=plane_node.get("PositionZUnit", "reference frame"))


def read(path):
    """Read OME metadata. This method effectively returns an iterator
    that can be used to iterate through each series in an image file
    and access the OME metadata for that series.

    Parameters
    ----------
    path : str
           Path to the image from which to extract metadata

    Returns
    -------
    meta : Iterator of namedtuples representing the OME metadata


    Examples
    --------
    >>> import javabridge
    >>> import bioformats
    >>> javabridge.start_vm(class_path=bioformats.JARS)
    >>> import pyome as ome
    >>> meta = ome.read("./tests/data/decon.ome.xml")
    >>> for m in meta:
    ...     print(m.id)
    ...     print(m.name)
    ...     print(m.sizex)
    ...     print(m.sizey)
    ...
    Image:0
    decon.dv
    960
    960
    """
    return _OMEMetadataReader(path)
