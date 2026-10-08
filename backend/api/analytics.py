from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from database import get_db
from models.users import User, UserRole
from models.uploaded_documents import UploadedDocument, VerificationStatus
from models.conversation_logs import ConversationLog, MessageType
from models.accessibility_metrics import AccessibilityMetric


router = APIRouter(prefix="/analytics", tags=["Admin Analytics"])


@router.get("/overview")
def get_overview_analytics(db: Session = Depends(get_db)):
    """
    Live aggregate analytics directly from PostgreSQL.
    No citizen PII is returned.
    """

    now = datetime.now(timezone.utc)
    today_start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    # Registered citizens
    total_citizens = (
        db.query(User)
        .filter(
            User.role == UserRole.CITIZEN,
            User.email != "demo.citizen@accessgov.ai",
        )
        .count()
    )

    new_citizens_today = (
        db.query(User)
        .filter(
            User.role == UserRole.CITIZEN,
            User.email != "demo.citizen@accessgov.ai",
            User.created_at >= today_start,
        )
        .count()
    )

    # Documents
    total_documents = db.query(UploadedDocument).count()

    verified_documents = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.verification_status
            == VerificationStatus.VERIFIED
        )
        .count()
    )

    pending_documents = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.verification_status
            == VerificationStatus.PENDING
        )
        .count()
    )

    # Current document model does not contain an OCR/readiness column.
    # Use verification status as the aggregate readiness signal.
    avg_readiness_score = (
        (verified_documents / total_documents) * 100.0
        if total_documents
        else 0.0
    )

    ocr_success_rate = avg_readiness_score

    # Conversations
    total_conversations = (
        db.query(ConversationLog)
        .filter(
            ConversationLog.message_type == MessageType.USER
        )
        .count()
    )

    return {
        "total_citizens": total_citizens,
        "new_citizens_today": new_citizens_today,
        "total_documents": total_documents,
        "avg_readiness_score": round(avg_readiness_score, 1),
        "ocr_success_rate": round(ocr_success_rate, 1),
        "total_conversations": total_conversations,
    }


@router.get("/conversations")
def get_conversation_analytics(db: Session = Depends(get_db)):
    """
    Live conversation analytics from conversation_logs.
    Only aggregate statistics are returned.
    """

    now = datetime.now(timezone.utc)
    today_start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    user_messages = ConversationLog.message_type == MessageType.USER

    total_conversations = (
        db.query(ConversationLog)
        .filter(user_messages)
        .count()
    )

    conversations_today = (
        db.query(ConversationLog)
        .filter(
            user_messages,
            ConversationLog.timestamp >= today_start,
        )
        .count()
    )

    active_sessions_today = (
        db.query(
            func.count(
                func.distinct(ConversationLog.session_id)
            )
        )
        .filter(
            user_messages,
            ConversationLog.timestamp >= today_start,
        )
        .scalar()
        or 0
    )

    avg_latency = (
        db.query(func.avg(ConversationLog.response_time_ms))
        .filter(
            ConversationLog.response_time_ms.isnot(None)
        )
        .scalar()
        or 0
    )

    # Current schema has no confidence field.
    avg_confidence = 0.0

    # Current schema has no response_source/fallback field.
    fallback_count = 0

    language_rows = (
        db.query(
            ConversationLog.language,
            func.count(ConversationLog.id),
        )
        .filter(user_messages)
        .group_by(ConversationLog.language)
        .all()
    )

    language_distribution = [
        {
            "language": language or "unknown",
            "count": count,
        }
        for language, count in language_rows
    ]

    hourly_rows = (
        db.query(
            extract("hour", ConversationLog.timestamp),
            func.count(ConversationLog.id),
        )
        .filter(
            user_messages,
            ConversationLog.timestamp >= today_start,
        )
        .group_by(
            extract("hour", ConversationLog.timestamp)
        )
        .all()
    )

    hourly_map = {
        int(hour): count
        for hour, count in hourly_rows
    }

    hourly_activity = [
        {
            "hour": f"{hour:02d}:00",
            "count": hourly_map.get(hour, 0),
        }
        for hour in range(24)
    ]

    intent_rows = (
        db.query(
            ConversationLog.intent,
            func.count(ConversationLog.id),
        )
        .filter(
            user_messages,
            ConversationLog.intent.isnot(None),
        )
        .group_by(ConversationLog.intent)
        .all()
    )

    intent_distribution = [
        {
            "intent": intent or "unknown",
            "count": count,
        }
        for intent, count in intent_rows
    ]

    return {
        "total_conversations": total_conversations,
        "conversations_today": conversations_today,
        "active_sessions_today": active_sessions_today,
        "avg_latency_ms": int(avg_latency),
        "avg_confidence": avg_confidence,
        "fallback_count": fallback_count,
        "language_distribution": language_distribution,
        "hourly_activity": hourly_activity,
        "intent_distribution": intent_distribution,
    }


@router.get("/accessibility")
def get_accessibility_analytics(db: Session = Depends(get_db)):
    citizen_filter = (
        User.role == UserRole.CITIZEN,
        User.email != "demo.citizen@accessgov.ai",
    )

    total_citizens = db.query(User).filter(*citizen_filter).count()

    # Count actual accessibility telemetry events from PostgreSQL.
    screen_reader_users = (
        db.query(AccessibilityMetric)
        .filter(
            AccessibilityMetric.metric_name == "screen_reader_toggle",
            AccessibilityMetric.metric_value == 1.0,
        )
        .count()
    )

    high_contrast_users = (
        db.query(AccessibilityMetric)
        .filter(
            AccessibilityMetric.metric_name == "contrast_toggle",
            AccessibilityMetric.metric_value == 1.0,
        )
        .count()
    )

    font_scale_rows = (
        db.query(
            AccessibilityMetric.metric_value,
            func.count(AccessibilityMetric.id),
        )
        .filter(
            AccessibilityMetric.metric_name == "font_scale_change"
        )
        .group_by(AccessibilityMetric.metric_value)
        .order_by(AccessibilityMetric.metric_value)
        .all()
    )

    font_scale_distribution = [
        {
            "scale": f"{value:g}%",
            "count": count,
        }
        for value, count in font_scale_rows
    ]

    total_telemetry_events = db.query(AccessibilityMetric).count()

    return {
        "total_telemetry_events": total_telemetry_events,
        "font_scale_distribution": font_scale_distribution,
        "contrast_mode_distribution": [
            {
                "mode": "high-contrast",
                "count": high_contrast_users,
            }
        ],
        "screen_reader_users": screen_reader_users,
    }