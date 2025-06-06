from datetime import timedelta
from django.utils import timezone
from .models import ClassSession

def start_class_session(course, session_code, department, level, semester, duration_minutes, max_students):
    """
    Creates and returns a new ClassSession object.

    Arguments:
    - course (str): Name of the course.
    - session_code (str): Unique session code.
    - department (str): Department code (must be valid choice).
    - level (str): Level code (must be valid choice).
    - semester (str): Semester code (must be valid choice).
    - duration_minutes (int): Duration of the session in minutes.
    - max_students (int): Maximum number of students that can mark attendance.

    Raises:
    - ValueError if a session with the same session_code already exists.
    """
 
    # Check if session_code already exists to avoid duplicates
    if ClassSession.objects.filter(session_code=session_code).exists():
        raise ValueError(f"Session code '{session_code}' already exists.")

    now = timezone.now()
    expires_at = now + timedelta(minutes=duration_minutes)

    session = ClassSession.objects.create(
        course=course,
        session_code=session_code,
        department=department,
        level=level,
        semester=semester,
        created_at=now,
        expires_at=expires_at,
        max_students=max_students  # Make sure your ClassSession model has this field
    )
    return session
