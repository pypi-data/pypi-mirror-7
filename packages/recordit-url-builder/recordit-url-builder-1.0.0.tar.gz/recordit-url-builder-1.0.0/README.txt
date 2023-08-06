===============================
Recordit URL Builder for Python
===============================

A simple tool to generate recordit URLs

Usage
=====
::

    from recordit.url import URLBuilder
    # or import recordit.url and use recordit.url.URLBuilder

    url_builder = URLBuilder(
      "f33dd06d1cd1fb6e94504c767e5ccd9d0f7cd039",     # your client ID
      "6d85ffe45dbc37f6e47bc443f6079dc26f61b3df"      # your secret
    )

    url_builder.generate({
        "fps": 12,
        "encode": "none",
        "action_url": "http://example.com/123",
        "callback": "http://example.com/api/123",
        "start_message": "This is the initial message",
        "end_message": "This is the end message",
        "width": 1280,
        "height": 720
    })

    # => recordit:f33dd06d1cd1fb6e94504c767e5ccd9d0f7cd039-565fcfbfe0c2e0c59be5
    9df7b3b73d42f564e6cc?fps=12&encode=none&action_url=http%3A%2F%2Fexample.com%
    2F123&callback=http%3A%2F%2Fexample.com%2Fapi%2F123&start_message=This%20is%
    20the%20initial%20message&end_message=This%20is%20the%20end%20message&width=
    1280&height=720
