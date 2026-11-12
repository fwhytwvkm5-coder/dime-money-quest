"""Builds Dime_Leak_Scanner.xlsx (free lead magnet). Run: python3 build_xlsx.py"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.comments import Comment

OUT = "Dime_Leak_Scanner.xlsx"
INK, GOLD, CREAM, GREY, INPUT = "18122A", "FFC828", "FFF8E1", "EDEDF2", "FFF2CC"
F = "Arial"
EUR = '€#,##0.00;-€#,##0.00;-'
EUR0 = '€#,##0;-€#,##0;-'
LEAKS = ["Snacks & coffee", "Takeout & delivery", "Rides & transport", "Subscriptions & apps",
         "Shopping & impulse buys", "Going out", "Fees & interest", "Groceries & essentials", "Other"]
thin = Side(style="thin", color="C8C8D2")
box = Border(left=thin, right=thin, top=thin, bottom=thin)

def title(ws, text, sub=None, width="H"):
    ws.merge_cells(f"A1:{width}1")
    ws["A1"] = text
    ws["A1"].font = Font(name=F, size=16, bold=True, color=GOLD)
    ws["A1"].fill = PatternFill("solid", fgColor=INK)
    ws["A1"].alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 34
    if sub:
        ws.merge_cells(f"A2:{width}2")
        ws["A2"] = sub
        ws["A2"].font = Font(name=F, size=10, italic=True, color="5A5A6E")
        ws["A2"].alignment = Alignment(indent=1)

def header(ws, row, labels):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = Font(name=F, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="3C3264")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = box
    ws.row_dimensions[row].height = 30

def body(c, fmt=None, inp=False, bold=False, italic=False, color="000000"):
    c.font = Font(name=F, bold=bold, italic=italic, color=color)
    if fmt: c.number_format = fmt
    if inp: c.fill = PatternFill("solid", fgColor=INPUT)
    c.border = box

wb = Workbook()

# ---------- Start Here ----------
ws = wb.active; ws.title = "Start Here"
title(ws, "DIME'S LEAK SCANNER", "Find out where your money drips away, in 7 days. Free from @dimesmoneyquest.", "B")
ws.column_dimensions["A"].width = 6; ws.column_dimensions["B"].width = 92
rows = [
    ("", "HOW IT WORKS"),
    ("1", "For 7 days, write down EVERY spend in the tab '7-Day Log'. Even €1. Card, cash, apps, everything."),
    ("2", "For each spend, pick a leak type from the dropdown and answer 'Needed?' honestly: Yes or No."),
    ("3", "On day 7, open 'Scan Results'. It shows each leak per week, per month and per year, and your biggest leak."),
    ("4", "Bonus: list every subscription in 'Subscription Scan'. Anything you haven't used in 30+ days gets flagged."),
    ("5", "Pick ONE leak and plug it this week (see the Plug Plan in the PDF guide). Then scan again next month."),
    ("", ""),
    ("", "COLOUR KEY"),
    ("", "Yellow cells = you type here.   White cells = calculated for you, don't type over them."),
    ("", "Grey rows marked EXAMPLE only show the format. They are not counted in any total."),
    ("", ""),
    ("", "GOOD TO KNOW"),
    ("", "Weekly amounts are scaled to a full 7 days if you logged fewer days. Per year = per week x 52. Per month = per year / 12."),
    ("", "Amounts are in €. The tool only adds up what you type; it doesn't connect to your bank."),
    ("", "This is a tracking tool, not financial advice."),
]
for i, (n, txt) in enumerate(rows, start=4):
    a, b = ws.cell(row=i, column=1, value=n), ws.cell(row=i, column=2, value=txt)
    head = txt.isupper() and txt != ""
    a.font = Font(name=F, bold=True, size=12, color=GOLD if n else "000000")
    a.fill = PatternFill("solid", fgColor=INK) if n else PatternFill()
    a.alignment = Alignment(horizontal="center", vertical="center")
    b.font = Font(name=F, bold=head, size=12 if head else 11, color="3C3264" if head else "000000")
    b.alignment = Alignment(wrap_text=True, vertical="center")
ws["B13"].fill = PatternFill("solid", fgColor=INPUT)
ws.sheet_view.showGridLines = False

# ---------- Lists (hidden) ----------
ls = wb.create_sheet("Lists")
for i, l in enumerate(LEAKS, 1): ls.cell(row=i, column=1, value=l)
ls.cell(row=1, column=2, value="Yes"); ls.cell(row=2, column=2, value="No")
ls.sheet_state = "hidden"

# ---------- 7-Day Log ----------
lg = wb.create_sheet("7-Day Log")
title(lg, "7-DAY LOG", "Type every spend in the yellow rows. Day = 1 to 7.", "G")
for col, w in zip("ABCDEFG", (7, 13, 40, 13, 26, 11, 22)): lg.column_dimensions[col].width = w
header(lg, 4, ["Day", "Date", "What did you buy?", "Amount (€)", "Leak type", "Needed?", ""])
ex = [1, "Mon", "Iced coffee on the way to work", 4.5, "Snacks & coffee", "No", "EXAMPLE (not counted)"]
for i, v in enumerate(ex, 1):
    c = lg.cell(row=5, column=i, value=v)
    body(c, EUR if i == 4 else None, italic=True, color="7A7A8C")
    c.fill = PatternFill("solid", fgColor=GREY)
FIRST, LAST = 7, 156
lg.cell(row=6, column=1, value="Your spends start below").font = Font(name=F, bold=True, color="3C3264")
for r in range(FIRST, LAST + 1):
    for col in range(1, 7):
        body(lg.cell(row=r, column=col), EUR if col == 4 else ("DD.MM." if col == 2 else None), inp=True)
dv_day = DataValidation(type="whole", operator="between", formula1="1", formula2="7", showErrorMessage=True,
                        errorTitle="Day 1-7", error="Use a number from 1 to 7.")
dv_amt = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", showErrorMessage=True,
                        error="Type the amount as a positive number, e.g. 4.50")
dv_leak = DataValidation(type="list", formula1=f"=Lists!$A$1:$A${len(LEAKS)}", showErrorMessage=True,
                         error="Pick a leak type from the list.")
dv_need = DataValidation(type="list", formula1='"Yes,No"', showErrorMessage=True, error="Yes or No.")
for dv, col in ((dv_day, "A"), (dv_amt, "D"), (dv_leak, "E"), (dv_need, "F")):
    lg.add_data_validation(dv); dv.add(f"{col}{FIRST}:{col}{LAST}")
lg["G4"] = "Running total"
lg["G7"] = f"=SUM(D{FIRST}:D{LAST})"; body(lg["G7"], EUR, bold=True)
lg["G8"] = "logged so far"; lg["G8"].font = Font(name=F, italic=True, color="5A5A6E")
lg.freeze_panes = "A7"

# ---------- Scan Results ----------
sr = wb.create_sheet("Scan Results")
title(sr, "SCAN RESULTS", "Calculated from your 7-Day Log. Fill in your monthly take-home pay (optional) in the yellow cell.", "H")
for col, w in zip("ABCDEFGH", (28, 14, 14, 14, 14, 14, 16, 22)): sr.column_dimensions[col].width = w
L = "'7-Day Log'"
info = [("Monthly take-home pay (€), optional", None, EUR0, True),
        ("Days logged", f"=MAX({L}!A{FIRST}:A{LAST})", "0", False),
        ("Scale to a full week", "=IF(B5>0,7/B5,0)", "0.00", False)]
for i, (lab, f, fmt, inp) in enumerate(info, start=4):
    sr.cell(row=i, column=1, value=lab).font = Font(name=F, bold=True)
    c = sr.cell(row=i, column=2, value=f); body(c, fmt, inp=inp)
sr["C6"] = "(7 / days logged)"; sr["C6"].font = Font(name=F, italic=True, color="5A5A6E")
H0 = 8
header(sr, H0, ["Leak type", "Logged (€)", "Not needed (€)", "Per week (€)", "Per month (€)", "Per year (€)", "Not needed per year (€)", "Share of pay / month"])
for k, leak in enumerate(LEAKS):
    r = H0 + 1 + k
    sr.cell(row=r, column=1, value=leak)
    sr.cell(row=r, column=2, value=f'=SUMIFS({L}!$D${FIRST}:$D${LAST},{L}!$E${FIRST}:$E${LAST},A{r})')
    sr.cell(row=r, column=3, value=f'=SUMIFS({L}!$D${FIRST}:$D${LAST},{L}!$E${FIRST}:$E${LAST},A{r},{L}!$F${FIRST}:$F${LAST},"No")')
    sr.cell(row=r, column=4, value=f"=B{r}*$B$6")
    sr.cell(row=r, column=6, value=f"=D{r}*52")
    sr.cell(row=r, column=5, value=f"=F{r}/12")
    sr.cell(row=r, column=7, value=f"=C{r}*$B$6*52")
    sr.cell(row=r, column=8, value=f'=IF($B$4>0,E{r}/$B$4,"")')
    for col in range(1, 9):
        body(sr.cell(row=r, column=col), None if col == 1 else ("0.0%" if col == 8 else EUR))
TOT = H0 + 1 + len(LEAKS)
sr.cell(row=TOT, column=1, value="TOTAL")
for col, letter in zip(range(2, 8), "BCDEFG"):
    sr.cell(row=TOT, column=col, value=f"=SUM({letter}{H0+1}:{letter}{TOT-1})")
sr.cell(row=TOT, column=8, value=f'=IF($B$4>0,E{TOT}/$B$4,"")')
for col in range(1, 9):
    c = sr.cell(row=TOT, column=col); body(c, None if col == 1 else ("0.0%" if col == 8 else EUR), bold=True)
    c.fill = PatternFill("solid", fgColor=CREAM)
# headline results
R = TOT + 2
res = [
    ("YOUR BIGGEST LEAK (not-needed spends)", f'=IF(G{TOT}=0,IF(F{TOT}=0,"Log some spends first","No not-needed spends yet"),INDEX(A{H0+1}:A{TOT-1},MATCH(MAX(G{H0+1}:G{TOT-1}),G{H0+1}:G{TOT-1},0)))', None),
    ("...costs you per year", f"=MAX(G{H0+1}:G{TOT-1})", EUR0),
    ("Spends you said you didn't need, per year", f"=G{TOT}", EUR0),
    ("PLUG HALF of those: you keep per month", f"=G{TOT}/2/12", EUR),
    ("PLUG HALF of those: you keep per year", f"=G{TOT}/2", EUR0),
    ("Leak level", f'=IF(F{TOT}=0,"-",IF(G{TOT}/12<25,"Tiny drip",IF(G{TOT}/12<100,"Leak Gang scout",IF(G{TOT}/12<250,"Leak Gang","LEAK GANG BOSS"))))', None),
]
for i, (lab, f, fmt) in enumerate(res):
    a = sr.cell(row=R + i, column=1, value=lab); a.font = Font(name=F, bold=True, color="3C3264")
    sr.merge_cells(start_row=R + i, start_column=2, end_row=R + i, end_column=3)
    c = sr.cell(row=R + i, column=2, value=f); body(c, fmt, bold=True)
    c.fill = PatternFill("solid", fgColor=CREAM)
sr.cell(row=R + 5, column=4, value="Not-needed spends per month: under €25 tiny drip · €25-99 scout · €100-249 Leak Gang · €250+ boss").font = Font(name=F, italic=True, size=9, color="5A5A6E")
sr.cell(row=R + 7, column=1, value="How it's calculated: per week = logged x (7 / days logged); per year = per week x 52; per month = per year / 12.").font = Font(name=F, italic=True, size=9, color="5A5A6E")
sr.freeze_panes = "A9"
sr.sheet_view.showGridLines = False

# ---------- Subscription Scan ----------
ss = wb.create_sheet("Subscription Scan")
title(ss, "SUBSCRIPTION SCAN", "List every subscription. Not used in 30+ days = cancel candidate.", "F")
for col, w in zip("ABCDEF", (32, 16, 20, 14, 16, 22)): ss.column_dimensions[col].width = w
header(ss, 4, ["Subscription", "Cost per month (€)", "Days since you last used it", "Verdict", "Per year (€)", ""])
ex = ["Music streaming", 9.99, 45]
for i, v in enumerate(ex, 1):
    c = ss.cell(row=5, column=i, value=v); body(c, EUR if i == 2 else None, italic=True, color="7A7A8C"); c.fill = PatternFill("solid", fgColor=GREY)
for col, f in ((4, '=IF(B5="","",IF(C5>30,"CANCEL?","KEEP"))'), (5, "=B5*12")):
    c = ss.cell(row=5, column=col, value=f); body(c, EUR if col == 5 else None, italic=True, color="7A7A8C"); c.fill = PatternFill("solid", fgColor=GREY)
ss.cell(row=5, column=6, value="EXAMPLE (not counted)").font = Font(name=F, italic=True, color="7A7A8C")
S0, S1 = 7, 31
ss.cell(row=6, column=1, value="Your subscriptions start below").font = Font(name=F, bold=True, color="3C3264")
for r in range(S0, S1 + 1):
    for col in (1, 2, 3): body(ss.cell(row=r, column=col), EUR if col == 2 else "0", inp=True)
    body(ss.cell(row=r, column=4, value=f'=IF(B{r}="","",IF(C{r}>30,"CANCEL?","KEEP"))'), bold=True)
    body(ss.cell(row=r, column=5, value=f'=IF(B{r}="","",B{r}*12)'), EUR)
red = PatternFill("solid", fgColor="FFD6DC"); green = PatternFill("solid", fgColor="D6F5DF")
ss.conditional_formatting.add(f"D{S0}:D{S1}", FormulaRule(formula=[f'$D{S0}="CANCEL?"'], fill=red, font=Font(name=F, bold=True, color="C0102C")))
ss.conditional_formatting.add(f"D{S0}:D{S1}", FormulaRule(formula=[f'$D{S0}="KEEP"'], fill=green))
T = S1 + 2
for i, (lab, f) in enumerate([("All subscriptions per year", f"=SUM(E{S0}:E{S1})"),
                              ("Cancel candidates per month", f'=SUMIFS(B{S0}:B{S1},D{S0}:D{S1},"CANCEL?")'),
                              ("Cancel candidates per year", f'=SUMIFS(E{S0}:E{S1},D{S0}:D{S1},"CANCEL?")')]):
    ss.cell(row=T + i, column=1, value=lab).font = Font(name=F, bold=True, color="3C3264")
    c = ss.cell(row=T + i, column=2, value=f); body(c, EUR, bold=True); c.fill = PatternFill("solid", fgColor=CREAM)
ss.freeze_panes = "A7"

for sh in (ws, lg, sr, ss):   # print: landscape, one page wide
    sh.page_setup.orientation = "landscape"; sh.sheet_properties.pageSetUpPr.fitToPage = True
    sh.page_setup.fitToWidth = 1; sh.page_setup.fitToHeight = 0
wb.move_sheet("Lists", offset=10)
wb.active = 0
wb.properties.title = "Dime's Leak Scanner"; wb.properties.creator = "@dimesmoneyquest"
wb.save(OUT)
print("saved", OUT)
