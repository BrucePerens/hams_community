import re

with open("cloudflare/utils/cloudflare_api.py", "r") as f:
    content = f.read()

# Replace purge_urls
purge_urls_replacement = """def purge_urls(urls, token, zone_id):
    if not token or not zone_id:
        return False
    if not urls:
        return True

    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Batch requests into chunks of 30 items
    success = True
    for i in range(0, len(urls), 30):
        chunk = urls[i:i+30]
        payload = {"files": chunk}
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            _logger.error(f"Cloudflare URL purge API failed for chunk: {e}")
            success = False
    return success"""

content = re.sub(
    r"def purge_urls\(urls, token, zone_id\):.*?return False",
    purge_urls_replacement,
    content,
    flags=re.DOTALL,
)

# Replace purge_tags
purge_tags_replacement = """def purge_tags(tags, token, zone_id):
    if not token or not zone_id:
        return False
    if not tags:
        return True

    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Batch requests into chunks of 30 items
    success = True
    for i in range(0, len(tags), 30):
        chunk = tags[i:i+30]
        payload = {"tags": chunk}
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            _logger.error(f"Cloudflare Tag purge API failed for chunk: {e}")
            success = False
    return success"""

content = re.sub(
    r"def purge_tags\(tags, token, zone_id\):.*?return False",
    purge_tags_replacement,
    content,
    flags=re.DOTALL,
)

with open("cloudflare/utils/cloudflare_api.py", "w") as f:
    f.write(content)
