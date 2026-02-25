# User Websites (`user_websites`) - API Reference

## Purpose
Provides multi-tenant proxy ownership, personalized user websites, group websites, integrated blogging, and robust GDPR compliance utilities (Data Portability and Right to Erasure).

## Python API

### `user_websites.owned.mixin`
An `AbstractModel` mixin that injects the Proxy Ownership Pattern into any model, allowing users to "own" records without possessing global backend access.
* **Usage:** Inherit this mixin in your custom models:
  ```python
  class MyModel(models.Model):
      _name = 'my.model'
      _inherit = ['user_websites.owned.mixin']
  ```
* **Methods Provided:**
  * `_check_proxy_ownership_create(vals_list)`: Validates ownership assignment during record creation.
  * `_check_proxy_ownership_write(vals)`: Prevents malicious ownership transfer.

### `res.users` (Extensions)
The user model is heavily extended to support routing and GDPR functions.

#### `_get_user_id_by_slug(slug)`
High-performance, RAM-cached lookup to resolve a website slug to a User ID.
* **Returns:** `int` (User ID) or `False`.
* **Usage:** Use this instead of `.search()` in frontend controllers.

#### `_get_gdpr_export_data()` (Extendable Hook)
Returns a dictionary of all personal data owned by the user. Dependent modules storing PII MUST override this to append their data.
* **Returns:** `dict`

#### `_execute_gdpr_erasure()` (Extendable Hook)
Permanently unlinks all user-owned content. Dependent modules MUST override this to execute `.sudo().unlink()` on their custom records.

#### `action_suspend_user_websites()` & `action_pardon_user_websites()`
Forcefully unpublishes (or pardons) user content based on the 3-strike moderation system.
