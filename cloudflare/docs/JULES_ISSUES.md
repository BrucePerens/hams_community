# JULES_ISSUES - cloudflare module

## AI Hallucination & Laziness Repairs
- [DONE] **Request Binding Checks**: Several instances where `hasattr(request, ...)` is used on potentially unbound Werkzeug `LocalProxy`. Fixed by using `type(request).__name__ == 'LocalProxy'` to check for proxy before calling `_get_current_object()`, and `getattr(obj, 'attr', False)` on the real object.
- [DONE] **Empty Exception Handlers**: `except RuntimeError: pass` in `models/edge_context.py`. Fixed by adding `_logger.debug()` calls.

## Proposed Linter Rules
- **Rule**: Forbid `hasattr(request, ...)` if `request` is a `LocalProxy` from `werkzeug.local` or `odoo.http`.
- **Reasoning**: Accessing attributes on an unbound proxy raises `RuntimeError`, defeating the purpose of the check.
- **Better Pattern**:
```python
try:
    req_obj = request._get_current_object()
    if hasattr(req_obj, 'attr'):
        ...
except RuntimeError:
    # Not bound
    ...
```
