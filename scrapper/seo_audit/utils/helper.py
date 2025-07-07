import re
from urllib.parse import urlparse


def validate_url(url):
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None


def is_safe_url(url):
    """Check if URL is safe to analyze"""
    parsed = urlparse(url)

    # Block internal IPs and localhost in production
    if parsed.hostname in ['localhost', '127.0.0.1']:
        return False

    # Block private IP ranges
    if parsed.hostname:
        ip_parts = parsed.hostname.split('.')
        if len(ip_parts) == 4:
            try:
                first_octet = int(ip_parts[0])
                second_octet = int(ip_parts[1])

                # Private IP ranges
                if (first_octet == 10 or
                        (first_octet == 172 and 16 <= second_octet <= 31) or
                        (first_octet == 192 and second_octet == 168)):
                    return False
            except ValueError:
                pass

    return True