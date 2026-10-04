from .models import HostelSetting

def hostel_settings(request):
    """Context processor providing hostel_settings to all templates."""
    try:
        settings = HostelSetting.get_settings()
    except Exception:
        settings = None
    return {
        "hostel_settings": settings
    }
