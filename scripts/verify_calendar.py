"""Check interoperability, dates, stable identifiers, reminders and displayed times."""
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'data/calendar.json').read_text())
raw = (ROOT / f'Ramazan_{data["year"]}_Berlin_IGMG.ics').read_bytes()
assert b'\n' not in raw.replace(b'\r\n', b''), 'Non-CRLF line endings'
assert all(len(line) <= 75 for line in raw.split(b'\r\n')), 'Unfolded UTF-8 line'
assert raw.endswith(b'END:VCALENDAR\r\n')
text = re.sub(r'\r\n[ \t]', '', raw.decode())
assert 'BEGIN:VTIMEZONE\r\nTZID:Europe/Berlin' in text
stack = []
for line in text.splitlines():
    if line.startswith('BEGIN:'):
        stack.append(line[6:])
    elif line.startswith('END:'):
        assert stack.pop() == line[4:], 'Unbalanced component'
assert not stack

events = []
for block in text.split('BEGIN:VEVENT\r\n')[1:]:
    block = block.split('END:VEVENT')[0]
    entry = dict(line.split(':', 1) for line in block.splitlines() if ':' in line)
    events.append(entry)
expected_uids = {day[key] for day in data['days'] for key in ('imsakUid', 'iftarUid')}
expected_uids.update(item['uid'] for item in data['events'])
actual_uids = [entry['UID'] for entry in events]
assert len(actual_uids) == len(expected_uids) == len(set(actual_uids))
assert set(actual_uids) == expected_uids, 'Changed or duplicate UID'
index = {entry['UID']: entry for entry in events}
last_date = None
page = (ROOT / 'index.html').read_text()
for day in data['days']:
    current_date = date.fromisoformat(day['date'])
    assert current_date.year == data['year']
    if last_date:
        assert current_date - last_date == timedelta(days=1)
    last_date = current_date
    assert f'data-date="{day["date"]}" data-imsak="{day["imsak"]}" data-iftar="{day["iftar"]}"' in page
    for kind in ('imsak', 'iftar'):
        event = index[day[kind + 'Uid']]
        start = datetime.strptime(event['DTSTART;TZID=Europe/Berlin'], '%Y%m%dT%H%M%S').replace(tzinfo=ZoneInfo(data['timezone']))
        end = datetime.strptime(event['DTEND;TZID=Europe/Berlin'], '%Y%m%dT%H%M%S').replace(tzinfo=ZoneInfo(data['timezone']))
        assert start.date() == current_date and start.strftime('%H:%M') == day[kind]
        assert end - start == timedelta(minutes=5)
        assert event['TRIGGER'] == ('-PT30M' if kind == 'imsak' else 'PT0S')
for special in data['events']:
    event = index[special['uid']]
    if special['time'] is None:
        assert date.fromisoformat(special['endDate']) > date.fromisoformat(special['date'])
        assert event['DTSTART;VALUE=DATE'] == special['date'].replace('-', '')
        assert event['DTEND;VALUE=DATE'] == special['endDate'].replace('-', '')
    if not special['verified']:
        assert 'vor Ort bestätigen' in event['SUMMARY']
assert page.count('data-date=') == len(data['days'])
assert f'Ramazan_{data["year"]}_Berlin_IGMG.ics' in page
stable = (ROOT / 'berlin-ramazan.ics').read_bytes()
assert stable == raw.replace(
    f'X-WR-CALNAME:Ramazan {data["year"]} · Berlin'.encode('utf-8'),
    'X-WR-CALNAME:Ramazan · Berlin'.encode('utf-8'), 1), 'Stable feed differs from reviewed edition'
assert 'webcal://raw.githubusercontent.com/aynaligb/ramazan-2026-kalender-IGMG/refs/heads/main/berlin-ramazan.ics' in page
assert 'value="https://raw.githubusercontent.com/aynaligb/ramazan-2026-kalender-IGMG/refs/heads/main/berlin-ramazan.ics"' in page
print(f'OK: {len(events)} unique events; CRLF, folding, timezone, alarms, dates and timetable verified.')
