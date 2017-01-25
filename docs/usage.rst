=====
Usage
=====

pyome leverages `javabridge` and `python-bioformats`, and it largely provides
the same set of tools for reading OME metadata from bio-image file formats. The
way in which it differs from `python-bioformats` is simply is the way one
interacts with the metadata. The whole idea was to provide a way to lazily
iterate through metadata for each series in a multi-series image file. Thus
when you call `read` on an image file, pyome returns an iterator that returns the
metadata for a single series on each iteration.

To use pyome in a project::

  import javabridge
  import bioformats
  import pyome as ome

  javabridge.start_vm(class_path=bioformats.JARS)

  meta = ome.read("decon.ome.xml")

  for m in meta:
    print(m.id)
    print(m.name)
    print(m.sizex)
    print(m.sizey)
    print(m.voxel_size_x)
    print(m.voxel_size_y)


A couple of important points:

- Each series is lazily read so everything is not loaded to memory.
- Note that because read return an iterator, you *can't* index a series by
  calling it number like a list (e.g., meta[0]). If you really want to do this
  there is an `_asdict()` method on the iterator object that will return a
  dictionary that you can index into. Note, however, that getting elements out
  of the dictionary require that you index with a key rather than the more
  friendly dot notation of the `namedtuple` that is returned in each iteration
  of the iterator.
- `itertools` and `functools` will generally help you.
