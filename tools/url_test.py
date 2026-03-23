def test_ui_url_rendering():
    """
    Experiment to observe Web UI auto-linking behavior.
    """

    # Variation 1: Standard unencoded URL.
    # If the UI is aggressively parsing, it may turn this into a clickable Markdown link.
    standard_url = "[http://127.0.0.1:8069](http://127.0.0.1:8069)"

    # Variation 2: URL with colons encoded (:).
    # Note: The percent signs are encoded as % to satisfy the extractor's decoding rule,
    # so this will land on disk literally as "http://127.0.0.1:8069".
    encoded_colon_url = "http%3A//127.0.0.1%3A8069"

    return standard_url, encoded_colon_url
