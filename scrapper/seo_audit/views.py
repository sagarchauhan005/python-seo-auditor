import json
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .services.seo_analyzer import SEOAnalyzer
import logging
from .utils.helper import validate_url, is_safe_url


# Create your views here.

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))


def audit(request):
    try:
        # Parse request data
        data = json.loads(request.body)
        url = data.get('url', '').strip()

        if not url:
            return JsonResponse({
                'status': 'error',
                'message': 'URL is required'
            }, status=400)

        # Validate URL
        if not validate_url(url):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid URL format'
            }, status=400)

        # Security check
        if not is_safe_url(url):
            return JsonResponse({
                'status': 'error',
                'message': 'URL not allowed'
            }, status=400)

        # Perform SEO analysis
        analyzer = SEOAnalyzer()
        analysis_result = analyzer.analyze(url)

        return JsonResponse({
            'status': 'success',
            'data': analysis_result
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logging.error(f"SEO analysis error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Analysis failed. Please try again.'+e.__str__()
        }, status=500)