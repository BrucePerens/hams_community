# Story: Parameter Whitelisting `[@ANCHOR: story_parameter_whitelisting]`

This story describes how sensitive system parameters are protected from unauthorized access or exfiltration.

## Background
System parameters (`ir.config_parameter`) often contain configuration that, if leaked, could compromise the system. Server-Side Template Injection (SSTI) is a common vector for exfiltrating these parameters.

## The Process
1. **Access Request**: A module needs to retrieve a system parameter using `_get_system_param` `[@ANCHOR: get_system_param]`.
2. **Whitelist Check**: The function checks if the requested key is in the hardcoded `PARAM_WHITELIST`.
3. **Banned Substring Check**: Even for non-whitelisted keys (if the policy allows), it checks for substrings like `secret`, `key`, `password`, etc.
4. **Restricted Retrieval**: If the key passes all checks, it is retrieved using `.sudo()` (safely wrapped) and returned.

## Developer Requirement
If a new, safe parameter needs to be accessible via this utility, the developer MUST add it to the `PARAM_WHITELIST` in the source code of `zero_sudo`.
