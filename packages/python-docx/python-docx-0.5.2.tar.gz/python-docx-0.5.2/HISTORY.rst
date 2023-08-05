.. :changelog:

Release History
---------------

0.5.2 (2014-05-06)
++++++++++++++++++

- Add #17 feature: character style


0.5.1 (2014-04-02)
++++++++++++++++++

- Fix issue #23, `Document.add_picture()` raises ValueError when document
  contains VML drawing.


0.5.0 (2014-03-02)
++++++++++++++++++

- Add 20 tri-state properties on Run, including all-caps, double-strike,
  hidden, shadow, small-caps, and 15 others.


0.4.0 (2014-03-01)
++++++++++++++++++

- Advance from alpha to beta status.
- Add pure-python image header parsing; drop Pillow dependency


0.3.0a5 (2014-01-10)
++++++++++++++++++++++

- Hotfix: issue #4, Document.add_picture() fails on second and subsequent
  images.


0.3.0a4 (2014-01-07)
++++++++++++++++++++++

- Complete Python 3 support, tested on Python 3.3


0.3.0a3 (2014-01-06)
++++++++++++++++++++++

- Fix setup.py error on some Windows installs


0.3.0a1 (2014-01-05)
++++++++++++++++++++++

- Full object-oriented rewrite
- Feature-parity with prior version
- text: add paragraph, run, text, bold, italic
- table: add table, add row, add column
- styles: specify style for paragraph, table
- picture: add inline picture, auto-scaling
- breaks: add page break
- tests: full pytest and behave-based 2-layer test suite


0.3.0dev1 (2013-12-14)
++++++++++++++++++++++

- Round-trip .docx file, preserving all parts and relationships
- Load default "template" .docx on open with no filename
- Open from stream and save to stream (file-like object)
- Add paragraph at and of document
