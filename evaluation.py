"""
Ablation study, baseline comparison, and figure generation.
Loads the unified CSVs produced by hybrid_model.py and runs:
  - leave-one-out ablation on the four base learners
  - baselines: predict-the-mean, linear, ridge, single HGB, single XGB
  - 6 figures saved to figures/
"""
import os, json, time, warnings
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import (HistGradientBoostingRegressor, RandomForestRegressor,
                              StackingRegressor, HistGradientBoostingClassifier)
from sklearn.metrics import (mean_absolute_error, r2_score, mean_squared_error,
                             accuracy_score, f1_score, roc_auc_score, brier_score_loss)
from sklearn.dummy import DummyRegressor
import lightgbm as lgb
import xgboost as xgb
warnings.filterwarnings('ignore')
np.random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, 'outputs')
FIG  = os.path.join(ROOT, 'figures')
os.makedirs(FIG, exist_ok=True)

print("Loading cached unified tables...")
real = pd.read_csv(os.path.join(OUT, 'unified_real_campaigns.csv'))
cre  = pd.read_csv(os.path.join(OUT, 'unified_creative_metadata.csv'))
res5 = json.load(open(os.path.join(OUT,'hybrid_results.json')))

# Re-derive features (mirror the training pipeline)
from sklearn.preprocessing import LabelEncoder
real['platform'] = real['platform'].fillna('Unknown').astype(str)
real['source']   = real['source'].astype(str)
le_p = LabelEncoder(); real['platform_enc'] = le_p.fit_transform(real['platform'])
le_s = LabelEncoder(); real['source_enc']   = le_s.fit_transform(real['source'])
real['log_impr']  = np.log1p(real['impressions'].fillna(0))
real['log_click'] = np.log1p(real['clicks'].fillna(0))
real['log_spent'] = np.log1p(real['spent'].fillna(0))
real['plat_src']  = real['platform_enc']*100 + real['source_enc']
real['impr_decile'] = real.groupby('source')['impressions'] \
   .transform(lambda x: pd.qcut(x,10,labels=False,duplicates='drop')).fillna(-1)

F_BASIC = ['platform_enc','source_enc','plat_src','log_impr','impr_decile']

# ===========================================================
# A) ABLATION STUDY  (drop one base learner at a time, on CTR + D1)
# ===========================================================
print("\n=== A) ABLATION STUDY ===")

base_estimators = {
    'hgb': HistGradientBoostingRegressor(max_iter=500, max_depth=8, learning_rate=0.05,
                                          l2_regularization=0.1, random_state=42),
    'lgb': lgb.LGBMRegressor(n_estimators=500, max_depth=8, num_leaves=63,
                              learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                              reg_alpha=0.05, reg_lambda=0.1, random_state=42, verbose=-1),
    'xgb': xgb.XGBRegressor(n_estimators=500, max_depth=7, learning_rate=0.05,
                             subsample=0.8, colsample_bytree=0.8, random_state=42, verbosity=0),
    'rf':  RandomForestRegressor(n_estimators=250, max_depth=15, min_samples_leaf=3,
                                  n_jobs=-1, random_state=42),
}

def fit_score(estimators, X, y):
    Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=42)
    if len(estimators) == 1:
        m = list(estimators.values())[0]
        m.fit(Xtr,ytr); yp = m.predict(Xte)
    else:
        m = StackingRegressor(estimators=list(estimators.items()),
                              final_estimator=Ridge(alpha=0.5), cv=5, n_jobs=-1)
        m.fit(Xtr,ytr); yp = m.predict(Xte)
    return r2_score(yte,yp), mean_absolute_error(yte,yp)

# CTR ablation
sub = real.dropna(subset=['ctr']).copy()
sub['ctr'] = sub['ctr'].clip(*sub['ctr'].quantile([0.005,0.995]).values)
X = sub[F_BASIC].fillna(-1).values; y = sub['ctr'].values

ablation = {'CTR':{}, 'D1':{}}
ablation['CTR']['full_stack_4'] = {'r2': float(fit_score(base_estimators, X, y)[0])}
print(f"  CTR full stack (4):       R2={ablation['CTR']['full_stack_4']['r2']:.4f}")
for drop in ['hgb','lgb','xgb','rf']:
    rem = {k:v for k,v in base_estimators.items() if k != drop}
    r2, mae = fit_score(rem, X, y)
    ablation['CTR'][f'drop_{drop}'] = {'r2':float(r2), 'delta':float(r2 - ablation['CTR']['full_stack_4']['r2'])}
    print(f"  CTR drop {drop:<3}:            R2={r2:.4f}  (delta={r2 - ablation['CTR']['full_stack_4']['r2']:+.4f})")

# Single-learner only
for name, est in base_estimators.items():
    r2, mae = fit_score({name:est}, X, y)
    ablation['CTR'][f'only_{name}'] = {'r2':float(r2)}
    print(f"  CTR only {name:<3}:            R2={r2:.4f}")

# D1 retention ablation (on creative metadata)
cat_cols = ['platform','brand','ad_format','creative_theme','cta_type',
            'audience_segment','language','source_dataset']
encs={}
for c in cat_cols:
    le = LabelEncoder(); cre[c+'_e'] = le.fit_transform(cre[c].fillna('NA').astype(str))
    encs[c]=le
cf = [c+'_e' for c in cat_cols] + ['has_offer','has_expert']
sub2 = cre.dropna(subset=['d1']).copy()
X2 = sub2[cf].values; y2 = sub2['d1'].values

ablation['D1']['full_stack_4'] = {'r2': float(fit_score(base_estimators, X2, y2)[0])}
print(f"  D1 full stack (4):        R2={ablation['D1']['full_stack_4']['r2']:.4f}")
for drop in ['hgb','lgb','xgb','rf']:
    rem = {k:v for k,v in base_estimators.items() if k != drop}
    r2, mae = fit_score(rem, X2, y2)
    ablation['D1'][f'drop_{drop}'] = {'r2':float(r2), 'delta':float(r2 - ablation['D1']['full_stack_4']['r2'])}
    print(f"  D1 drop {drop:<3}:             R2={r2:.4f}  (delta={r2 - ablation['D1']['full_stack_4']['r2']:+.4f})")

# Data ablation: drop manual / drop LLM
for drop_src, label in [('manual','no_manual_120'), (('07','08','09'),'no_LLM_1000')]:
    keep = cre.copy()
    if isinstance(drop_src, tuple):
        keep = keep[~keep['source_dataset'].isin(drop_src)]
    else:
        keep = keep[keep['source_dataset'] != drop_src]
    keep = keep.dropna(subset=['d1'])
    X3 = keep[cf].values; y3 = keep['d1'].values
    if len(X3) > 100:
        r2, _ = fit_score(base_estimators, X3, y3)
        ablation['D1'][label] = {'r2': float(r2),
                                  'delta': float(r2 - ablation['D1']['full_stack_4']['r2']),
                                  'n_rows': int(len(X3))}
        print(f"  D1 {label:<18}: R2={r2:.4f}  (delta={r2 - ablation['D1']['full_stack_4']['r2']:+.4f})")

with open(os.path.join(OUT,'ablation_results.json'),'w') as f:
    json.dump(ablation, f, indent=2)

# ===========================================================
# B) BASELINE COMPARISON (CTR + D1)
# ===========================================================
print("\n=== B) BASELINE COMPARISON ===")
baselines = {'CTR':{}, 'D1':{}}

def baseline(name, model, X, y):
    Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=42)
    model.fit(Xtr,ytr); yp = model.predict(Xte)
    return float(r2_score(yte,yp)), float(mean_absolute_error(yte,yp))

# CTR
for nm, mdl in [
    ('predict_mean',  DummyRegressor(strategy='mean')),
    ('linear_reg',    LinearRegression()),
    ('ridge',         Ridge(alpha=1.0)),
    ('single_xgb',    xgb.XGBRegressor(n_estimators=500, max_depth=7, learning_rate=0.05,
                                        random_state=42, verbosity=0)),
    ('single_hgb',    HistGradientBoostingRegressor(max_iter=500, max_depth=8,
                                                     learning_rate=0.05, random_state=42)),
]:
    r2, mae = baseline(nm, mdl, X, y)
    baselines['CTR'][nm] = {'r2':r2, 'mae':mae}
    print(f"  CTR {nm:<14}: R2={r2:.4f}  MAE={mae:.4f}")
baselines['CTR']['full_stack_4'] = {'r2': ablation['CTR']['full_stack_4']['r2']}
print(f"  CTR full_stack_4 :  R2={baselines['CTR']['full_stack_4']['r2']:.4f}")

# D1
for nm, mdl in [
    ('predict_mean',  DummyRegressor(strategy='mean')),
    ('linear_reg',    LinearRegression()),
    ('ridge',         Ridge(alpha=1.0)),
    ('single_xgb',    xgb.XGBRegressor(n_estimators=500, max_depth=7, learning_rate=0.05,
                                        random_state=42, verbosity=0)),
    ('single_hgb',    HistGradientBoostingRegressor(max_iter=500, max_depth=8,
                                                     learning_rate=0.05, random_state=42)),
]:
    r2, mae = baseline(nm, mdl, X2, y2)
    baselines['D1'][nm] = {'r2':r2, 'mae':mae}
    print(f"  D1  {nm:<14}: R2={r2:.4f}  MAE={mae:.4f}")
baselines['D1']['full_stack_4'] = {'r2': ablation['D1']['full_stack_4']['r2']}
print(f"  D1  full_stack_4 :  R2={baselines['D1']['full_stack_4']['r2']:.4f}")

with open(os.path.join(OUT,'baseline_results.json'),'w') as f:
    json.dump(baselines, f, indent=2)

# ===========================================================
# C) FIGURES
# ===========================================================
print("\n=== C) FIGURES ===")
plt.rcParams.update({'font.size':10, 'figure.dpi':140})

# --- Fig 1: R^2 with bootstrap 95% CI for all regression tasks ---
reg_tasks = ['CTR','CPC','CVR','ROI','CPM','CPA','Engagement_Score',
             'D1_Retention_Rate','D7_Retention_Rate','D30_Retention_Rate',
             'Install_Quality_Score','Cross_Platform_Lift']
labels, r2s, lo, hi = [], [], [], []
for t in reg_tasks:
    if t in res5:
        labels.append(t.replace('_',' '))
        r2s.append(res5[t]['R2'])
        lo.append(res5[t]['R2'] - res5[t]['R2_CI95'][0])
        hi.append(res5[t]['R2_CI95'][1] - res5[t]['R2'])
fig, ax = plt.subplots(figsize=(8.5,4.8))
y_pos = np.arange(len(labels))
bars = ax.barh(y_pos, r2s, xerr=[lo,hi], color='#2c7fb8', ecolor='#444', capsize=3, height=0.6)
ax.set_yticks(y_pos); ax.set_yticklabels(labels)
ax.set_xlabel('Test-set R² (with bootstrap 95% CI)')
ax.set_title('Figure 1. Per-task R² with bootstrap 95% confidence intervals')
ax.set_xlim(0,1)
ax.axvline(0.65, color='gray', linestyle='--', alpha=0.5, label='R²=0.65')
ax.legend(loc='lower right')
ax.invert_yaxis()
plt.tight_layout(); plt.savefig(os.path.join(FIG,'fig1_r2_with_CI.png'), dpi=150)
plt.close()
print(f"  Saved fig1_r2_with_CI.png")

# --- Fig 2: Permutation feature importance (CTR + D1) ---
fig, axes = plt.subplots(1, 2, figsize=(11,4))
for ax_i, key, title in [(axes[0],'CTR','Figure 2a. Feature importance (CTR)'),
                          (axes[1],'D1_Retention_Rate','Figure 2b. Feature importance (D1)')]:
    feats = res5[key].get('top_features', [])
    if feats:
        names = [f['feature'] for f in feats][::-1]
        vals  = [f['importance'] for f in feats][::-1]
        ax_i.barh(names, vals, color='#1d91c0')
        ax_i.set_xlabel('Permutation importance')
        ax_i.set_title(title)
plt.tight_layout(); plt.savefig(os.path.join(FIG,'fig2_feature_importance.png'), dpi=150)
plt.close()
print(f"  Saved fig2_feature_importance.png")

# --- Fig 3: Predicted vs actual scatter (CTR) ---
m_ctr_full = StackingRegressor(estimators=list(base_estimators.items()),
                                final_estimator=Ridge(alpha=0.5), cv=5, n_jobs=-1)
Xtr,Xte,ytr,yte = train_test_split(X, y, test_size=0.2, random_state=42)
m_ctr_full.fit(Xtr,ytr); yp = m_ctr_full.predict(Xte)
fig, ax = plt.subplots(figsize=(5.5,5))
ax.scatter(yte, yp, alpha=0.15, s=12, c='#2c7fb8')
mx = max(yte.max(), yp.max())
ax.plot([0,mx],[0,mx], 'r--', alpha=0.7, label='y=x perfect prediction')
ax.set_xlabel('Actual CTR'); ax.set_ylabel('Predicted CTR')
ax.set_title(f'Figure 3. Predicted vs actual CTR (test set, n={len(yte)})')
ax.legend()
ax.text(0.02, 0.95, f'R² = {r2_score(yte,yp):.3f}', transform=ax.transAxes,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))
plt.tight_layout(); plt.savefig(os.path.join(FIG,'fig3_pred_vs_actual_ctr.png'), dpi=150)
plt.close()
print(f"  Saved fig3_pred_vs_actual_ctr.png")

# --- Fig 4: Calibration curve for high-CTR classifier ---
sub_h = real.dropna(subset=['ctr']).copy()
thr = sub_h['ctr'].quantile(0.75)
sub_h['high_ctr'] = (sub_h['ctr']>=thr).astype(int)
Xh = sub_h[F_BASIC].fillna(-1).values; yh = sub_h['high_ctr'].values
Xtr,Xte,ytr,yte = train_test_split(Xh,yh,test_size=0.2,random_state=42,stratify=yh)
clf = HistGradientBoostingClassifier(max_iter=500,max_depth=7,learning_rate=0.05,random_state=42)
clf.fit(Xtr,ytr); ph = clf.predict_proba(Xte)[:,1]
# Bin and plot
bins = np.linspace(0,1,11)
mids = (bins[:-1]+bins[1:])/2
emp_pos = []
for i in range(10):
    m = (ph >= bins[i]) & (ph < bins[i+1])
    emp_pos.append(yte[m].mean() if m.sum() > 0 else np.nan)
fig, ax = plt.subplots(figsize=(5.5,5))
ax.plot([0,1],[0,1],'k--',alpha=0.5,label='Perfect calibration')
ax.plot(mids, emp_pos, marker='o', color='#2c7fb8', label='Model')
ax.set_xlabel('Predicted probability'); ax.set_ylabel('Empirical fraction positive')
ax.set_title('Figure 4. Reliability diagram for the high-CTR classifier')
ax.text(0.05,0.92,f"Brier = {brier_score_loss(yte,ph):.3f}\nAUC = {roc_auc_score(yte,ph):.3f}",
        transform=ax.transAxes, bbox=dict(boxstyle='round',facecolor='white',alpha=0.85))
ax.legend(); ax.grid(alpha=0.25)
plt.tight_layout(); plt.savefig(os.path.join(FIG,'fig4_calibration.png'), dpi=150)
plt.close()
print(f"  Saved fig4_calibration.png")

# --- Fig 5: Ablation impact (CTR + D1 side-by-side) ---
fig, axes = plt.subplots(1,2, figsize=(11,4))
for ax_i, key, title in [(axes[0],'CTR','Figure 5a. Ablation impact on CTR'),
                          (axes[1],'D1','Figure 5b. Ablation impact on D1 retention')]:
    a = ablation[key]
    full = a['full_stack_4']['r2']
    items = [('Full 4-model stack', full)]
    for k in ['drop_hgb','drop_lgb','drop_xgb','drop_rf']:
        items.append((k.replace('_',' '), a.get(k,{}).get('r2', np.nan)))
    for k in ['only_hgb','only_lgb','only_xgb','only_rf']:
        items.append((k.replace('_',' '), a.get(k,{}).get('r2', np.nan)))
    if 'no_manual_120' in a: items.append(('drop manual (D1 only)', a['no_manual_120']['r2']))
    if 'no_LLM_1000' in a:   items.append(('drop LLM (D1 only)', a['no_LLM_1000']['r2']))
    names, vals = zip(*items)
    colors = ['#1a9850']+['#fc8d59']*4+['#91bfdb']*4+['#999999']*max(0,len(items)-9)
    y_pos = np.arange(len(names))
    ax_i.barh(y_pos, vals, color=colors[:len(items)])
    ax_i.set_yticks(y_pos); ax_i.set_yticklabels(names, fontsize=8)
    ax_i.set_xlabel('R²'); ax_i.set_title(title)
    ax_i.invert_yaxis(); ax_i.set_xlim(0, max(vals)*1.1)
plt.tight_layout(); plt.savefig(os.path.join(FIG,'fig5_ablation.png'), dpi=150)
plt.close()
print(f"  Saved fig5_ablation.png")

# --- Fig 6: Baseline comparison bar chart ---
fig, axes = plt.subplots(1,2, figsize=(11,4))
for ax_i, key, title in [(axes[0],'CTR','Figure 6a. Baselines vs full stack (CTR)'),
                          (axes[1],'D1','Figure 6b. Baselines vs full stack (D1)')]:
    b = baselines[key]
    order = ['predict_mean','linear_reg','ridge','single_hgb','single_xgb','full_stack_4']
    names = [n for n in order if n in b]
    vals = [b[n]['r2'] for n in names]
    colors = ['#999','#fdae6b','#fd8d3c','#41b6c4','#2c7fb8','#1a9850']
    ax_i.bar(names, vals, color=colors[:len(names)])
    ax_i.set_ylabel('R²'); ax_i.set_title(title)
    ax_i.tick_params(axis='x', rotation=30, labelsize=9)
    ax_i.set_ylim(min(0,min(vals))-0.05, max(vals)*1.1)
    for i,v in enumerate(vals):
        ax_i.text(i, v+0.01, f'{v:.2f}', ha='center', fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG,'fig6_baselines.png'), dpi=150)
plt.close()
print(f"  Saved fig6_baselines.png")

print(f"\nAll artefacts in {OUT} and {FIG}")
