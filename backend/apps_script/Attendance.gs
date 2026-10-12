/**
 * Attendance web app — bound to the IGC 2026 registration sheet.
 *
 * Why this exists: a Google Sheet shared as "anyone with the link can edit"
 * lets people edit in the browser, but it does NOT let a server write to it —
 * that needs authentication. This script runs as the sheet's owner and exposes
 * two actions to the FastAPI backend (backend/attendance.py), guarded by a
 * shared secret:
 *
 *   list   → header row + every response row
 *   write  → set attend_* / first_timer cells on one row (with safety checks)
 *
 * Setup (once) — see DEPLOY.md:
 *   1. In the sheet: Extensions → Apps Script. Paste this file over Code.gs.
 *   2. Project Settings → Script properties → add ATTENDANCE_SECRET = <long random string>.
 *   3. Deploy → New deployment → type "Web app"
 *        Execute as: Me      Who has access: Anyone
 *      Copy the /exec URL.
 *   4. Put the URL and the same secret into the backend env
 *      (ATTENDANCE_SCRIPT_URL, ATTENDANCE_SCRIPT_SECRET).
 *   Re-deploy ("Manage deployments" → edit → new version) after editing this file.
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
      ensureColumns_(sheet);
      if (body.action === 'list') return reply_(list_(sheet));
      if (body.action === 'write') return reply_(write_(sheet, body));
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

/** Adds any missing attend_* / first_timer header to the right of the form columns. */
function ensureColumns_(sheet) {
  var have = headers_(sheet).map(function (h) { return String(h).trim().toLowerCase(); });
  NEW_COLUMNS.forEach(function (name) {
    if (have.indexOf(name) !== -1) return;
    var col = sheet.getLastColumn() + 1;
    sheet.getRange(1, col).setValue(name).setFontWeight('bold');
    // Plain text so "2026-10-16 09:42" is kept as typed, not turned into a date.
    sheet.getRange(2, col, Math.max(sheet.getMaxRows() - 1, 1), 1).setNumberFormat('@');
    have.push(name);
  });
}

function list_(sheet) {
  var lastRow = sheet.getLastRow();
  var lastCol = sheet.getLastColumn();
  var rows = lastRow > 1 ? sheet.getRange(2, 1, lastRow - 1, lastCol).getDisplayValues() : [];
  return { ok: true, headers: headers_(sheet), first_row: 2, rows: rows };
}

function write_(sheet, body) {
  var row = Number(body.row);
  if (!row || row < 2 || row > sheet.getLastRow()) return { ok: false, error: 'row_changed', message: 'Row no longer exists — search again.' };

  var headers = headers_(sheet).map(function (h) { return String(h).trim().toLowerCase(); });
  var nameCol = headers.findIndex(function (h) { return h.indexOf('full name') === 0 || h === 'name'; }) + 1;
  var phoneCol = headers.findIndex(function (h) { return h.indexOf('phone') === 0; }) + 1;
  if (!nameCol) return { ok: false, error: 'script_error', message: 'No "Full Name" column found.' };

  // The row number came from an earlier read. If rows were sorted, inserted or
  // deleted since, refuse rather than tick the wrong person.
  var name = String(sheet.getRange(row, nameCol).getDisplayValue()).trim();
  var phone = phoneCol ? String(sheet.getRange(row, phoneCol).getDisplayValue()).trim() : '';
  if (name !== body.expect_name || (phoneCol && phone !== body.expect_phone)) {
    return { ok: false, error: 'row_changed', message: 'The sheet changed since you searched — search again.' };
  }

  var updates = body.updates || {};
  var guard = body.only_if_empty;
  if (guard && NEW_COLUMNS.indexOf(guard) !== -1) {
    var gcol = headers.indexOf(guard) + 1;
    var current = String(sheet.getRange(row, gcol).getDisplayValue()).trim();
    if (current) return { ok: true, already: true, current: current };
  }

  Object.keys(updates).forEach(function (key) {
    if (NEW_COLUMNS.indexOf(key) === -1) return; // never touch form columns
    var col = headers.indexOf(key) + 1;
    if (col) sheet.getRange(row, col).setNumberFormat('@').setValue(String(updates[key]));
  });
  return { ok: true, already: false };
}
