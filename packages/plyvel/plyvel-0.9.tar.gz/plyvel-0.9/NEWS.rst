===============
Version history
===============

Plyvel 0.9
==========

Release date: 2014-08-27

* Ensure that the Python GIL is initialized when a custom comparator is used,
  since the background thread LevelDB uses for compaction calls back into Python
  code in that case. This makes single-threaded programs using a custom
  comparator work as intended. (`issue #35
  <https://github.com/wbolster/plyvel/issues/35>`_)


Plyvel 0.8
==========

Release date: 2013-11-29

* Allow snapshots to be closed explicitly using either
  :py:meth:`Snapshot.close()` or a ``with`` block (`issue #21
  <https://github.com/wbolster/plyvel/issues/21>`_)


Plyvel 0.7
==========

Release date: 2013-11-15

* New raw iterator API that mimics the LevelDB C++ interface. See
  :py:meth:`DB.raw_iterator()` and :py:class:`RawIterator`. (`issue #17
  <https://github.com/wbolster/plyvel/issues/17>`_)

* Migrate to `pytest` and `tox` for testing (`issue #24
  <https://github.com/wbolster/plyvel/issues/24>`_)

* Performance improvements in iterator and write batch construction. The
  internal calls within Plyvel are now a bit faster, and the `weakref` handling
  required for iterators is now a lot faster due to replacing
  :py:class:`weakref.WeakValueDictionary` with manual `weakref` handling.

* The `fill_cache`, `verify_checksums`, and `sync` arguments to various methods
  are now correctly taken into account everywhere, and their default values are
  now booleans reflecting the the LevelDB defaults.


Plyvel 0.6
==========

Release date: 2013-10-18

* Allow iterators to be closed explicitly using either
  :py:meth:`Iterator.close()` or a ``with`` block (`issue #19
  <https://github.com/wbolster/plyvel/issues/19>`_)

* Add useful ``__repr__()`` for :py:class:`DB` and :py:class:`PrefixedDB`
  instances (`issue #16 <https://github.com/wbolster/plyvel/issues/16>`_)


Plyvel 0.5
==========

Release date: 2013-09-17

* Fix :py:meth:`Iterator.seek()` for :py:class:`PrefixedDB` iterators
  (`issue #15 <https://github.com/wbolster/plyvel/issues/15>`_)

* Make some argument type checking a bit stricter (mostly ``None`` checks)

* Support LRU caches larger than 2GB by using the right integer type for the
  ``lru_cache_size`` :py:class:`DB` constructor argument.

* Documentation improvements


Plyvel 0.4
==========

Release date: 2013-06-17

* Add optional 'default' argument for all ``.get()`` methods
  (`issue #11 <https://github.com/wbolster/plyvel/issues/11>`_)


Plyvel 0.3
==========

Release date: 2013-06-03

* Fix iterator behaviour for reverse iterators using a prefix
  (`issue #9 <https://github.com/wbolster/plyvel/issues/9>`_)

* Documentation improvements


Plyvel 0.2
==========

Release date: 2013-03-15

* Fix iterator behaviour for iterators using non-existing start or stop keys
  (`issue #4 <https://github.com/wbolster/plyvel/issues/4>`_)


Plyvel 0.1
==========

Release date: 2012-11-26

* Initial release
