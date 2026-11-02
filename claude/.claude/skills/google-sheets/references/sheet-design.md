# Designing a sheet

A sheet people work in is an interface. Decide its screens before scripting any of it, then review
the build in the real Sheets interface. Each rule below names its source, listed at the end. Rules
marked "workstation" come from Geoff's rulings or a failure here, not from a published source.

## Separate the record from its views

Keep the record as one plain rectangle: rows are subjects, columns are variables, and a single
header row names them (Broman and Woo). Don't scatter small tables around a tab. Separate inputs,
workings, and outputs into their own tabs (FAST).

A task or a reading view gets its own tab built from that record, and each tab has one job
(workstation). A season grid, a one-day entry form, and a standings list are three screens, even
when they show the same data. An owner fixes rows in the record, and everyone else uses a view.

## Keep values consistent

- Use the same code for the same thing on every tab, and one fixed form for each kind of value
  (Broman and Woo). Dates get one format across the workbook (workstation).
- Put one thing in a cell (Broman and Woo). A cell that holds a count where its neighbors hold a
  status code is a defect.
- Keep raw data free of calculations, and put summaries on their own tab (Broman and Woo).
- Every column in a table is the same kind of thing. A separator or summary column that looks like
  data is a defect, and a workaround that needs one is a sign the structure is wrong (workstation).
- Don't store meaning in color or font. A status belongs in a column, and color only repeats it
  (Broman and Woo; Microsoft).

## Keep tables simple

- Use one header row in the record, and short, descriptive column names (Broman and Woo; Microsoft).
- Avoid merged cells in a table. Keyboard and screen-reader navigation depend on a simple rectangle
  (Microsoft). A title above a table may span it.
- Give each tab a descriptive name, never `Sheet1`, and use high contrast between text and fill
  (Microsoft).
- Choose a table (Format > Convert to table) when column types, views, and a footer suit the job
  (Google). Column types flag entries that don't match.

## Help people find and compare

These come from NN/g's four table tasks: find records, compare data, edit a row, and act on records.

- Make the first column a human-readable identifier.
- Order columns by importance, and keep related columns together.
- Freeze the header row and identifying columns when a table outgrows the screen.
- Help the eye follow a row with light rules or banding.
- Show when something is hidden or filtered.
- Editing in place suits narrow tables. Make a wide table's editable part obvious.
- A common bulk action gets row check boxes plus one select-all control.

## Make entry fast and safe

- Validate every input: a list of values, a number range, or a check box (Broman and Woo).
- Mark input cells with a fill or border as well as a font color (ICAEW).
- Design the most frequent task first, at the size of the device it happens on (workstation).
- Keep a pick list short enough to scan. A strict dropdown of dozens of items needs another way to
  navigate, and typing part of a value fails validation (workstation).

## Review the build

A PDF export isn't evidence of how a sheet looks: it hides dropdown chips, group controls, frozen
panes, and clipped cells (workstation). Before anyone else sees it, open every tab in the real
interface as its user would, and go through this list. When a defect turns up, look for its whole
class.

- [ ] Every value of one kind has one format, on every tab.
- [ ] Every column in each table holds one kind of thing, and every header is readable, unclipped.
- [ ] Each tab does one job, and the most frequent task takes the fewest steps.
- [ ] Nothing depends on color alone.
- [ ] Hidden helpers leave no marks on a visible tab.
- [ ] The sheet opens where its user needs to start.

## Sources

Read in the accepted manuscript:

- Broman and Woo, [Data Organization in Spreadsheets](https://doi.org/10.1080/00031305.2017.1375989),
  *The American Statistician*, 2018.

Read through a page summary or search excerpts, so check the wording before quoting:

- Nielsen Norman Group, [Data Tables: Four Major User Tasks](https://www.nngroup.com/articles/data-tables/).
- Google, [Use tables in Google Sheets](https://support.google.com/docs/answer/14239833).
- Microsoft, [Accessibility best practices with Excel spreadsheets](https://support.microsoft.com/en-us/office/accessibility-best-practices-with-excel-spreadsheets-6cc05fc5-1314-48b5-8eb3-683e49b3e593).

Secondhand, not read in the original, so check before leaning on them:

- FAST Standard, for financial models.
- ICAEW Financial Modelling Code.

Not reached: Stephen Few's *Show Me the Numbers*, and Schwabish's "Ten Guidelines for Better
Tables". Both are the main references on table layout, and they'd improve this page.
