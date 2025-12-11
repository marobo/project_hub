from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import requests
from user_agents import parse as parse_ua
from .models import Project, Contact, Visitor


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def get_geolocation(ip_address):
    """Get country and city from IP address using ip-api.com"""
    try:
        # Skip private/local IPs
        if ip_address in ('127.0.0.1', 'localhost', '::1'):
            return {'country': '', 'city': ''}
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}',
            timeout=2
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', ''),
                    'city': data.get('city', '')
                }
    except Exception:
        pass
    return {'country': '', 'city': ''}


def parse_user_agent(ua_string):
    """Parse user agent string to extract browser, OS, and device type"""
    try:
        ua = parse_ua(ua_string)
        device_type = 'mobile' if ua.is_mobile else (
            'tablet' if ua.is_tablet else 'desktop'
        )
        browser = f"{ua.browser.family} {ua.browser.version_string}"
        os_name = f"{ua.os.family} {ua.os.version_string}"
        return {
            'browser': browser.strip(),
            'operating_system': os_name.strip(),
            'device_type': device_type
        }
    except Exception:
        return {'browser': '', 'operating_system': '', 'device_type': ''}


def track_visitor(request):
    """Track visitor with session-based deduplication"""
    ip_address = get_client_ip(request)
    ua_string = request.META.get('HTTP_USER_AGENT', '')[:500]
    page = request.path

    # Session-based deduplication:
    # Track which pages have been viewed in this session
    visited_pages = request.session.get('visited_pages', {})
    current_time = timezone.now()

    # Check if this page was already tracked in this session
    if page in visited_pages:
        last_visit_str = visited_pages[page]
        try:
            from datetime import datetime
            last_visit = datetime.fromisoformat(last_visit_str)
            # Make it timezone-aware if it isn't
            if timezone.is_naive(last_visit):
                last_visit = timezone.make_aware(last_visit)
            # If visited within the last 30 minutes, skip
            if (current_time - last_visit) < timedelta(minutes=30):
                return
        except (ValueError, TypeError):
            pass  # Invalid timestamp, proceed to track

    # Update session with the current page visit timestamp
    visited_pages[page] = current_time.isoformat()
    request.session['visited_pages'] = visited_pages

    # Parse user agent
    ua_info = parse_user_agent(ua_string)

    # Get geolocation
    geo_info = get_geolocation(ip_address)

    Visitor.objects.create(
        ip_address=ip_address,
        page=page,
        user_agent=ua_string,
        browser=ua_info['browser'],
        operating_system=ua_info['operating_system'],
        device_type=ua_info['device_type'],
        country=geo_info['country'],
        city=geo_info['city']
    )


def home(request):
    track_visitor(request)
    projects = Project.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            Contact.objects.create(name=name, email=email, message=message)
            messages.success(request, 'Thank you! Your message has been sent.')
            return redirect('home')

    return render(request, 'home.html', {'projects': projects})


@staff_member_required
def visitor_stats(request):
    """Dashboard for viewing visitor statistics"""
    now = timezone.now()
    today = now.date()
    last_7_days = today - timedelta(days=6)
    last_5_minutes = now - timedelta(minutes=5)

    # Currently active visitors (last 5 minutes)
    active_visitors = Visitor.objects.filter(visited_at__gte=last_5_minutes)
    active_count = active_visitors.values('ip_address').distinct().count()

    # Total visitors
    total_visitors = Visitor.objects.count()

    # Today's visitors
    today_visitors = Visitor.objects.filter(visited_at__date=today).count()

    # Unique IPs today
    unique_today = (
        Visitor.objects.filter(visited_at__date=today)
        .values('ip_address').distinct().count()
    )

    # Unique IPs total
    unique_total = Visitor.objects.values('ip_address').distinct().count()

    # Visits per day (last 7 days)
    daily_visits = (
        Visitor.objects
        .filter(visited_at__date__gte=last_7_days)
        .annotate(date=TruncDate('visited_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Top pages
    top_pages = (
        Visitor.objects
        .values('page')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # Browser breakdown
    top_browsers = (
        Visitor.objects
        .exclude(browser='')
        .values('browser')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    # Device type breakdown
    device_breakdown = (
        Visitor.objects
        .exclude(device_type='')
        .values('device_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Top countries
    top_countries = (
        Visitor.objects
        .exclude(country='')
        .values('country')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # Recent visitors
    recent_visitors = Visitor.objects.all()[:20]

    context = {
        'active_count': active_count,
        'active_visitors': active_visitors[:10],
        'total_visitors': total_visitors,
        'today_visitors': today_visitors,
        'unique_today': unique_today,
        'unique_total': unique_total,
        'daily_visits': list(daily_visits),
        'top_pages': top_pages,
        'top_browsers': top_browsers,
        'device_breakdown': device_breakdown,
        'top_countries': top_countries,
        'recent_visitors': recent_visitors,
    }

    return render(request, 'visitor_stats.html', context)
