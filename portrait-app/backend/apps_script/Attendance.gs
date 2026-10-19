/**
 * Attendance web app — bound to your event's registration sheet.
 *
 * Why this exists: a Google Sheet shared as "anyone with the link can edit"
 * lets people edit in the browser, but it does NOT let a server write to it —
 * that needs authentication. This script runs as the sheet's owner and exposes
 * two actions to the FastAPI backend (backend/attendance.py), guarded by a
 * shared secret:
 *
 *   list   → header row + every response row
 *   write  → set attend_* / first_timer cells on one row (with safety checks)
 *   append → add a new row (a walk-in who never registered through the Form)
 *
 * Setup (once) — see DEPLOY.md:
 *   1. In the sheet: Extensions → Apps Script. Paste this file over Code.gs.
 *   2. Project Settings → Script properties → add ATTENDANCE_SECRET = <long random string>.
 *   3. Deploy → New deployment → type "Web app"
 *        Execute as: Me      Who has access: Anyone
 *      Copy the /exec URL.
 *   4. Put the URL and the same secret into the backend env
 *      (ATTENDANCE_SCRIPT_URL, ATTENDANCE_SCRIPT_SECRET).
 *   Re-deploy ("Manage deployments" → edit → new version) after editing this file —
 *   the live URL keeps serving the OLD code until you do.
 */

// Leave blank to use the first tab (where the Form writes responses).
var SHEET_NAME = '';

var NEW_COLUMNS = ['attend_friday', 'attend_saturday', 'attend_sunday', 'first_timer'];

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var secret = PropertiesService.getScriptProperties().getProperty('ATTENDANCE_SECRET');
    if (!secret || body.secret !== secret) return reply_({ ok: false, error: 'unauthorized' });

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      var sheet = sheet_();
      var headers = ensureColumns_(sheet);
      if (body.action === 'list') return reply_(list_(sheet, headers));
      if (body.action === 'write') return reply_(write_(sheet, headers, body));
      if (body.action === 'append') return reply_(append_(sheet, headers, body));
      return reply_({ ok: false, error: 'bad_action' });
    } finally {
      lock.releaseLock();
    }
  } catch (err) {
    return reply_({ ok: false, error: 'script_error', message: String(err) });
  }
}

function reply_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return SHEET_NAME ? ss.getSheetByName(SHEET_NAME) : ss.getSheets()[0];
}

function headers_(sheet) {
  var n = Math.max(sheet.getLastColumn(), 1);
  return sheet.getRange(1, 1, 1, n).getDisplayValues()[0];
}

/**
 * Adds any missing attend_* / first_timer header to the right of the form columns.
 * Returns the display headers (read once per request, passed to the actions).
 */
function ensureColumns_(sheet) {
  var raw = headers_(sheet);
  var have = raw.map(function (h) { return String(h).trim().toLowerCase(); });
  var added = false;
  NEW_COLUMNS.forEach(function (name) {
    if (have.indexOf(name) !== -1) return;
    var col = sheet.getLastColumn() + 1;
    sheet.getRange(1, col).setValue(name).setFontWeight('bold');
    // Plain text so "2027-01-01 09:42" is kept as typed, not turned into a date.
    sheet.getRange(2, col, Math.max(sheet.getMaxRows() - 1, 1), 1).setNumberFormat('@');
    have.push(name);
    raw.push(name);
    added = true;
  });
  return raw;
}

function list_(sheet, headers) {
  var lastRow = sheet.getLastRow();
  var lastCol = headers.length;
  var rows = lastRow > 1 ? sheet.getRange(2, 1, lastRow - 1, lastCol).getDisplayValues() : [];
  return { ok: true, headers: headers, first_row: 2, rows: rows };
}

function write_(sheet, rawHeaders, body) {
  var row = Number(body.row);
  if (!row || row < 2 || row > sheet.getLastRow()) return { ok: false, error: 'row_changed', message: 'Row no longer exists — search again.' };

  var headers = rawHeaders.map(function (h) { return String(h).trim().toLowerCase(); });
  var nameCol = headers.findIndex(function (h) { return h.indexOf('full name') === 0 || h === 'name'; });
  var phoneCol = headers.findIndex(function (h) { return h.indexOf('phone') === 0; });
  if (nameCol < 0) return { ok: false, error: 'script_error', message: 'No "Full Name" column found.' };

  // One read for the whole row (each separate read is a slow round trip).
  var cells = sheet.getRange(row, 1, 1, headers.length).getDisplayValues()[0];

  // The row number came from an earlier read. If rows were sorted, inserted or
  // deleted since, refuse rather than tick the wrong person.
  var name = String(cells[nameCol]).trim();
  var phone = phoneCol >= 0 ? String(cells[phoneCol]).trim() : '';
  if (name !== body.expect_name || (phoneCol >= 0 && phone !== body.expect_phone)) {
    return { ok: false, error: 'row_changed', message: 'The sheet changed since you searched — search again.' };
  }

  var updates = body.updates || {};
  var guard = body.only_if_empty;
  if (guard && NEW_COLUMNS.indexOf(guard) !== -1) {
    var current = String(cells[headers.indexOf(guard)] || '').trim();
    if (current) return { ok: true, already: true, current: current };
  }

  Object.keys(updates).forEach(function (key) {
    if (NEW_COLUMNS.indexOf(key) === -1) return; // never touch form columns
    var col = headers.indexOf(key) + 1;
    if (col) sheet.getRange(row, col).setNumberFormat('@').setValue(String(updates[key]));
  });
  return { ok: true, already: false };
}

/** Which logical field a header holds — mirrors _canon() in backend/attendance.py. */
function canon_(header) {
  var h = String(header).trim().toLowerCase();
  if (NEW_COLUMNS.indexOf(h) !== -1) return h;
  if (h.indexOf('timestamp') === 0) return 'timestamp';
  if (h.indexOf('full name') === 0 || h === 'name') return 'name';
  if (h.indexOf('phone') === 0) return 'phone';
  if (h.indexOf('gender') === 0) return 'gender';
  if (h.indexOf('age group') === 0) return 'age_group';
  if (h.indexOf('church') === 0) return 'church';
  if (h.indexOf('transport') !== -1) return 'transport';
  if (h.indexOf('joining us from') !== -1) return 'area';
  if (h.indexOf('hear about') !== -1) return 'source';
  return null;
}

/**
 * Adds a row for a walk-in. `cells` is keyed by logical field (name, phone,
 * gender, … attend_friday, first_timer); anything not given stays blank.
 */
function append_(sheet, rawHeaders, body) {
  var cells = body.cells || {};
  if (!String(cells.name || '').trim()) return { ok: false, error: 'bad_request', message: 'A name is required.' };
  var row = sheet.getLastRow() + 1;
  rawHeaders.forEach(function (h, i) {
    var key = canon_(h);
    if (!key || !(key in cells)) return;
    var range = sheet.getRange(row, i + 1);
    // Phones keep their leading 0; our stamps stay as typed. The timestamp is
    // left alone so Sheets parses it exactly as it does for a Form response.
    if (key === 'phone' || NEW_COLUMNS.indexOf(key) !== -1) range.setNumberFormat('@');
    range.setValue(String(cells[key]));
  });
  return { ok: true, row: row };
}
