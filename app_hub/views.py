import json
import requests
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.utils import timezone
from user_agents import parse as parse_ua

from .models import Contact, Project, Visitor

# Private/local IPs to skip geolocation
LOCAL_IPS = ('127.0.0.1', 'localhost', '::1')


def track_visitor(request):
    """Track visitor with 30-minute session-based deduplication."""
    page = request.path
    now = timezone.now()

    # Skip if visited this page within 30 minutes
    visited = request.session.get('visited_pages', {})
    if page in visited:
        try:
            last = datetime.fromisoformat(visited[page])
            if timezone.is_naive(last):
                last = timezone.make_aware(last)
            if (now - last) < timedelta(minutes=30):
                return
        except (ValueError, TypeError):
            pass

    # Update session
    visited[page] = now.isoformat()
    request.session['visited_pages'] = visited

    # Get visitor info (check proxy headers for real IP)
    # Priority: CF-Connecting-IP > X-Real-IP > X-Forwarded-For > REMOTE_ADDR
    ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if not ip:
        ip = request.META.get('HTTP_X_REAL_IP')
    if not ip:
        xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if xff:
            # X-Forwarded-For can contain: client, proxy1, proxy2
            # The first IP is the real client IP
            ip = xff.split(',')[0].strip()
    if not ip:
        ip = request.META.get('REMOTE_ADDR', '')
    ua_string = request.META.get('HTTP_USER_AGENT', '')[:500]

    # Parse user agent
    ua_info = _parse_user_agent(ua_string)
    geo_info = _get_geolocation(ip)

    Visitor.objects.create(
        ip_address=ip,
        page=page,
        user_agent=ua_string,
        **ua_info,
        **geo_info,
    )


def _parse_user_agent(ua_string):
    """Extract browser, OS, and device type from user agent."""
    try:
        ua = parse_ua(ua_string)
        if ua.is_mobile:
            device = 'mobile'
        elif ua.is_tablet:
            device = 'tablet'
        else:
            device = 'desktop'
        browser = f"{ua.browser.family} {ua.browser.version_string}"
        os_info = f"{ua.os.family} {ua.os.version_string}"
        return {
            'browser': browser.strip(),
            'operating_system': os_info.strip(),
            'device_type': device,
        }
    except Exception:
        return {'browser': '', 'operating_system': '', 'device_type': ''}


def _get_geolocation(ip):
    """Get country and city from IP using ip-api.com."""
    if ip in LOCAL_IPS:
        return {'country': '', 'city': '', 'latitude': None, 'longitude': None}
    try:
        resp = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', ''),
                    'city': data.get('city', ''),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                }
    except Exception:
        pass
    return {'country': '', 'city': '', 'latitude': None, 'longitude': None}


def home(request):
    track_visitor(request)
    projects = Project.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        user_message = request.POST.get('message')

        if name and email and user_message:
            Contact.objects.create(name=name, email=email, message=user_message)
            messages.success(request, 'Thank you! Your message has been sent.')
            return redirect('home')

    return render(request, 'home.html', {'projects': projects})


@staff_member_required
def visitor_stats(request):
    """Dashboard for viewing visitor statistics."""
    now = timezone.now()
    today = now.date()

    # Helper for counting by field
    def count_by(field, exclude_empty=True, limit=None):
        if exclude_empty:
            qs = Visitor.objects.exclude(**{field: ''})
        else:
            qs = Visitor.objects
        qs = qs.values(field).annotate(count=Count('id')).order_by('-count')
        return qs[:limit] if limit else qs

    # Active visitors (last 5 min)
    active_qs = Visitor.objects.filter(
        visited_at__gte=now - timedelta(minutes=5)
    )
    active_unique = active_qs.values('ip_address', 'user_agent').distinct()

    # Today's visitors
    today_qs = Visitor.objects.filter(visited_at__date=today)
    today_unique = today_qs.values('ip_address', 'user_agent').distinct()

    # All unique visitors
    all_unique = Visitor.objects.values('ip_address', 'user_agent').distinct()

    # Daily visits (last 7 days)
    daily_qs = Visitor.objects.filter(
        visited_at__date__gte=today - timedelta(days=6)
    ).annotate(
        date=TruncDate('visited_at')
    ).values('date').annotate(count=Count('id')).order_by('date')

    # Visitors with coordinates for map (last 100)
    map_visitors = list(
        Visitor.objects.exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
        .values('city', 'country', 'latitude', 'longitude')[:100]
    )

    context = {
        'active_count': active_unique.count(),
        'active_visitors': active_qs[:10],
        'total_visitors': Visitor.objects.count(),
        'today_visitors': today_qs.count(),
        'unique_today': today_unique.count(),
        'unique_total': all_unique.count(),
        'daily_visits': list(daily_qs),
        'top_pages': count_by('page', exclude_empty=False, limit=10),
        'top_browsers': count_by('browser', limit=5),
        'device_breakdown': count_by('device_type'),
        'top_countries': count_by('country', limit=10),
        'recent_visitors': Visitor.objects.all()[:20],
        'map_visitors': json.dumps(map_visitors),
    }
    return render(request, 'visitor_stats.html', context)
