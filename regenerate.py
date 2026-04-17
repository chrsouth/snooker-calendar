#!/usr/bin/env python3
"""
Rebuild an ICS for the WST 'Upcoming Fixtures' URL.

Note:
- The WST page is JS-driven and does not reliably expose the full fixture list
  in plain HTML, so this script uses a curated schedule table based on the
  currently published order-of-play for the 2026 World Championship.
- Edit SESSIONS below if WST updates the slate.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import hashlib

TZ = "Europe/London"
LOCATION = "Crucible Theatre, Sheffield, England"
OUT_FILE = "wst_upcoming_fixtures_world_championship_2026.ics"

SESSIONS = [
    ("2026-04-18 10:00", "Zhao Xintong vs Liam Highfield", "Round 1"),
    ("2026-04-18 10:00", "Mark Allen vs Zhang Anda", "Round 1"),
    ("2026-04-18 14:30", "Xiao Guodong vs Zhou Yuelong", "Round 1"),
    ("2026-04-18 14:30", "Mark Williams vs Antoni Kowalski", "Round 1"),
    ("2026-04-18 19:00", "Zhao Xintong vs Liam Highfield", "Round 1"),
    ("2026-04-18 19:00", "Barry Hawkins vs Matthew Stevens", "Round 1"),
    ("2026-04-19 10:00", "Ding Junhui vs David Gilbert", "Round 1"),
    ("2026-04-19 10:00", "Mark Allen vs Zhang Anda", "Round 1"),
    ("2026-04-19 14:30", "John Higgins vs Ali Carter", "Round 1"),
    ("2026-04-19 14:30", "Barry Hawkins vs Matthew Stevens", "Round 1"),
    ("2026-04-19 19:00", "Xiao Guodong vs Zhou Yuelong", "Round 1"),
    ("2026-04-19 19:00", "Mark Williams vs Antoni Kowalski", "Round 1"),
    ("2026-04-20 10:00", "Ding Junhui vs David Gilbert", "Round 1"),
    ("2026-04-20 10:00", "Kyren Wilson vs Stan Moody", "Round 1"),
    ("2026-04-20 14:30", "John Higgins vs Ali Carter", "Round 1"),
    ("2026-04-20 14:30", "Wu Yize vs Lei Peifan", "Round 1"),
    ("2026-04-20 19:00", "Shaun Murphy vs Fan Zhengyi", "Round 1"),
    ("2026-04-20 19:00", "Kyren Wilson vs Stan Moody", "Round 1"),
    ("2026-04-21 10:00", "Chris Wakelin vs Liam Pullen", "Round 1"),
    ("2026-04-21 10:00", "Judd Trump vs Gary Wilson", "Round 1"),
    ("2026-04-21 14:30", "Ronnie O'Sullivan vs He Guoqiang", "Round 1"),
    ("2026-04-21 14:30", "Wu Yize vs Lei Peifan", "Round 1"),
    ("2026-04-21 19:00", "Shaun Murphy vs Fan Zhengyi", "Round 1"),
    ("2026-04-21 19:00", "Judd Trump vs Gary Wilson", "Round 1"),
    ("2026-04-22 10:00", "Chris Wakelin vs Liam Pullen", "Round 1"),
    ("2026-04-22 10:00", "Mark Selby vs Jak Jones", "Round 1"),
    ("2026-04-22 14:30", "Ronnie O'Sullivan vs He Guoqiang", "Round 1"),
    ("2026-04-22 14:30", "Si Jiahui vs Hossein Vafaei", "Round 1"),
    ("2026-04-22 19:00", "Neil Robertson vs Pang Junxu", "Round 1"),
    ("2026-04-22 19:00", "Mark Selby vs Jak Jones", "Round 1"),
    ("2026-04-23 13:00", "Si Jiahui vs Hossein Vafaei", "Round 1"),
    ("2026-04-23 13:00", "Xiao Guodong / Zhou Yuelong vs Shaun Murphy / Fan Zhengyi", "Last 16"),
    ("2026-04-23 19:00", "Neil Robertson vs Pang Junxu", "Round 1"),
    ("2026-04-23 19:00", "Kyren Wilson / Stan Moody vs Mark Allen / Zhang Anda", "Last 16"),
    ("2026-04-24 10:00", "Xiao Guodong / Zhou Yuelong vs Shaun Murphy / Fan Zhengyi", "Last 16"),
    ("2026-04-24 10:00", "Barry Hawkins / Matthew Stevens vs Mark Williams / Antoni Kowalski", "Last 16"),
    ("2026-04-24 14:30", "Zhao Xintong / Liam Highfield vs Ding Junhui / David Gilbert", "Last 16"),
    ("2026-04-24 14:30", "Kyren Wilson / Stan Moody vs Mark Allen / Zhang Anda", "Last 16"),
    ("2026-04-24 19:00", "Xiao Guodong / Zhou Yuelong vs Shaun Murphy / Fan Zhengyi", "Last 16"),
    ("2026-04-24 19:00", "Barry Hawkins / Matthew Stevens vs Mark Williams / Antoni Kowalski", "Last 16"),
    ("2026-04-25 10:00", "Chris Wakelin / Liam Pullen vs Neil Robertson / Pang Junxu", "Last 16"),
    ("2026-04-25 10:00", "Kyren Wilson / Stan Moody vs Mark Allen / Zhang Anda", "Last 16"),
    ("2026-04-25 14:30", "Zhao Xintong / Liam Highfield vs Ding Junhui / David Gilbert", "Last 16"),
    ("2026-04-25 14:30", "Si Jiahui / Hossein Vafaei vs Judd Trump / Gary Wilson", "Last 16"),
    ("2026-04-25 19:00", "John Higgins / Ali Carter vs Ronnie O'Sullivan / He Guoqiang", "Last 16"),
    ("2026-04-25 19:00", "Barry Hawkins / Matthew Stevens vs Mark Williams / Antoni Kowalski", "Last 16"),
    ("2026-04-26 10:00", "Zhao Xintong / Liam Highfield vs Ding Junhui / David Gilbert", "Last 16"),
    ("2026-04-26 10:00", "Mark Selby / Jak Jones vs Wu Yize / Lei Peifan", "Last 16"),
    ("2026-04-26 14:30", "Chris Wakelin / Liam Pullen vs Neil Robertson / Pang Junxu", "Last 16"),
    ("2026-04-26 14:30", "Si Jiahui / Hossein Vafaei vs Judd Trump / Gary Wilson", "Last 16"),
    ("2026-04-26 19:00", "John Higgins / Ali Carter vs Ronnie O'Sullivan / He Guoqiang", "Last 16"),
    ("2026-04-26 19:00", "Mark Selby / Jak Jones vs Wu Yize / Lei Peifan", "Last 16"),
    ("2026-04-27 10:00", "TBD vs TBD", "Last 16"),
    ("2026-04-27 10:00", "TBD vs TBD", "Last 16"),
    ("2026-04-27 14:30", "TBD vs TBD", "Last 16"),
    ("2026-04-27 14:30", "TBD vs TBD", "Last 16"),
    ("2026-04-27 19:00", "TBD vs TBD", "Last 16"),
    ("2026-04-27 19:00", "TBD vs TBD", "Last 16"),
    ("2026-04-28 10:00", "TBD vs TBD", "Quarter-final"),
    ("2026-04-28 10:00", "TBD vs TBD", "Quarter-final"),
    ("2026-04-28 14:30", "TBD vs TBD", "Quarter-final"),
    ("2026-04-28 14:30", "TBD vs TBD", "Quarter-final"),
    ("2026-04-28 19:00", "TBD vs TBD", "Quarter-final"),
    ("2026-04-28 19:00", "TBD vs TBD", "Quarter-final"),
    ("2026-04-29 10:00", "TBD vs TBD", "Quarter-final"),
    ("2026-04-29 10:00", "TBD vs TBD", "Quarter-final"),
    ("2026-04-29 14:30", "TBD vs TBD", "Quarter-final"),
    ("2026-04-29 14:30", "TBD vs TBD", "Quarter-final"),
    ("2026-04-29 19:00", "TBD vs TBD", "Quarter-final"),
    ("2026-04-29 19:00", "TBD vs TBD", "Quarter-final"),
    ("2026-04-30 13:00", "TBD vs TBD", "Semi-final"),
    ("2026-04-30 19:00", "TBD vs TBD", "Semi-final"),
    ("2026-05-01 10:00", "TBD vs TBD", "Semi-final"),
    ("2026-05-01 14:30", "TBD vs TBD", "Semi-final"),
    ("2026-05-01 19:00", "TBD vs TBD", "Semi-final"),
    ("2026-05-02 10:00", "TBD vs TBD", "Semi-final"),
    ("2026-05-02 14:30", "TBD vs TBD", "Semi-final"),
    ("2026-05-02 19:00", "TBD vs TBD", "Semi-final"),
    ("2026-05-03 13:00", "TBD vs TBD", "Final"),
    ("2026-05-03 19:00", "TBD vs TBD", "Final"),
    ("2026-05-04 13:00", "TBD vs TBD", "Final"),
    ("2026-05-04 19:00", "TBD vs TBD", "Final"),
]

def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def build_ics() -> str:
    dur = timedelta(hours=3, minutes=30)
    now_utc = datetime.now(tz=ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")
    out = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OpenAI//WST Fixtures Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:WST Upcoming Fixtures (World Championship 2026)",
        f"X-WR-TIMEZONE:{TZ}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    for idx, (dt_s, match, rnd) in enumerate(SESSIONS, start=1):
        start = datetime.strptime(dt_s, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(TZ))
        end = start + dur
        title = f"{match} — {rnd}"
        uid = hashlib.md5(f"{idx}|{dt_s}|{match}|{rnd}".encode()).hexdigest() + "@openai.local"
        desc = (
            "Rebuilt from the WST Upcoming Fixtures schedule table. "
            "Times are Europe/London."
        )
        out += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_utc}",
            f"DTSTART;TZID={TZ}:{start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID={TZ}:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{esc(title)}",
            f"LOCATION:{esc(LOCATION)}",
            f"DESCRIPTION:{esc(desc)}",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
            "END:VEVENT",
        ]
    out.append("END:VCALENDAR")
    return "\r\n".join(out) + "\r\n"

if __name__ == "__main__":
    with open(OUT_FILE, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(build_ics())
    print(f"Wrote {len(SESSIONS)} events to {OUT_FILE}")
