from __future__ import annotations

from datetime import datetime, timezone


def _fmt_dt(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y%m%dT%H%M%SZ")


def build_ics_event(uid: str, title: str, description: str, start_dt: datetime, end_dt: datetime, location: str | None) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//USV Events Platform//EN",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{_fmt_dt(datetime.now(timezone.utc))}",
        f"DTSTART:{_fmt_dt(start_dt)}",
        f"DTEND:{_fmt_dt(end_dt)}",
        f"SUMMARY:{title}",
    ]
    if description:
        safe_desc = description.replace("\n", "\\n")
        lines.append(f"DESCRIPTION:{safe_desc}")
    if location:
        lines.append(f"LOCATION:{location}")
    lines += ["END:VEVENT", "END:VCALENDAR", ""]
    return "\r\n".join(lines)

