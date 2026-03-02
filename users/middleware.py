# users/middleware.py

from django.utils import timezone
from .models import UserSession
import user_agents

class SessionTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Track authenticated user sessions
        if request.user.is_authenticated:
            # Parse user agent
            ua_string = request.META.get('HTTP_USER_AGENT', '')
            try:
                user_agent = user_agents.parse(ua_string)
                
                device = "Mobile" if user_agent.is_mobile else "Tablet" if user_agent.is_tablet else "Desktop"
                browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
            except:
                device = "Unknown"
                browser = "Unknown"
            
            # Get or create session
            session_key = request.session.session_key
            if session_key:
                try:
                    UserSession.objects.update_or_create(
                        session_key=session_key,
                        defaults={
                            'user': request.user,
                            'device': device,
                            'browser': browser,
                            'ip_address': request.META.get('REMOTE_ADDR', ''),
                            'location': '',  # You can add IP geolocation here if needed
                            'last_activity': timezone.now(),
                        }
                    )
                except Exception as e:
                    # Log error but don't break the request
                    print(f"Error tracking session: {e}")
        
        return response