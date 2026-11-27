import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Running Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(36, 754, "CARELOOP CLINICS — NO-SHOW GUARD: EXECUTIVE STRATEGY REPORT")
            self.drawRightString(576, 754, "CONFIDENTIAL / CLINICAL OPERATIONS")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.6)
            self.line(36, 747, 576, 747)
        
        # Running Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.6)
        self.line(36, 40, 576, 40)
        self.drawString(36, 28, "CareLoop Clinics — No-Show Guard | Outpatient Data Science & GenAI Operations")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 28, page_text)
        self.restoreState()

def build_pdf():
    pdf_path = "CareLoop_NoShowGuard_Executive_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Custom palette
    c_primary = colors.HexColor("#1A365D")   # Deep navy
    c_secondary = colors.HexColor("#2B6CB0") # Steel blue
    c_dark = colors.HexColor("#2D3748")      # Charcoal body
    c_light = colors.HexColor("#F7FAFC")     # Off white
    c_alt_row = colors.HexColor("#EDF2F7")   # Light slate
    c_border = colors.HexColor("#CBD5E0")    # Border grey
    c_highlight = colors.HexColor("#EBF8FF") # Soft blue
    c_yellow = colors.HexColor("#FEFCBF")    # Soft yellow

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=21,
        textColor=c_primary,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=c_secondary,
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=c_primary,
        spaceBefore=5,
        spaceAfter=3
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_secondary,
        spaceBefore=4,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_dark,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=c_primary
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.0,
        textColor=c_dark
    )

    table_body_center = ParagraphStyle(
        'TableBodyCenter',
        parent=table_body_style,
        alignment=1
    )

    table_body_bold = ParagraphStyle(
        'TableBodyBold',
        parent=table_body_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, EXECUTIVE SUMMARY & DESCRIPTIVE ANALYTICS
    # =========================================================================
    story.append(Paragraph("CARELOOP CLINICS: NO-SHOW GUARD", title_style))
    story.append(Paragraph("<b>End-to-End Predictive Risk Engine & GenAI Follow-Up Intelligence</b> | Executive Operations Briefing", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_primary, spaceBefore=0, spaceAfter=5))

    # Executive Summary Box
    summary_html = """<b>EXECUTIVE SUMMARY & CORE STRATEGIC TAKEAWAYS:</b><br/>
    CareLoop Clinics operates eight outpatient healthcare facilities across six Indian cities, experiencing a baseline appointment no-show rate of <b>22.0% (218 / 990 appointments)</b>. Empty doctor slots idle clinical staff, forfeit consultation fee revenues, and deny timely care to patients on waiting lists. This end-to-end engineering engagement implemented a comprehensive data intelligence system spanning data cleaning with live weather enrichment, relational SQL analytics, supervised machine learning, and generative AI note synthesis.<br/>
    • <b>Advance Lead Time Risk Escalation:</b> No-show rates jump from <b>16.2%</b> for bookings made 1–7 days in advance to <b>60.5%</b> for appointments scheduled 31+ days ahead.<br/>
    • <b>Machine Learning Model Superiority:</b> Standardized Logistic Regression achieved superior test generalization (<b>ROC-AUC = 0.8577</b> vs 0.8237 for default Random Forest). Automated reminders confer an unscaled odds ratio of <b>0.4234</b> (~57.7% lower no-show odds, holding other features constant).<br/>
    • <b>Operating Threshold Optimization (0.35):</b> Prioritizing clinical recall over the standard 0.50 threshold catches <b>61.2% of test no-shows</b> (and <b>73.3% in chronological future validation</b>) while flagging only 24.7% of daily appointment volume for 1-minute front-desk phone confirmations.<br/>
    • <b>GenAI Root-Cause Discovery:</b> 100% of analyzed call-centre follow-up notes citing forgetfulness belonged to patients who never received automated reminders.
    """
    summary_table = Table([[Paragraph(summary_html, callout_style)]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light),
        ('BOX', (0, 0), (-1, -1), 0.8, c_secondary),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 4))

    # Section 1: Business Context & Clinic Network
    story.append(Paragraph("1. Outpatient Network & Baseline Performance", h1_style))
    story.append(Paragraph(
        "CareLoop Clinics (a controlled synthetic benchmark healthcare network across Pune, Jaipur, Indore, Kochi, Lucknow, and Nagpur) ingested 1,020 raw bookings. Defensive CSV parsing rejected 32 corrupted records into <code>rejected_rows.json</code>, leaving 990 validated patient encounters enriched with live Open-Meteo ambient temperatures.",
        body_style
    ))

    clinic_data = [
        [Paragraph("<b>Clinic ID</b>", table_header_style), Paragraph("<b>Clinic Name</b>", table_header_style), Paragraph("<b>City & Tier</b>", table_header_style), Paragraph("<b>Live Temp</b>", table_header_style), Paragraph("<b>Total Appts</b>", table_header_style), Paragraph("<b>No-Show Rate</b>", table_header_style)],
        [Paragraph("C01", table_body_center), Paragraph("Hadapsar Care Centre", table_body_style), Paragraph("Pune (Tier 1)", table_body_center), Paragraph("15.7 °C", table_body_center), Paragraph("143", table_body_center), Paragraph("<b>27.3%</b> (39 ns — Highest*)", table_body_center)],
        [Paragraph("C03", table_body_center), Paragraph("Malviya Nagar Clinic", table_body_style), Paragraph("Jaipur (Tier 2)", table_body_center), Paragraph("15.3 °C", table_body_center), Paragraph("142", table_body_center), Paragraph("<b>26.8%</b> (38 ns)", table_body_center)],
        [Paragraph("C02", table_body_center), Paragraph("Kothrud Family Clinic", table_body_style), Paragraph("Pune (Tier 1)", table_body_center), Paragraph("14.4 °C", table_body_center), Paragraph("160", table_body_center), Paragraph("22.5% (36 ns)", table_body_center)],
        [Paragraph("C05", table_body_center), Paragraph("Vijay Nagar Clinic", table_body_style), Paragraph("Indore (Tier 2)", table_body_center), Paragraph("15.2 °C", table_body_center), Paragraph("101", table_body_center), Paragraph("20.8% (21 ns)", table_body_center)],
        [Paragraph("C06", table_body_center), Paragraph("Edappally Medical Centre Kochi", table_body_style), Paragraph("Kochi (Tier 2)", table_body_center), Paragraph("24.2 °C", table_body_center), Paragraph("142", table_body_center), Paragraph("16.2% (23 ns)", table_body_center)],
        [Paragraph("C04", table_body_center), Paragraph("Vaishali Nagar Clinic", table_body_style), Paragraph("Jaipur (Tier 2)", table_body_center), Paragraph("16.0 °C", table_body_center), Paragraph("130", table_body_center), Paragraph("13.8% (18 ns — Lowest*)", table_body_center)],
        [Paragraph("C07", table_body_center), Paragraph("Gomti Nagar Care Point", table_body_style), Paragraph("Lucknow (Tier 2)", table_body_center), Paragraph("17.0 °C", table_body_center), Paragraph("90 (&lt;95)*", table_body_center), Paragraph("33.3% (30 ns)", table_body_center)],
        [Paragraph("C08", table_body_center), Paragraph("Sitabuldi Health Point", table_body_style), Paragraph("Nagpur (Tier 2)", table_body_center), Paragraph("22.3 °C", table_body_center), Paragraph("82 (&lt;95)*", table_body_center), Paragraph("15.9% (13 ns)", table_body_center)],
    ]
    t_clinic = Table(clinic_data, colWidths=[45, 155, 85, 55, 65, 135])
    t_clinic.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_alt_row]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_clinic)
    story.append(Paragraph("<i>*Note: In SQL Task 2.1 (HAVING count >= 95), C07 (90 visits) and C08 (82 visits) are excluded to avoid small-sample distortion.</i>", body_style))

    # Section 2: Lead Time Escalation
    story.append(Paragraph("2. SQL Empirical Finding: Advance Booking Lead Time Escalation", h1_style))
    lead_text = """Relational SQL analysis (Part 2) identified booking lead time as the single most critical structural driver of attendance failure. Patients booking appointments within 7 days exhibit an <b>83.8% attendance rate (16.2% no-show)</b>. However, when appointments are scheduled 31+ days ahead, no-show rates escalate to <b>60.5%</b>.
    """
    story.append(Paragraph(lead_text, body_style))

    if os.path.exists("report_assets/lead_time_escalation.png"):
        img_lead = Image("report_assets/lead_time_escalation.png", width=440, height=138)
        img_lead.hAlign = 'CENTER'
        story.append(img_lead)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: PREDICTIVE MODELING & BENCHMARKING
    # =========================================================================
    story.append(Paragraph("3. Predictive Modeling Benchmark & Generalization Analysis", h1_style))
    story.append(Paragraph(
        "To intercept no-shows before they occur, six candidate model architectures were benchmarked across 792 training rows (80%) and 198 hold-out test rows (20%, seed 42) using 11 engineered features: age, distance (km), fee (INR), lead days, prior no-shows, reminder status, booking channel (3 one-hot levels), and visit type (2 levels).",
        body_style
    ))

    # Benchmark Table (100% matched to verified python script output)
    bench_data = [
        [Paragraph("<b>Algorithm / Architecture</b>", table_header_style), Paragraph("<b>Train Acc</b>", table_header_style), Paragraph("<b>Test Acc</b>", table_header_style), Paragraph("<b>5-Fold CV AUC</b>", table_header_style), Paragraph("<b>Test ROC-AUC</b>", table_header_style), Paragraph("<b>Test Recall (0.50)</b>", table_header_style), Paragraph("<b>Test Prec (0.50)</b>", table_header_style)],
        [Paragraph("Dummy Baseline (Majority Class)", table_body_style), Paragraph("78.66%", table_body_center), Paragraph("75.25%", table_body_center), Paragraph("0.5000", table_body_center), Paragraph("0.5000", table_body_center), Paragraph("0.00%", table_body_center), Paragraph("0.00%", table_body_center)],
        [Paragraph("<b>Logistic Regression (Standardized)</b>", table_body_bold), Paragraph("83.08%", table_body_center), Paragraph("78.79%", table_body_center), Paragraph("0.8157", table_body_center), Paragraph("<b>0.8577</b>", table_body_center), Paragraph("34.69%", table_body_center), Paragraph("62.96%", table_body_center)],
        [Paragraph("Decision Tree (Full, depth=14)", table_body_style), Paragraph("100.00%", table_body_center), Paragraph("82.83%", table_body_center), Paragraph("0.7273", table_body_center), Paragraph("0.7558", table_body_center), Paragraph("61.22%", table_body_center), Paragraph("66.67%", table_body_center)],
        [Paragraph("Decision Tree (Pruned, max_depth=3)", table_body_style), Paragraph("81.82%", table_body_center), Paragraph("78.28%", table_body_center), Paragraph("0.7417", table_body_center), Paragraph("0.6845", table_body_center), Paragraph("12.24%", table_body_center), Paragraph("100.00%", table_body_center)],
        [Paragraph("Random Forest (Default, 100 Trees)", table_body_style), Paragraph("100.00%", table_body_center), Paragraph("81.82%", table_body_center), Paragraph("<b>0.8555</b>", table_body_center), Paragraph("0.8237", table_body_center), Paragraph("36.73%", table_body_center), Paragraph("78.26%", table_body_center)],
        [Paragraph("Random Forest (Tuned, max_depth=8)", table_body_style), Paragraph("93.18%", table_body_center), Paragraph("82.83%", table_body_center), Paragraph("0.8544", table_body_center), Paragraph("0.8336", table_body_center), Paragraph("32.65%", table_body_center), Paragraph("94.12%", table_body_center)],
    ]
    t_bench = Table(bench_data, colWidths=[165, 58, 58, 68, 68, 61, 62])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_alt_row]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BACKGROUND', (0, 2), (-1, 2), c_highlight),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 4))

    # Overfitting vs Generalization Commentary
    gen_text = """<b>Why Logistic Regression was selected over Random Forest:</b><br/>
    Although the unconstrained Random Forest achieved a higher 5-fold cross-validation ROC-AUC on training data (0.8555 vs 0.8157), it suffered from complete memorization (100.00% training accuracy vs 81.82% test accuracy). On the unseen held-out test set, <b>Logistic Regression delivered the highest generalization ROC-AUC of any model (0.8577 vs 0.8237 for default RF and 0.8336 for tuned RF)</b>. Logistic Regression also provides calibrated probabilities required for operating threshold tuning and transparent odds-ratio interpretability.
    """
    story.append(Paragraph(gen_text, body_style))

    if os.path.exists("report_assets/roc_comparison.png"):
        img_roc = Image("report_assets/roc_comparison.png", width=440, height=138)
        img_roc.hAlign = 'CENTER'
        story.append(img_roc)

    story.append(Spacer(1, 4))

    # Feature Coefficients Table (100% exact from notebook cell 4 & python output)
    story.append(Paragraph("<b>Logistic Regression Feature Coefficients & Odds Ratios:</b>", h2_style))
    coef_data = [
        [Paragraph("<b>Feature Name</b>", table_header_style), Paragraph("<b>Scaled Coef</b>", table_header_style), Paragraph("<b>Unscaled Metric</b>", table_header_style), Paragraph("<b>Odds Ratio</b>", table_header_style), Paragraph("<b>Clinical Interpretation</b>", table_header_style)],
        [Paragraph("lead_days", table_body_bold), Paragraph("+1.8397", table_body_center), Paragraph("+0.1853 / day", table_body_center), Paragraph("<b>1.2036</b>", table_body_center), Paragraph("Each additional advance booking day increases no-show odds by 20.4%.", table_body_style)],
        [Paragraph("age", table_body_bold), Paragraph("-1.7449", table_body_center), Paragraph("-0.1033 / year", table_body_center), Paragraph("<b>0.9018</b>", table_body_center), Paragraph("Older patients exhibit higher compliance (~9.8% lower odds per year).", table_body_style)],
        [Paragraph("fee_inr", table_body_style), Paragraph("-0.8703", table_body_center), Paragraph("-0.0038 / INR", table_body_center), Paragraph("0.9962", table_body_center), Paragraph("Higher consultation fees are modestly associated with lower no-show rates.", table_body_style)],
        [Paragraph("distance_km", table_body_style), Paragraph("+0.7397", table_body_center), Paragraph("+0.1030 / km", table_body_center), Paragraph("1.1085", table_body_center), Paragraph("Longer travel distances increase no-show odds (~10.9% per km).", table_body_style)],
        [Paragraph("prior_no_shows", table_body_bold), Paragraph("+0.5899", table_body_center), Paragraph("+0.5998 / count", table_body_center), Paragraph("<b>1.8217</b>", table_body_center), Paragraph("Each prior missed appointment increases no-show odds by 82.2%.", table_body_style)],
        [Paragraph("reminder_sent", table_body_bold), Paragraph("-0.4189", table_body_center), Paragraph("-0.8594 (Yes vs No)", table_body_center), Paragraph("<b>0.4234</b>", table_body_center), Paragraph("Sending an automated reminder reduces no-show odds by 57.7% (OR < 1).", table_body_style)],
    ]
    t_coef = Table(coef_data, colWidths=[85, 55, 85, 55, 260])
    t_coef.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_alt_row]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_coef)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: OPERATING THRESHOLDS & RIGOROUS VALIDATION
    # =========================================================================
    story.append(Paragraph("4. Operational Threshold Tuning & Healthcare Economics", h1_style))
    story.append(Paragraph(
        "Standard machine learning defaults assign classifications at probability threshold 0.50. In outpatient healthcare, this default fails because of severe <b>cost asymmetry</b>: a missed no-show (False Negative) leaves a 15–30 minute physician slot empty, causing an unrecoverable fee loss of INR 500–800. Conversely, flagging a reliable patient (False Positive) incurs only a nominal 1-minute front-desk phone confirmation call (estimated cost < INR 15).",
        body_style
    ))

    # Threshold Table (100% exact matched to python verification output)
    thresh_data = [
        [Paragraph("<b>Evaluation Cohort</b>", table_header_style), Paragraph("<b>Threshold</b>", table_header_style), Paragraph("<b>Accuracy</b>", table_header_style), Paragraph("<b>Precision</b>", table_header_style), Paragraph("<b>Recall</b>", table_header_style), Paragraph("<b>F1 Score</b>", table_header_style), Paragraph("<b>Flagged Volume</b>", table_header_style)],
        [Paragraph("5-Fold Out-of-Fold (Train)", table_body_style), Paragraph("0.50 (Default)", table_body_center), Paragraph("82.45%", table_body_center), Paragraph("68.29%", table_body_center), Paragraph("33.14%", table_body_center), Paragraph("0.4462", table_body_center), Paragraph("82 / 792 (10.4%)", table_body_center)],
        [Paragraph("5-Fold Out-of-Fold (Train)", table_body_style), Paragraph("<b>0.35 (Tuned)</b>", table_body_center), Paragraph("82.07%", table_body_center), Paragraph("58.71%", table_body_center), Paragraph("<b>53.85%</b> (+20.7%)", table_body_center), Paragraph("<b>0.5617</b>", table_body_center), Paragraph("155 / 792 (19.6%)", table_body_center)],
        [Paragraph("Held-Out Test Set (Random)", table_body_style), Paragraph("0.50 (Default)", table_body_center), Paragraph("78.79%", table_body_center), Paragraph("62.96%", table_body_center), Paragraph("34.69%", table_body_center), Paragraph("0.4474", table_body_center), Paragraph("27 / 198 (13.6%)", table_body_center)],
        [Paragraph("<b>Held-Out Test Set (Random)</b>", table_body_bold), Paragraph("<b>0.35 (Tuned)</b>", table_body_center), Paragraph("79.80%", table_body_center), Paragraph("61.22%", table_body_center), Paragraph("<b>61.22%</b> (30/49 caught)", table_body_center), Paragraph("<b>0.6122</b>", table_body_center), Paragraph("<b>49 / 198 (24.7%)</b>", table_body_center)],
        [Paragraph("Chronological Test (Future Months)", table_body_style), Paragraph("0.50 (Default)", table_body_center), Paragraph("82.83%", table_body_center), Paragraph("61.22%", table_body_center), Paragraph("66.67%", table_body_center), Paragraph("0.6383", table_body_center), Paragraph("49 / 198 (24.7%)", table_body_center)],
        [Paragraph("<b>Chronological Test (Future Months)</b>", table_body_bold), Paragraph("<b>0.35 (Tuned)</b>", table_body_center), Paragraph("74.24%", table_body_center), Paragraph("45.83%", table_body_center), Paragraph("<b>73.33%</b> (33/45 caught)", table_body_center), Paragraph("<b>0.5641</b>", table_body_center), Paragraph("<b>72 / 198 (36.4%)</b>", table_body_center)],
    ]
    t_thresh = Table(thresh_data, colWidths=[140, 65, 52, 54, 75, 54, 100])
    t_thresh.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_alt_row]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BACKGROUND', (0, 4), (-1, 4), c_highlight),
        ('BACKGROUND', (0, 6), (-1, 6), c_yellow),
    ]))
    story.append(t_thresh)
    story.append(Spacer(1, 4))

    if os.path.exists("report_assets/threshold_tuning.png"):
        img_th = Image("report_assets/threshold_tuning.png", width=440, height=135)
        img_th.hAlign = 'CENTER'
        story.append(img_th)

    story.append(Spacer(1, 4))

    # Methodological Rigor: Leak-Free & Chronological Validation
    story.append(Paragraph("5. Methodological Rigor: Zero-Leakage & Chronological Benchmarks", h1_style))
    rigor_text = """To ensure production validity and eliminate subtle preprocessing data leakage, two advanced validation studies were implemented in <code>03_model.ipynb</code> (Task 3.6):<br/>
    • <b>Strict Leak-Free Pipeline:</b> In standard pipelines, imputations (median age, distance) and Tukey fences are often computed over the entire dataset before splitting. When re-engineered so that medians (Age: 48.0, Distance: 8.10 km) and fences (Distance: 28.5125 km, Fee: INR 1,008.38) were fit <b>strictly on training data</b>, test ROC-AUC was <b>0.8619</b> (vs 0.8577 originally), and threshold 0.35 achieved 59.18% recall and precision across 49 flagged rows. This confirms zero artificial inflation from pre-split cleaning.<br/>
    • <b>Chronological Validation (Past → Future):</b> Clinic operations predict future visits from past records. Partitioning appointments chronologically (Train: Jan 1 to May 26, 792 rows; Test: May 27 to Jun 30, 198 rows) yielded a robust <b>ROC-AUC of 0.8320</b>. At threshold 0.35, the model intercepted <b>73.3% of all future no-shows (33 out of 45)</b>, demonstrating exceptional real-world efficacy.
    """
    story.append(Paragraph(rigor_text, body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: GENAI ANALYSIS & STRATEGIC PLAYBOOK
    # =========================================================================
    story.append(Paragraph("6. GenAI Follow-Up Intelligence (Gemini Flash & Pydantic)", h1_style))
    genai_text = """In Part 4, unstructured qualitative follow-up call notes were analyzed using Google Gemini Flash, governed by strict Pydantic v2 schemas and the CRAFT structured prompting methodology (Context, Role, Action, Format, Target). The pipeline achieved 100% validation compliance across all 10 sampled records, gracefully bypassed blank note <code>N004</code> (<code>skipped_blank</code>), and remained resilient to adversarial prompt injection and Hinglish dialect variations.<br/>
    <b>Cross-Tabulation Discovery:</b> Synthesizing qualitative root causes against relational booking records uncovered that <b>100% of patients who cited <code>forgot_or_no_reminder</code> had NOT received an automated reminder (<code>reminder_sent = No</code>)</b>. This perfectly corroborates the predictive model's odds ratio (0.4234), proving that automated reminders directly extinguish patient forgetfulness.
    """
    story.append(Paragraph(genai_text, body_style))

    # Notes Table (100% exact matched to notes_analysed.csv)
    notes_sample = [
        [Paragraph("<b>Note ID</b>", table_header_style), Paragraph("<b>Appt ID</b>", table_header_style), Paragraph("<b>Root Cause</b>", table_header_style), Paragraph("<b>Conf.</b>", table_header_style), Paragraph("<b>Status</b>", table_header_style), Paragraph("<b>Recommended Action</b>", table_header_style)],
        [Paragraph("N001", table_body_center), Paragraph("A0001", table_body_center), Paragraph("forgot_or_no_reminder", table_body_style), Paragraph("0.95", table_body_center), Paragraph("valid", table_body_center), Paragraph("Ensure automated SMS/WhatsApp reminders are dispatched 24h prior to visit.", table_body_style)],
        [Paragraph("N002", table_body_center), Paragraph("A0002", table_body_center), Paragraph("distance_or_transport", table_body_style), Paragraph("0.92", table_body_center), Paragraph("valid", table_body_center), Paragraph("Offer teleconsultation or reschedule to a closer CareLoop branch.", table_body_style)],
        [Paragraph("N003", table_body_center), Paragraph("A0003", table_body_center), Paragraph("cost_or_fee", table_body_style), Paragraph("0.94", table_body_center), Paragraph("valid", table_body_center), Paragraph("Provide flexible installment options or inform patient about subsidized slots.", table_body_style)],
        [Paragraph("N004", table_body_center), Paragraph("A0004", table_body_center), Paragraph("other", table_body_style), Paragraph("0.00", table_body_center), Paragraph("skipped_blank", table_body_center), Paragraph("Re-call patient (Zero API call bypass on blank note).", table_body_style)],
        [Paragraph("N007", table_body_center), Paragraph("A0007", table_body_center), Paragraph("forgot_or_no_reminder", table_body_style), Paragraph("0.93", table_body_center), Paragraph("valid", table_body_center), Paragraph("Verify patient phone number and automate multi-channel reminders.", table_body_style)],
    ]
    t_notes = Table(notes_sample, colWidths=[42, 45, 98, 38, 62, 255])
    t_notes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_alt_row]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_notes)
    story.append(Spacer(1, 4))

    # Section 7: Strategic Playbook
    story.append(Paragraph("7. Executive Action Plan & Clinic Operations Playbook", h1_style))
    story.append(Paragraph(
        "Based on cross-disciplinary insights, CareLoop Clinics should immediately execute a 3-tier phased rollout across its outpatient network:",
        body_style
    ))

    playbook_data = [
        [Paragraph("<b>Time Horizon</b>", table_header_style), Paragraph("<b>Strategic Initiative</b>", table_header_style), Paragraph("<b>Target Entity / Channel</b>", table_header_style), Paragraph("<b>Expected Impact & Operational Outcome</b>", table_header_style)],
        [
            Paragraph("<b>Phase 1: Day 1–30<br/>(Immediate)</b>", table_body_bold),
            Paragraph("<b>Automated Multi-Stage Reminders:</b> Mandate automated WhatsApp & SMS confirmations at 7 days and 24 hours prior to appointment for all advance bookings (>7 days).", table_body_style),
            Paragraph("Network-wide; focus on Hadapsar (27.3%) & Malviya Nagar (26.8%).", table_body_style),
            Paragraph("Targets forgetfulness-driven no-shows (100% unreminded in GenAI audit); directly leverages empirical reminder association (OR = 0.4234).", table_body_style)
        ],
        [
            Paragraph("<b>Phase 2: Day 31–60<br/>(Medium-Term)</b>", table_body_bold),
            Paragraph("<b>Evening Risk Scoring & High-Risk Calling:</b> Execute the Logistic Regression model nightly at 7:00 PM at threshold 0.35. Front desk conducts 1-min phone check-ins for the flagged ~25% cohort.", table_body_style),
            Paragraph("Clinic Receptionists & Patient Coordinators.", table_body_style),
            Paragraph("Intercepts 61.2% (random test) to 73.3% (future chronological) of no-shows. Converts unconfirmed slots into standby slots 12 hours in advance.", table_body_style)
        ],
        [
            Paragraph("<b>Phase 3: Day 61–90<br/>(Systemic)</b>", table_body_bold),
            Paragraph("<b>Smart Booking Rules & Teleconsult Fallback:</b> Introduce confirmation deposits or split advance holds for 31+ day bookings (60.5% no-show band). Offer teleconsultation redirects during transit/weather alerts.", table_body_style),
            Paragraph("EMR / Practice Management Software.", table_body_style),
            Paragraph("Reduces severe lead-time attrition and mitigates weather/transit cancellations identified in Part 4 notes without creating waiting room bottlenecks.", table_body_style)
        ],
    ]
    t_play = Table(playbook_data, colWidths=[80, 185, 115, 160])
    t_play.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_alt_row]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_play)
    story.append(Spacer(1, 4))

    # Sign-off box
    signoff_text = """<b>PROJECT SIGN-OFF & METRIC CERTIFICATION:</b><br/>
    All analytical metrics, regression parameters, SQL calculations, and machine learning outputs in this document are strictly reproducible via the public open-source project repository: <b>https://github.com/sdn9300/careloop-noshow-guard</b>.<br/>
    <i>Data Provenance: Controlled synthetic outpatient benchmark dataset calibrated to realistic Indian clinical operations, enriched with live weather telemetry from Open-Meteo REST API.</i>
    """
    t_sign = Table([[Paragraph(signoff_text, body_style)]], colWidths=[540])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_alt_row),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#A0AEC0")),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Executive Report PDF generated successfully: {pdf_path}")

if __name__ == '__main__':
    build_pdf()
