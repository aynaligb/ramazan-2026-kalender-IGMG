'use strict';

// The static timetable and download remain usable when JavaScript is unavailable.
const calendarAddress = document.querySelector('#calendar-url');
const copyButton = document.querySelector('#copy-url');
const copyStatus = document.querySelector('#copy-status');
copyButton.hidden = false;
copyButton.addEventListener('click', async () => {
  try {
    if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(calendarAddress.value);
    copyStatus.textContent = 'Kalenderadresse kopiert. Du kannst sie jetzt in deiner App einfügen.';
  } catch {
    calendarAddress.focus();
    calendarAddress.select();
    copyStatus.textContent = 'Bitte die markierte Adresse mit dem Kopierbefehl deines Geräts kopieren.';
  }
});
calendarAddress.addEventListener('click', () => calendarAddress.select());

const rows = [...document.querySelectorAll('#times-body tr')];
const select = document.querySelector('#day-select');
const previous = document.querySelector('#previous-day');
const next = document.querySelector('#next-day');
const today = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Berlin' }).format(new Date());
const format = new Intl.DateTimeFormat('de-DE', { weekday: 'short', day: '2-digit', month: 'long', timeZone: 'Europe/Berlin' });
let selected = Math.max(0, rows.findIndex(row => row.dataset.date === today));
const minutes = clock => Number(clock.slice(0, 2)) * 60 + Number(clock.slice(3));

if (rows.length) {
  rows.forEach((row, index) => {
    const option = document.createElement('option');
    option.value = String(index);
    option.textContent = format.format(new Date(`${row.dataset.date}T12:00:00+01:00`));
    select.append(option);
  });
  function updateDay(index) {
    selected = Math.min(rows.length - 1, Math.max(0, index));
    const row = rows[selected];
    select.value = String(selected);
    document.querySelector('#day-label').textContent = `${selected + 1}. FASTENTAG${row.dataset.date === today ? ' · HEUTE' : ''}`;
    document.querySelector('#imsak-time').textContent = row.dataset.imsak;
    document.querySelector('#iftar-time').textContent = row.dataset.iftar;
    const duration = minutes(row.dataset.iftar) - minutes(row.dataset.imsak);
    document.querySelector('#fast-duration').textContent = `${Math.floor(duration / 60)} Stunden ${duration % 60} Minuten Fastenzeit`;
    previous.disabled = selected === 0;
    next.disabled = selected === rows.length - 1;
    rows.forEach((entry, i) => entry.classList.toggle('active-row', selected === i));
  }
  previous.addEventListener('click', () => updateDay(selected - 1));
  next.addEventListener('click', () => updateDay(selected + 1));
  select.addEventListener('change', () => updateDay(Number(select.value)));
  updateDay(selected);
  document.querySelector('#day-browser').hidden = false;
  document.querySelector('#month-filters').hidden = false;
  if (today > rows.at(-1).dataset.date) {
    document.querySelector('#edition-note').textContent = 'Archiv · Ramazan 2026 ist abgeschlossen. Du siehst die geprüften Zeiten vom 19. Februar bis 19. März 2026.';
  } else if (today < rows[0].dataset.date) {
    document.querySelector('#edition-note').textContent = 'Vorschau · Der erste Fasttag dieser Ausgabe ist der 19. Februar 2026.';
  } else {
    document.querySelector('#edition-note').textContent = 'Ramazan 2026 · Der heutige Fasttag ist vorausgewählt. Alle Zeiten gelten für Berlin.';
  }
  document.querySelectorAll('[data-month]').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-month]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      rows.forEach(row => { row.hidden = button.dataset.month !== 'all' && row.dataset.date.slice(5, 7) !== button.dataset.month; });
    });
  });
}
