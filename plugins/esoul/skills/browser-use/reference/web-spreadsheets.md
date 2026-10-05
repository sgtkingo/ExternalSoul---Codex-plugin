# Grids that live in a web app

Excel for the web, Google Sheets and their kin paint the grid to a **canvas**. There are no cell
elements to select, no text to read back, and the ordinary automation instincts all fail quietly.

## The loop

1. **Open the file and prove which one it is** — read the document title back and assert the
   expected name before a single keystroke.
2. **Wait for the grid.** Read the page until its text contains both the sheet-tab name and the
   cell-reference box. A blank editor frame accepts keystrokes and swallows them.
3. **Check the right worksheet is selected** (the read shows `<name> [selected]`) and that the mode
   is *Editing*, not *Viewing*.
4. **Write each cell by reference** — never by clicking into the grid:
   ```
   press_key  ["Escape", "ControlOrMeta+G"]     // Go To: its field is focused on open
   type       "B18"   clear: true  enter: true  // the reference
   type       "<value>"             enter: true // the value
   ```
   `clear` is load-bearing — the Go To field remembers, and `O43` typed twice becomes `O43O43`.
5. **Download the file and diff it** against the pristine copy: did my cells land, and did anything
   else change?
6. **Retry the failures, diff again**, until clean.

## Grid-specific traps

**Decimals follow the workbook's locale.** `6,8` in a Czech or German sheet, `6.8` in an English
one. Get it wrong and the value silently becomes a date. Copy the format from a row a human filled.

**Two stray values can blank a whole column.** Anything written into the range a spilling array
formula needs turns it into `#SPILL!`, and every computed value below disappears. If a column of
dates or totals goes empty, look for something written into its spill range — not for a broken
formula.

**Do not walk with arrow keys.** Merged ranges swallow them: one `ArrowRight` out of a `D:N` merge
lands in `O`, and a 25-press run landed one row low twice running. Address every cell by reference.

**Paste is not universal.** Clipboard paste writes nothing into Excel for the web — it returns
success and does nothing — while Google Sheets accepts it. Do not assume across applications.

**Long values need slicing.** Typing several hundred characters in one call can blow the transport
timeout *mid-value*, leaving the cell half-written, which is worse than not starting.

**Dropdown-validated columns take the exact list text.** Read the value an existing row uses and
write it byte-for-byte; a shortened label breaks validation and makes your period the odd one out.

## Reconciliation

Most real sheets have a check cell — hours remaining, a difference, a balance. **Drive it to zero
and confirm it from the downloaded file.** It is a far better witness than any individual cell:
one wrong entry among forty looks entirely plausible, while a total of 46 294 hours does not.
