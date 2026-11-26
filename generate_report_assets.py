import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_curve, auc, confusion_matrix, precision_recall_curve

os.makedirs("report_assets", exist_ok=True)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica', 'Arial', 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

df = pd.read_csv("appointments_clean.csv")

# 1. Lead Time Risk Chart
plt.figure(figsize=(7, 4), dpi=300)
lead_bands = ['1-7 Days', '8-14 Days', '15-30 Days', '31+ Days']
rates = [16.2, 17.4, 30.0, 60.5]
appts = [390, 304, 253, 43]
colors = ['#2b5c8f', '#3b75af', '#d97724', '#c0392b']

bars = plt.bar(lead_bands, rates, color=colors, width=0.55, edgecolor='none', zorder=3)
plt.title("No-Show Rate Escalation by Advance Booking Lead Time", fontsize=12, fontweight='bold', pad=15, color='#1a252f')
plt.ylabel("No-Show Rate (%)", fontsize=10, fontweight='bold', color='#2c3e50')
plt.xlabel("Booking Lead Time Band", fontsize=10, fontweight='bold', color='#2c3e50')
plt.ylim(0, 75)
plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

for bar, rate, count in zip(bars, rates, appts):
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1.8, f"{rate}%\n({count} visits)", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1a252f')

plt.axhline(22.0, color='#7f8c8d', linestyle=':', linewidth=1.5, label='Overall Average (22.0%)', zorder=2)
plt.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
plt.tight_layout()
plt.savefig("report_assets/lead_time_escalation.png")
plt.close()

# 2. ROC Curves Comparison
X_raw = df[['age', 'distance_km', 'fee_inr', 'lead_days', 'prior_no_shows', 'reminder_sent', 'booking_channel', 'visit_type']].copy()
X_raw['reminder_sent'] = X_raw['reminder_sent'].map({'Yes': 1, 'No': 0})
X = pd.get_dummies(X_raw, columns=['booking_channel', 'visit_type'], drop_first=False, dtype=int)
y = df['no_show'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_train)
X_te_s = scaler.transform(X_test)

lr = LogisticRegression(max_iter=1000, random_state=42).fit(X_tr_s, y_train)
rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train, y_train)
dt = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X_train, y_train)

fpr_lr, tpr_lr, _ = roc_curve(y_test, lr.predict_proba(X_te_s)[:, 1])
fpr_rf, tpr_rf, _ = roc_curve(y_test, rf.predict_proba(X_test)[:, 1])
fpr_dt, tpr_dt, _ = roc_curve(y_test, dt.predict_proba(X_test)[:, 1])

plt.figure(figsize=(7, 4.5), dpi=300)
plt.plot(fpr_lr, tpr_lr, label=f'Logistic Regression (AUC = {auc(fpr_lr, tpr_lr):.3f})', color='#1f77b4', linewidth=2.5)
plt.plot(fpr_rf, tpr_rf, label=f'Random Forest 100 Trees (AUC = {auc(fpr_rf, tpr_rf):.3f})', color='#2ca02c', linewidth=2, linestyle='--')
plt.plot(fpr_dt, tpr_dt, label=f'Decision Tree Depth=3 (AUC = {auc(fpr_dt, tpr_dt):.3f})', color='#ff7f0e', linewidth=1.8, linestyle='-.')
plt.plot([0, 1], [0, 1], color='#7f8c8d', linestyle=':', label='Random Chance (AUC = 0.500)')
plt.title("Held-Out Test Set ROC Curve Comparison", fontsize=12, fontweight='bold', pad=15, color='#1a252f')
plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=10, fontweight='bold', color='#2c3e50')
plt.ylabel("True Positive Rate (Recall / Sensitivity)", fontsize=10, fontweight='bold', color='#2c3e50')
plt.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
plt.tight_layout()
plt.savefig("report_assets/roc_comparison.png")
plt.close()

# 3. Decision Threshold Sensitivity Chart
thresholds = np.linspace(0.1, 0.9, 81)
precisions, recalls, f1s = [], [], []
y_probs = lr.predict_proba(X_te_s)[:, 1]

for th in thresholds:
    p = (y_probs >= th).astype(int)
    rec = np.sum((p == 1) & (y_test == 1)) / np.sum(y_test == 1)
    prec = np.sum((p == 1) & (y_test == 1)) / max(np.sum(p == 1), 1)
    f1 = 2 * (prec * rec) / max((prec + rec), 1e-9)
    precisions.append(prec)
    recalls.append(rec)
    f1s.append(f1)

plt.figure(figsize=(7, 4), dpi=300)
plt.plot(thresholds, recalls, label='Recall (Sensitivity)', color='#d9534f', linewidth=2.2)
plt.plot(thresholds, precisions, label='Precision (PPV)', color='#0275d8', linewidth=2.2)
plt.plot(thresholds, f1s, label='F1 Score', color='#5cb85c', linewidth=2, linestyle='--')
plt.axvline(0.35, color='#2c3e50', linestyle='-', linewidth=1.5, label='Selected Operational Threshold (0.35)')
plt.axvline(0.50, color='#95a5a6', linestyle=':', linewidth=1.2, label='Default Threshold (0.50)')

plt.title("Operating Threshold Tuning: Precision vs. Recall Trade-Off", fontsize=12, fontweight='bold', pad=15, color='#1a252f')
plt.xlabel("Probability Decision Threshold", fontsize=10, fontweight='bold', color='#2c3e50')
plt.ylabel("Score Metric", fontsize=10, fontweight='bold', color='#2c3e50')
plt.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
plt.tight_layout()
plt.savefig("report_assets/threshold_tuning.png")
plt.close()

print("Report assets generated successfully.")
