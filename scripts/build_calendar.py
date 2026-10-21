"""Build the subscription feed from reviewed source data (Python standard library)."""
import json
import re
from datetime import datetime, timedelta
from html import escape as html_escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def escape(value):
    return value.replace('\\', '\\\\').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')


def fold(line):
    result, current = [], ''
    for char in line:
        if len((current + char).encode('utf-8')) > 75:
            result.append(current)
            current = ' '
        current += char
    return '\r\n'.join(result + [current])


def build():
    data = json.loads((ROOT / 'data/calendar.json').read_text())
    year, zone = data['year'], ZoneInfo(data['timezone'])
    stamp = data['updated'].replace('-', '') + 'T120000Z'
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Ramazan Berlin//Calendar//DE',
             'CALSCALE:GREGORIAN', f'X-WR-CALNAME:Ramazan {year} · Berlin',
             'X-WR-TIMEZONE:Europe/Berlin', 'X-APPLE-CALENDAR-COLOR:#174C3D',
             'BEGIN:VTIMEZONE', 'TZID:Europe/Berlin', 'X-LIC-LOCATION:Europe/Berlin',
             'BEGIN:DAYLIGHT', 'TZOFFSETFROM:+0100', 'TZOFFSETTO:+0200', 'TZNAME:CEST',
             'DTSTART:19960331T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU', 'END:DAYLIGHT',
             'BEGIN:STANDARD', 'TZOFFSETFROM:+0200', 'TZOFFSETTO:+0100', 'TZNAME:CET',
             'DTSTART:19961027T030000', 'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU', 'END:STANDARD',
             'END:VTIMEZONE']

    def event(uid, title, day, clock=None, end_date=None, description='', reminder=None):
        lines.extend(['BEGIN:VEVENT', f'UID:{uid}', f'DTSTAMP:{stamp}', f'LAST-MODIFIED:{stamp}',
                      'SEQUENCE:1', 'STATUS:CONFIRMED', 'TRANSP:TRANSPARENT'])
        if clock:
            start = datetime.fromisoformat(f'{day}T{clock}:00').replace(tzinfo=zone)
            end = start + timedelta(minutes=5)
            lines.extend([f'DTSTART;TZID=Europe/Berlin:{start:%Y%m%dT%H%M%S}',
                          f'DTEND;TZID=Europe/Berlin:{end:%Y%m%dT%H%M%S}'])
        else:
            lines.extend([f'DTSTART;VALUE=DATE:{day.replace("-", "")}',
                          f'DTEND;VALUE=DATE:{end_date.replace("-", "")}'])
        lines.extend([f'SUMMARY:{escape(title)}', f'DESCRIPTION:{escape(description)}',
                      f'LOCATION:{escape(data["city"])}', f'URL:{data["source"]["url"]}'])
        if reminder is not None:
            trigger = '-PT30M' if reminder == 30 else 'PT0S'
            lines.extend(['BEGIN:VALARM', f'TRIGGER:{trigger}', 'ACTION:DISPLAY',
                          f'DESCRIPTION:{escape(title)}', 'END:VALARM'])
        lines.append('END:VEVENT')

    source = f'Quelle: {data["source"]["name"]}\n{data["source"]["document"]}'
    for day in data['days']:
        event(day['imsakUid'], 'Imsak – Fastenbeginn', day['date'], day['imsak'],
              description=source, reminder=30)
        event(day['iftarUid'], 'Akşam – Iftar (Fastenbrechen)', day['date'], day['iftar'],
              description=source, reminder=0)
    for item in data['events']:
        title = item['title']
        if not item['verified']:
            title += ' – Uhrzeit vor Ort bestätigen'
        event(item['uid'], title, item['date'], item.get('time'), item.get('endDate'),
              item['description'] + '\n' + source, 0 if item.get('time') else None)
    lines.append('END:VCALENDAR')
    feed = ('\r\n'.join(fold(line) for line in lines) + '\r\n').encode('utf-8')
    # Keep the original filename and all UIDs: existing subscriptions continue to work.
    (ROOT / f'Ramazan_{year}_Berlin_IGMG.ics').write_bytes(feed)
    # This year-independent URL always serves the latest reviewed edition.
    # Annual archive files and their existing subscriptions remain available.
    stable_name = f'X-WR-CALNAME:Ramazan {year} · Berlin'.encode('utf-8')
    (ROOT / 'berlin-ramazan.ics').write_bytes(
        feed.replace(stable_name, 'X-WR-CALNAME:Ramazan · Berlin'.encode('utf-8'), 1))
    rows = []
    notes = {item['date']: item['title'].split(' – ')[0]
             for item in data['events'] if item['time'] is None and 'BAYRAMI' not in item['title']}
    weekdays = ['Mo.', 'Di.', 'Mi.', 'Do.', 'Fr.', 'Sa.', 'So.']
    for index, day in enumerate(data['days'], 1):
        dt = datetime.fromisoformat(day['date'])
        note = notes.get(day['date'], '')
        css = ' class="special-row"' if note else ''
        rows.append(f'<tr{css} data-date="{day["date"]}" data-imsak="{day["imsak"]}" '
                    f'data-iftar="{day["iftar"]}"><td>{index:02d}</td>'
                    f'<td>{weekdays[dt.weekday()]} {dt:%d.%m.}</td><td>{day["imsak"]}</td>'
                    f'<td>{day["iftar"]}</td><td class="table-note">{html_escape(note)}</td></tr>')
    page = ROOT / 'index.html'
    template = page.read_text()
    template = re.sub(r'<!-- TIMES:START -->.*?<!-- TIMES:END -->',
                      '<!-- TIMES:START -->\n' + '\n'.join(rows) + '\n<!-- TIMES:END -->',
                      template, flags=re.S)
    page.write_text(template)
    print(f'Generated {len(data["days"]) * 2 + len(data["events"])} events for {year}.')


if __name__ == '__main__':
    build()
