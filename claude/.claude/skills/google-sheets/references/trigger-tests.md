# Trigger tests

A simple trigger (`onOpen`, `onEdit`) fires only on a person's open or edit, never on an API
write. A test therefore calls the handler itself, through `clasp run-function`, with the event
object Google would have passed.

## Thin handlers

A handler checks its event and hands the work to a named function that takes a sheet or a range:

```javascript
function onEdit(e) {
  const tab = SORTED_TABS.find((t) => t.name === e.range.getSheet().getName());
  if (!tab || e.range.getColumn() !== 1) return;
  sortTab_(tab);
}
```

UI calls (`SpreadsheetApp.getUi()`, menus, dialogs) stay in the handler, because they throw when
the script runs through the Execution API. No one sees a `Spreadsheet.toast` from an API run, so
a test checks the cells, never a toast. Whether `toast` throws there is unverified: if a handler
toasts on success, run its test once and read the result before relying on it. If a handler can't
shed its UI calls, test the work function alone and say so in the PR.

## `tests.gs`

One public function per case. Each builds the event from the live sheet, calls the real handler,
and returns a short summary:

```javascript
function testOnEditRosterName() {
  const ss = SpreadsheetApp.getActive();
  const range = ss.getSheetByName('Roster').getRange('A3');
  const value = range.getValue();
  onEdit({ source: ss, range: range, value: value, oldValue: value });
  return ss.getSheetByName('Roster').getRange('A3:A12').getValues().flat();
}
```

The `onEdit` event's fields are `authMode`, `oldValue`, `range`, `source`, `triggerUid`, `user`,
and `value`; `onOpen` takes `authMode`, `source`, `triggerUid`, and `user`
(developers.google.com/apps-script/guides/triggers/events). Build only the fields the handler
reads.

Rules:

- No trailing underscore: the Execution API can't call a private function.
- A test changes only what the handler would. Retyping a value with itself keeps the data the same.
- The return value helps a reader, but the evidence is a `gws` read of the cells afterwards.
- The file ships with the script, so coaches see it in the editor. Open it with one comment saying
  the functions are for Claude's tests and change nothing unless run.

## What a test can't show

A built event proves the handler's logic. It doesn't prove that a real edit fires the trigger, and
it shows nothing on screen. When either matters, the test procedure ends with Geoff's browser
check (SKILL.md, step 6).
