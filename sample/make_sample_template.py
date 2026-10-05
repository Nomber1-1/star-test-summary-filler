"""Generates a synthetic blank summary form for testing.

This is NOT Skate Canada's form. It is a minimal stand-in carrying the same
form-field names the filler script writes to, so the tool can be run and tested
without the official document. Every field is left empty.

Usage:  python make_sample_template.py [output.pdf]
"""
import sys
import pymupdf

COLS = [
    ("SkaterName",                "Skater name", 132, "text"),
    ("SkaterSkateCanadaNumber",   "Skater #",     54, "text"),
    ("TestCode",                  "Test",         42, "text"),
    ("TestDate",                  "Date",         54, "text"),
    ("EvaluatorName",             "Evaluator",    82, "text"),
    ("EvaluatorSkateCanadaNumber","Eval #",       46, "text"),
    ("TestPassedCheck",           "Pass",         24, "check"),
    ("TestFailedCheck",           "Fail",         24, "check"),
    ("TestPassedWHonoursCheck",   "Hon",          24, "check"),
    ("TestAmount",                "Amount",       36, "text"),
]
ORG = [("OrgName", "Organisation"), ("OrgNumber", "Org #"),
       ("CoordinatorName", "Coordinator"), ("CoordinatorNumber", "Coordinator #"),
       ("CoordinatorCellNumber", "Coordinator cell")]


def build(path="sample_template.pdf", slots=10):
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((30, 40), "Summary of Tests - SAMPLE TEMPLATE (synthetic)",
                     fontsize=13)
    page.insert_text((30, 58), "Not an official form. Field names match the filler script.",
                     fontsize=8)

    y = 80
    for name, label in ORG:
        page.insert_text((30, y + 9), label, fontsize=8)
        w = pymupdf.Widget()
        w.field_name = name
        w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        w.rect = pymupdf.Rect(30, y - 2, 285, y + 12)
        w.field_value = ""
        page.add_widget(w)
        y += 20

    top = 200
    x = 30
    for _, label, width, _ in COLS:
        page.insert_text((x + 1, top - 4), label, fontsize=7)
        x += width
    x = 30
    for i in range(1, slots + 1):
        ry = top + (i - 1) * 26
        for name, _, width, kind in COLS:
            w = pymupdf.Widget()
            w.field_name = f"{name}{i}"
            if kind == "check":
                w.field_type = pymupdf.PDF_WIDGET_TYPE_CHECKBOX
                w.field_value = False
            else:
                w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
                w.field_value = ""
            w.rect = pymupdf.Rect(x + 1, ry, x + width - 4, ry + 16)
            page.add_widget(w)
            x += width
        x = 30

    fy = top + slots * 26 + 18
    page.insert_text((430, fy + 10), "Total due", fontsize=8)
    w = pymupdf.Widget()
    w.field_name = "TotalAmountDue"
    w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
    w.rect = pymupdf.Rect(490, fy - 2, 582, fy + 14)
    w.field_value = ""
    page.add_widget(w)

    doc.save(path)
    n = sum(1 for p in pymupdf.open(path) for _ in p.widgets())
    print(f"wrote {path} with {n} form fields")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "sample_template.pdf")
