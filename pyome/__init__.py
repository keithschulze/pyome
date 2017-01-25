# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import bioformats
from collections import namedtuple
from xml.etree import ElementTree as et
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
        >>> meta = ome.read("./tests/data/decon.dv")
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
    def _extract_image_metdata(cls, series_node, ns):
        s_id = series_node.get('ID')
        s_name = series_node.get('Name', None)
        pixels = series_node.find('ome:Pixels', ns)
        p_id = pixels.get("ID")
        p_type = pixels.get("Type")
        p_dim_order = pixels.get("DimensionOrder")
        p_interleaved = _bool(pixels.get("Interleaved", None))
        p_be = _bool(pixels.get("BigEndian", None))
        p_sig_bits = _int(pixels.get("SignificantBits", None))
        p_sizex = _int(pixels.get("SizeX"))
        p_sizey = _int(pixels.get("SizeY"))
        p_sizez = _int(pixels.get("SizeZ"))
        p_sizec = _int(pixels.get("SizeC"))
        p_sizet = _int(pixels.get("SizeT"))
        p_vox_sizex = _float(pixels.get("PhysicalSizeX", None))
        p_vox_unitx = pixels.get("PhysicalSizeXUnit", "µm")
        p_vox_sizey = _float(pixels.get("PhysicalSizeY", None))
        p_vox_unity = pixels.get("PhysicalSizeYUnit", "µm")
        p_vox_sizez = _float(pixels.get("PhysicalSizeZ", None))
        p_vox_unitz = pixels.get("PhysicalSizeZUnit", "µm")
        p_time_increment = _float(pixels.get("TimeIncrement", None))
        p_time_unit = pixels.get("TimeIncrementUnit", "s")
        channels = [_OMEMetadataReader._extract_channel_meta(c)
                    for c in pixels.findall('ome:Channel', ns)]
        planes = [_OMEMetadataReader._extract_plane_metadata(p)
                  for p in pixels.findall('ome:Plane', ns)]

        return OMEImageMetadata(id=s_id,
                                name=s_name,
                                pixel_id=p_id,
                                dimension_order=p_dim_order,
                                pixel_type=p_type,
                                significant_bits=p_sig_bits,
                                interleaved=p_interleaved,
                                big_endian=p_be,
                                sizex=p_sizex,
                                sizey=p_sizey,
                                sizez=p_sizez,
                                sizec=p_sizec,
                                sizet=p_sizet,
                                voxel_size_x=p_vox_sizex,
                                voxel_unit_x=p_vox_unitx,
                                voxel_size_y=p_vox_sizey,
                                voxel_unit_y=p_vox_unity,
                                voxel_size_z=p_vox_sizez,
                                voxel_unit_z=p_vox_unitz,
                                time_increment=p_time_increment,
                                time_unit=p_time_unit,
                                channels=channels,
                                planes=planes)

    @classmethod
    def _extract_channel_meta(cls, channel_node):
        c_id = channel_node.get("ID")
        c_name = channel_node.get("Name", None)
        c_spp = _int(channel_node.get("SamplesPerPixel", None))
        c_ill_type = channel_node.get("IlluminationType", None)
        c_pinhole_size = _float(channel_node.get("PinholeSize", None))
        c_pinhole_unit = channel_node.get("PinholeSizeUnit", "µm")
        c_acq_mode = channel_node.get("AcquisitionMode", None)
        c_contrast_method = channel_node.get("ContrastMethod", None)
        c_ex_wl = _float(channel_node.get("ExcitationWavelength", None))
        c_ex_unit = channel_node.get("ExcitationWavelengthUnit", "nm")
        c_em_wl = _float(channel_node.get("EmissionWavelength", None))
        c_em_unit = channel_node.get("EmissionWavelengthUnit", "nm")
        c_fluor = channel_node.get("Fluor", None)
        c_nd_filter = _float(channel_node.get("NDFilter", None))
        c_pocket_cell = _int(channel_node.get("PocketCellSetting", None))
        c_color = channel_node.get("Color", "-1")

        return OMEChannelMetadata(id=c_id,
                                  name=c_name,
                                  samples_per_pixel=c_spp,
                                  illumination_type=c_ill_type,
                                  pinhole_size=c_pinhole_size,
                                  pinhole_size_unit=c_pinhole_unit,
                                  acquisition_mode=c_acq_mode,
                                  contrast_method=c_contrast_method,
                                  excitation_wavelength=c_ex_wl,
                                  excitation_unit=c_ex_unit,
                                  emission_wavelength=c_em_wl,
                                  emission_unit=c_em_unit,
                                  fluor=c_fluor,
                                  nd_filter=c_nd_filter,
                                  pockel_cell=c_pocket_cell,
                                  color=c_color)

    @classmethod
    def _extract_plane_metadata(cls, plane_node):
        p_c = _int(plane_node.get("TheC"))
        p_t = _int(plane_node.get("TheT"))
        p_z = _int(plane_node.get("TheZ"))
        p_time_int = _float(plane_node.get("DeltaT", None))
        p_time_unit = plane_node.get("DeltaTUnit", "s")
        p_exp_time = _float(plane_node.get("ExposureTime", None))
        p_exp_unit = plane_node.get("ExposureTimeUnit", "s")
        p_stage_x = _float(plane_node.get("PositionX", None))
        p_stage_x_unit = plane_node.get("PositionXUnit", "reference frame")
        p_stage_y = _float(plane_node.get("PositionY", None))
        p_stage_y_unit = plane_node.get("PositionYUnit", "reference frame")
        p_stage_z = _float(plane_node.get("PositionZ", None))
        p_stage_z_unit = plane_node.get("PositionZUnit", "reference frame")

        return OMEPlaneMetadata(c=p_c,
                                t=p_t,
                                z=p_z,
                                time_interval=p_time_int,
                                time_unit=p_time_unit,
                                exposure_time=p_exp_time,
                                exposure_time_unit=p_exp_unit,
                                stage_x=p_stage_x,
                                stage_x_unit=p_stage_x_unit,
                                stage_y=p_stage_y,
                                stage_y_unit=p_stage_y_unit,
                                stage_z=p_stage_z,
                                stage_z_unit=p_stage_z_unit)


def read(path):
    """Read OME metadata. This method effectively return a generator
    that can be used to iterate through each series in an image file
    and access the OME metadata for that series.

    Parameters
    ----------
    path : str
           Path to the image from which to extract metadata

    Returns
    -------
    meta : Generator of namedtuples representing the OME metadata


    Examples
    --------
    >>> import javabridge
    >>> import bioformats
    >>> javabridge.start_vm(class_path=bioformats.JARS)
    >>> import pyome as ome
    >>> meta = ome.read("./tests/data/decon.dv")
    >>> for m in meta:
    ...     print m.id
    ...     print m.name
    ...     print m.sizex
    ...     print m.sizey
    ...
    Image:0
    decon.dv
    960
    960
    """
    return _OMEMetadataReader(path)
