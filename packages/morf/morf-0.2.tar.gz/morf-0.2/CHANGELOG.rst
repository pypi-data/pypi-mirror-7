0.2
---

- All ``render_*`` methods now return ``markupsafe.Markup`` objects
- An ``exclude`` argument was added to the default ``Form.update_object``
  implementation, allowing subclasses to more easily override the updating of
  specific attributes, and allowing ``Form.update_object`` to manage the
  remainder.

0.1
---

- Initial release
