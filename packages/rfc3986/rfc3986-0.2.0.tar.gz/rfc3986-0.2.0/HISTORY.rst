0.2.0 -- 2014-06-30
-------------------

- Add support for requiring components during validation. This includes adding
  parameters ``require_scheme``, ``require_authority``, ``require_path``,
  ``require_path``, ``require_query``, and ``require_fragment`` to
  ``rfc3986.is_valid_uri`` and ``URIReference#is_valid``.

0.1.0 -- 2014-06-27
-------------------

- Initial Release includes validation and normalization of URIs
