from . import models  # noqa: F401


def post_init_hook(env):
    import os

    html_path = os.path.join(os.path.dirname(__file__), "data", "documentation.html")
    if not os.path.exists(html_path):
        return
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "manual.article" in env:
        env["manual.article"].sudo().create(
            {"name": "Binary Downloader", "body": content}
        )
    elif "knowledge.article" in env:
        env["knowledge.article"].sudo().create(
            {"name": "Binary Downloader", "body": content}
        )
