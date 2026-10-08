from datetime import datetime, timezone
import hashlib

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.users import User
from models.analytics_events import AnalyticsEvent
from models.accessibility_metrics import AccessibilityMetric
from auth.dependencies import get_current_active_user


router = APIRouter(prefix="/accessibility", tags=["Accessibility Telemetry"])


@router.post("/event")
def record_accessibility_event(
    event: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Record anonymized accessibility telemetry for an authenticated user.
    No email, phone number, Aadhaar number, or document data is stored.
    """

    event_type = event.get("event_type", "unknown")

    user_hash = hashlib.sha256(
        f"accessgov-user-{current_user.id}".encode("utf-8")
    ).hexdigest()

    metric_value = 1.0

    if event_type == "font_scale_change":
        metric_value = float(event.get("font_scale", 100))

    elif event_type == "contrast_toggle":
        metric_value = 1.0 if event.get("contrast_mode") == "high-contrast" else 0.0

    elif event_type == "screen_reader_toggle":
        metric_value = 1.0 if event.get("screen_reader_enabled") else 0.0

    elif event_type == "voice_access_toggle":
        metric_value = 1.0 if event.get("enabled") else 0.0

    metric = AccessibilityMetric(
        metric_name=event_type,
        metric_value=metric_value,
        page_or_component="citizen_portal",
        device_type="web",
        timestamp=datetime.now(timezone.utc),
    )

    db.add(metric)

    analytics_event = AnalyticsEvent(
        user_hash=user_hash,
        event_type=event_type,
        payload={
            "font_scale": event.get("font_scale"),
            "contrast_mode": event.get("contrast_mode"),
            "screen_reader_enabled": event.get("screen_reader_enabled"),
        },
        created_at=datetime.now(timezone.utc),
    )

    db.add(analytics_event)

    db.commit()

    return {
        "status": "recorded",
        "event_type": event_type,
    }
