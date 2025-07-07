import logging
import re
import time
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup


class SEOAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
        self.max_content_size = 10 * 1024 * 1024  # 10MB

    def analyze(self, url):
        """Main analysis method"""
        start_time = time.time()

        try:
            # Fetch page content
            response = self._fetch_page(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract page content
            page_content = self._extract_page_content(soup, response)


            # Perform all SEO checks
            checks = {
                'title_tag': self._check_title_tag(soup),
                'meta_description': self._check_meta_description(soup),
                'h1_tag': self._check_h1_tag(soup),
                'header_hierarchy': self._check_header_hierarchy(soup),
                'content_length': self._check_content_length(soup),
                'keyword_density': self._check_keyword_density(soup),
                'alt_text': self._check_alt_text(soup),
                'canonical_url': self._check_canonical_url(soup, url),
                'meta_robots': self._check_meta_robots(soup),
                'xml_sitemap': self._check_xml_sitemap(soup, url),
                'schema_markup': self._check_schema_markup(soup),
                'broken_links': self._check_broken_links(soup, url)
            }

            # Calculate page info
            page_info = self._calculate_page_info(soup, response, time.time() - start_time)

            return {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'checks': checks,
                'page_info': page_info
            }

        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")

    def _fetch_page(self, url):
        """Fetch page content with proper error handling"""
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True
            )
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                raise Exception("URL does not return HTML content")

            # Check content size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_content_size:
                raise Exception("Page content too large")

            return response

        except requests.exceptions.Timeout:
            raise Exception("Request timeout - page took too long to load")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error - could not reach the website")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP error {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to fetch page: {str(e)}")

    def _extract_page_content(self, soup, response):
        """Extract and clean page content"""
        # Remove script and style elements
        text_soup = BeautifulSoup(str(soup), 'html.parser')
        # Remove script and style elements
        for script in text_soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        return text_soup.get_text()

    def _check_title_tag(self, soup):
        """Check title tag presence and length"""
        title_tag = soup.find('title')

        if not title_tag or not title_tag.string:
            return {
                'status': 'failed',
                'details': 'Title tag missing',
                'issue': 'No title tag found on the page',
                'recommendation': 'Add a descriptive title tag between 50-60 characters'
            }

        title_length = len(title_tag.string.strip())

        if title_length < 30:
            return {
                'status': 'failed',
                'details': f'Title tag too short ({title_length} characters)',
                'issue': 'Title tag is shorter than recommended minimum',
                'recommendation': 'Expand title to 50-60 characters for better SEO'
            }
        elif title_length > 60:
            return {
                'status': 'failed',
                'details': f'Title tag too long ({title_length} characters)',
                'issue': 'Title tag exceeds recommended maximum length',
                'recommendation': 'Shorten title to 50-60 characters to prevent truncation'
            }
        else:
            return {
                'status': 'passed',
                'details': f'Title tag present with {title_length} characters'
            }

    def _check_meta_description(self, soup):
        """Check meta description presence and length"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})

        if not meta_desc or not meta_desc.get('content'):
            return {
                'status': 'failed',
                'details': 'Meta description missing',
                'issue': 'No meta description tag found on the page',
                'recommendation': 'Add a compelling meta description between 150-160 characters'
            }

        desc_length = len(meta_desc.get('content', '').strip())

        if desc_length < 120:
            return {
                'status': 'failed',
                'details': f'Meta description too short ({desc_length} characters)',
                'issue': 'Meta description is shorter than recommended',
                'recommendation': 'Expand meta description to 150-160 characters'
            }
        elif desc_length > 160:
            return {
                'status': 'failed',
                'details': f'Meta description too long ({desc_length} characters)',
                'issue': 'Meta description exceeds recommended length',
                'recommendation': 'Shorten meta description to 150-160 characters'
            }
        else:
            return {
                'status': 'passed',
                'details': f'Meta description present with {desc_length} characters'
            }

    def _check_h1_tag(self, soup):
        """Check H1 tag presence and uniqueness"""
        h1_tags = soup.find_all('h1')

        if not h1_tags:
            return {
                'status': 'failed',
                'details': 'No H1 tag found',
                'issue': 'Page is missing an H1 tag',
                'recommendation': 'Add a single, descriptive H1 tag to the page'
            }

        if len(h1_tags) > 1:
            return {
                'status': 'failed',
                'details': f'Multiple H1 tags found ({len(h1_tags)})',
                'issue': 'Page has multiple H1 tags',
                'recommendation': 'Use only one H1 tag per page'
            }

        h1_text = h1_tags[0].get_text().strip()
        h1_length = len(h1_text)

        if h1_length < 10:
            return {
                'status': 'failed',
                'details': f'H1 tag too short ({h1_length} characters)',
                'issue': 'H1 tag content is too brief',
                'recommendation': 'Make H1 tag more descriptive (20-70 characters)'
            }
        elif h1_length > 70:
            return {
                'status': 'failed',
                'details': f'H1 tag too long ({h1_length} characters)',
                'issue': 'H1 tag content is too lengthy',
                'recommendation': 'Shorten H1 tag to 20-70 characters'
            }
        else:
            return {
                'status': 'passed',
                'details': f'Single H1 tag found with {h1_length} characters'
            }

    def _check_header_hierarchy(self, soup):
        """Check proper header hierarchy (H1-H6)"""
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        if not headers:
            return {
                'status': 'failed',
                'details': 'No header tags found',
                'issue': 'Page has no header structure',
                'recommendation': 'Add proper header hierarchy starting with H1'
            }

        header_levels = [int(h.name[1]) for h in headers]

        # Check if starts with H1
        if header_levels[0] != 1:
            return {
                'status': 'failed',
                'details': 'Header hierarchy does not start with H1',
                'issue': 'First header is not H1',
                'recommendation': 'Start header hierarchy with H1 tag'
            }

        # Check for skipped levels
        for i in range(1, len(header_levels)):
            current_level = header_levels[i]
            prev_level = header_levels[i - 1]

            if current_level > prev_level + 1:
                return {
                    'status': 'failed',
                    'details': f'Header hierarchy skips levels (H{prev_level} to H{current_level})',
                    'issue': 'Header hierarchy skips levels',
                    'recommendation': 'Maintain sequential header hierarchy (H1→H2→H3)'
                }

        return {
            'status': 'passed',
            'details': f'Proper header hierarchy with {len(headers)} headers'
        }

    def _check_content_length(self, soup):
        """Check content length and basic readability"""
        # Extract main content text
        text_content = soup.get_text()
        words = re.findall(r'\b\w+\b', text_content.lower())
        word_count = len(words)

        if word_count < 300:
            return {
                'status': 'failed',
                'details': f'Content too short ({word_count} words)',
                'issue': 'Page has insufficient content for SEO',
                'recommendation': 'Add more quality content (aim for 300+ words)'
            }
        elif word_count > 2000:
            return {
                'status': 'passed',
                'details': f'Comprehensive content with {word_count} words'
            }
        else:
            return {
                'status': 'passed',
                'details': f'Good content length with {word_count} words'
            }

    def _check_keyword_density(self, soup):
        """Analyze keyword density and distribution"""
        text_content = soup.get_text().lower()
        words = re.findall(r'\b\w+\b', text_content)

        if len(words) < 100:
            return {
                'status': 'failed',
                'details': 'Insufficient content for keyword analysis',
                'issue': 'Not enough content to analyze keywords',
                'recommendation': 'Add more content to enable keyword analysis'
            }

        # Count word frequency
        word_counts = Counter(words)

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is',
                      'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                      'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}

        # Filter out stop words and short words
        filtered_words = {word: count for word, count in word_counts.items()
                          if word not in stop_words and len(word) > 3}

        if not filtered_words:
            return {
                'status': 'failed',
                'details': 'No meaningful keywords identified',
                'issue': 'Content lacks focused keywords',
                'recommendation': 'Include relevant keywords naturally in content'
            }

        # Get top keywords
        top_keywords = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:5]
        max_density = (top_keywords[0][1] / len(words)) * 100

        if max_density > 3:
            return {
                'status': 'failed',
                'details': f'Keyword over-optimization detected ({max_density:.1f}%)',
                'issue': 'Keyword density too high - may be considered spam',
                'recommendation': 'Reduce keyword density to 1-2% for natural content'
            }
        elif max_density < 0.5:
            return {
                'status': 'failed',
                'details': f'Low keyword focus ({max_density:.1f}%)',
                'issue': 'Primary keywords appear too infrequently',
                'recommendation': 'Increase target keyword usage to 1-2% density'
            }
        else:
            return {
                'status': 'passed',
                'details': f'Good keyword density ({max_density:.1f}%)'
            }

    def _check_alt_text(self, soup):
        """Check image alt text presence"""
        images = soup.find_all('img')

        if not images:
            return {
                'status': 'passed',
                'details': 'No images found on page'
            }

        missing_alt = []
        empty_alt = []

        for img in images:
            src = img.get('src', 'unknown')
            alt = img.get('alt')

            if alt is None:
                missing_alt.append(src)
            elif not alt.strip():
                empty_alt.append(src)

        total_issues = len(missing_alt) + len(empty_alt)

        if total_issues == 0:
            return {
                'status': 'passed',
                'details': f'All {len(images)} images have alt text'
            }
        else:
            return {
                'status': 'failed',
                'details': f'{total_issues} out of {len(images)} images missing alt text',
                'issue': 'Some images lack descriptive alt attributes',
                'recommendation': 'Add descriptive alt text to all images for accessibility and SEO'
            }

    def _check_canonical_url(self, soup, original_url):
        """Check for canonical URL presence"""
        canonical = soup.find('link', {'rel': 'canonical'})

        if not canonical or not canonical.get('href'):
            return {
                'status': 'failed',
                'details': 'Canonical URL missing',
                'issue': 'No canonical link tag found',
                'recommendation': 'Add canonical URL to prevent duplicate content issues'
            }

        canonical_url = canonical.get('href')

        # Basic validation
        if not canonical_url.startswith(('http://', 'https://')):
            return {
                'status': 'failed',
                'details': 'Invalid canonical URL format',
                'issue': 'Canonical URL is not properly formatted',
                'recommendation': 'Use absolute URLs for canonical tags'
            }

        return {
            'status': 'passed',
            'details': 'Canonical URL properly set'
        }

    def _check_meta_robots(self, soup):
        """Check meta robots tag configuration"""
        robots_meta = soup.find('meta', {'name': 'robots'})

        if not robots_meta:
            return {
                'status': 'passed',
                'details': 'No robots meta tag (defaults to index,follow)'
            }

        content = robots_meta.get('content', '').lower()

        if 'noindex' in content:
            return {
                'status': 'failed',
                'details': 'Page set to noindex',
                'issue': 'Meta robots prevents search engine indexing',
                'recommendation': 'Remove noindex directive if you want page indexed'
            }

        return {
            'status': 'passed',
            'details': f'Meta robots configured: {content}'
        }

    def _check_xml_sitemap(self, soup, url):
        """Check for XML sitemap references"""
        # Check robots.txt for sitemap
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_url = f"{base_url}/robots.txt"

            robots_response = self.session.get(robots_url, timeout=10)
            if robots_response.status_code == 200:
                if 'sitemap:' in robots_response.text.lower():
                    return {
                        'status': 'passed',
                        'details': 'XML sitemap referenced in robots.txt'
                    }

            # Check for sitemap link in HTML
            sitemap_link = soup.find('link', {'type': 'application/xml'}) or \
                           soup.find('a', href=re.compile(r'sitemap.*\.xml', re.I))

            if sitemap_link:
                return {
                    'status': 'passed',
                    'details': 'XML sitemap link found in HTML'
                }

            return {
                'status': 'failed',
                'details': 'XML sitemap reference not found',
                'issue': 'No XML sitemap linked in robots.txt or HTML',
                'recommendation': 'Create and submit an XML sitemap to search engines'
            }

        except:
            return {
                'status': 'failed',
                'details': 'Could not check for XML sitemap',
                'issue': 'Unable to verify sitemap presence',
                'recommendation': 'Ensure XML sitemap is accessible and referenced'
            }

    def _check_schema_markup(self, soup):
        """Check for structured data markup"""
        # Check for JSON-LD
        json_ld = soup.find_all('script', {'type': 'application/ld+json'})

        schema_types = []

        if json_ld:
            schema_types.append(f'JSON-LD ({len(json_ld)} blocks)')

        if schema_types:
            return {
                'status': 'passed',
                'details': f'Schema markup found: {", ".join(schema_types)}'
            }
        else:
            return {
                'status': 'failed',
                'details': 'No structured data detected',
                'issue': 'No JSON-LD, microdata, or RDFa schema markup found',
                'recommendation': 'Implement relevant schema markup (Organization, Article, etc.)'
            }

    def _check_broken_links(self, soup, base_url):
        """Check for broken internal links (basic check)"""
        links = soup.find_all('a', href=True)

        if not links:
            return {
                'status': 'passed',
                'details': 'No links found to check'
            }

        internal_links = []
        broken_links = []

        parsed_base = urlparse(base_url)

        for link in links[:20]:  # Limit to first 20 links for performance
            href = link.get('href')

            # Skip non-HTTP links
            if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                continue

            # Convert relative to absolute
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)

            # Only check internal links
            if parsed_url.netloc == parsed_base.netloc:
                internal_links.append(full_url)

                try:
                    response = self.session.head(full_url, timeout=5, allow_redirects=True)
                    if response.status_code >= 400:
                        broken_links.append(full_url)
                except:
                    broken_links.append(full_url)

        if broken_links:
            return {
                'status': 'failed',
                'details': f'{len(broken_links)} broken internal links found',
                'issue': 'Some internal links return errors',
                'recommendation': 'Fix or remove broken internal links'
            }
        else:
            return {
                'status': 'passed',
                'details': f'No broken links detected (checked {len(internal_links)} internal links)'
            }

    def _calculate_page_info(self, soup, response, load_time):
        """Calculate page statistics"""
        title_tag = soup.find('title')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        images = soup.find_all('img')
        links = soup.find_all('a', href=True)
        h1_tags = soup.find_all('h1')

        # Count internal vs external links
        base_domain = urlparse(response.url).netloc
        internal_links = 0
        external_links = 0

        for link in links:
            href = link.get('href', '')
            if href.startswith('http'):
                if urlparse(href).netloc == base_domain:
                    internal_links += 1
                else:
                    external_links += 1
            elif href.startswith('/') or not href.startswith(('mailto:', 'tel:', '#')):
                internal_links += 1

        # Count words
        text_content = soup.get_text()
        words = re.findall(r'\b\w+\b', text_content)

        return {
            'title_length': len(title_tag.string.strip()) if title_tag and title_tag.string else 0,
            'meta_description_length': len(meta_desc.get('content', '').strip()) if meta_desc else 0,
            'word_count': len(words),
            'images_count': len(images),
            'internal_links': internal_links,
            'external_links': external_links,
            'h1_count': len(h1_tags),
            'load_time': round(load_time, 2)
        }
