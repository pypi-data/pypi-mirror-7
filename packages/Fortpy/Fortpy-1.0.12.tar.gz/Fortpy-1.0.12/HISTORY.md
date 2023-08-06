FORTPY: Revision History
======

Revision 1.0.12
------

- Debugged error where the first parameter to an embedded procedure on a derived type was still being explicitly passed in to the embedded procedure. Since the compiler does that automatically, it was choking.

Revision 1.0.11
------

- Debugged the first real unit test case of an embedded method unit test.
- Debugged some additional allocation problems with auto-generated parameters in the unit testing.

Revision 1.0.10
------

- Fixed a bug that was preventing deferred shape arrays from being allocated automatically by fortpy in unit testing.

Revision 1.0.9
------

- Fixed a bug when comparing two simple representations where the second file has more entries than the first one.
- Fixed a misrepresentation of match success in the testing. The framework was using `common_match` in the `percent_match` routine which made wrong results seem a lot better.
- Added coloring to the terminal output for all packages.

Revision 1.0.8
------

- Fixed bug in `fortpy.pysave` that made 2d saving not produce tabular input.
- Fixed bug that crashed the program when `<isense>` was not present in the `config.xml` file.
- Added support for automated profiling of methods being tested using the -profile argument to `scripts/runtests.py`.

Revision 1.0.7
------

- Added `timed="true"` attribute support to the `<test>` tag.
- Fixed bug where an empty folder being cleaned would raise an exception on `remove()`
- Added a check for executables being tested to make sure they have a `public` modifier or are in the list of public symbols in the parent module.
- Added debug compile option to unit testing.
- Fixed automatic allocation errors for pointers.
- Fixed fortpy.f90 line and value counting routines.
- Added support for arrays of derived types; still get suggestions for embedded members if operating on an element of an array of derived types.
- Fixed a bug in `parsers.types` where "endtype" was not recognized.
- Added `<isense>` section to `config.xml` with an option to uppercase the builtin Fortran names
  by default with the suggestions.

Revision 1.0.6
------

- Fixed issue with fortpy/templates directory not being installed.

Revision 1.0.5
------

- Fixed issue with the builtin.xml file not being included in the distribution.

Revision 1.0.4
------

- Added support for gfortran compilation in unit testing
- Altered testing XML template to use `<test>` instead of `<outcome>`
  - Allow multiple inputs using `<input>` tags instead of comma-separated list.
  - Allow multiple output comparisons with `<output>` tags instead of comma-separated list.
  - Added _description_ attribute to `<test>` tag.
- Constant-input mode for testing. When a `<line>` template is specified for an `<input>` tag, the call to the main method being unit tested can be repeated for each line in that input file.
- Altered testing XML template to use `<assignment>` instead of `<instance>`.
- Variable value assignments directly from files.
  - `<assignment>` tag now accepts additional attributes _folder_, _file_ and _rename_.
- Major overhaul of underlying classes for the unit testing to make future feature enhancements much easier. Added the `elements` module in the `isense` package.
- Added support for built-in functions using information documented from a textbook that is now in `builtin.xml`. Added the `builtin` module to parse and cache that XML documentation.