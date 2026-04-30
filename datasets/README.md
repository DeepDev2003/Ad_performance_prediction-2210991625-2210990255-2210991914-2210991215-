# DATASETS INVENTORY — Ad Performance Prediction Project

This folder contains all data collected for the ML model training pipeline.
A total of **9 datasets** spanning **~912,000+ raw rows** across real campaign data, real user interaction data, and AI-augmented creative metadata.

---

## REAL DATASETS (collected from Kaggle)

### 01_kaggle_facebook_ads_REAL.csv
- **Source:** Kaggle — Facebook Ad Campaign dataset
- **Rows:** 1,143
- **Type:** Real Facebook campaign data
- **Key columns:** ad_id, campaign_id, age, gender, interest1/2/3, impressions, clicks, spent, total_conversion, approved_conversion
- **Use for:** Training CTR, CPC, conversion rate prediction models

### 02_social_media_advertising_300k_REAL.csv
- **Source:** Kaggle — Social Media Advertising dataset
- **Rows:** 300,000
- **Type:** Real multi-platform campaign data
- **Key columns:** Campaign_ID, Target_Audience, Campaign_Goal, Channel_Used (Facebook/Instagram/Twitter/Pinterest), Conversion_Rate, ROI, Acquisition_Cost, Clicks, Impressions, Engagement_Score, Customer_Segment, Company
- **Note:** Sample down to ~3,000-5,000 rows for training to keep balanced with other sources
- **Use for:** Multi-platform performance prediction, ROI modeling

### 03_ad_click_prediction_10k_REAL.csv
- **Source:** Kaggle — Ad Click Prediction dataset
- **Rows:** 10,000
- **Type:** Real user-level click prediction data
- **Key columns:** age, gender, device_type, ad_position, browsing_history, time_of_day, click (0/1)
- **Use for:** CTR classifier, user demographic effects

### 04_social_media_ad_optimization_REAL.csv
- **Source:** Kaggle — Social Media Ad Optimization dataset
- **Rows:** 500
- **Type:** Real ad-level performance with engagement scores
- **Key columns:** user_id, age, gender, location, ad_category, ad_platform, ad_type, impressions, clicks, conversion, time_spent_on_ad, engagement_score
- **Use for:** Engagement modeling, conversion prediction

### 05a-d_campaign_db_*.csv (4 files — RELATIONAL DATABASE)
- **Source:** Kaggle — Full Ad Campaign Database
- **Files:**
  - `05a_campaign_db_campaigns.csv` — 50 campaigns (campaign_id, name, dates, budget)
  - `05b_campaign_db_ads.csv` — 200 ads (ad_id, platform, type, targeting)
  - `05c_campaign_db_events_400k.csv` — **400,000 events** (impressions, clicks, conversions, likes, shares per ad per user)
  - `05d_campaign_db_users.csv` — User profiles (age, gender, country, interests)
- **Type:** Real relational ad campaign data
- **Use for:** Aggregate events into per-ad metrics — this is the closest to actual SDK output we have

### 06_marketing_campaign_200k_REAL.csv
- **Source:** Kaggle — Marketing Campaign Dataset
- **Rows:** 200,000
- **Type:** Real campaign performance with ROI
- **Key columns:** Company, Campaign_Type (Influencer/Search/Display/Email/Social), Channel_Used (Google Ads/YouTube/Facebook/Instagram/Email/Website), Conversion_Rate, ROI, Clicks, Impressions, Engagement_Score
- **Note:** Sample down to ~3,000-5,000 rows for training
- **Use for:** Cross-channel performance prediction, ROI modeling

---

## AI-GENERATED DATASETS (synthetic, mirrors industry patterns)

### 07_chatgpt_main_ads_500_AIGEN.csv
- **Source:** ChatGPT (GPT-4) using detailed prompt
- **Rows:** 500
- **Type:** AI-generated parenting/maternal health app ads
- **Key columns:** 33 columns including platform (Meta/Google/YouTube), brand (Mylo + competitors), ad_format, creative_theme, audience_segment, language, full performance metrics including D0/D1/D7 retention, IQS
- **Use for:** Training the SDK retention metrics models (D0, D1, IQS)

### 08_claude_edge_cases_200_AIGEN.csv
- **Source:** Claude AI using edge case prompt
- **Rows:** 200
- **Type:** AI-generated edge cases and anomalies
- **Includes:** Creative fatigue patterns, fraud signals, viral accidents, platform mismatches, audience mismatches, budget extremes, seasonal spikes, language mismatches, winning unicorns, retargeting gold
- **Use for:** Improving model robustness on anomalies

### 09_gemini_competitors_300_AIGEN.csv
- **Source:** Gemini AI using competitor-focused prompt
- **Rows:** 300
- **Type:** AI-generated competitor brand ads
- **Brands covered:** FirstCry, MamEarth_Baby, Pampers_India, Huggies_India, PharmEasy_Baby, Healofy, BabyChakra, Pregakem, HealthKart_Women, Himalaya_BabyCare
- **Use for:** Competitor pattern learning

---

## SUMMARY TABLE

| # | File | Rows | Source | Type |
|---|------|------|--------|------|
| 1 | 01_kaggle_facebook_ads_REAL.csv | 1,143 | Kaggle | Real |
| 2 | 02_social_media_advertising_300k_REAL.csv | 300,000 | Kaggle | Real |
| 3 | 03_ad_click_prediction_10k_REAL.csv | 10,000 | Kaggle | Real |
| 4 | 04_social_media_ad_optimization_REAL.csv | 500 | Kaggle | Real |
| 5 | 05c_campaign_db_events_400k.csv | 400,000 | Kaggle | Real (events) |
| 6 | 06_marketing_campaign_200k_REAL.csv | 200,000 | Kaggle | Real |
| 7 | 07_chatgpt_main_ads_500_AIGEN.csv | 500 | ChatGPT | AI-gen |
| 8 | 08_claude_edge_cases_200_AIGEN.csv | 200 | Claude | AI-gen |
| 9 | 09_gemini_competitors_300_AIGEN.csv | 300 | Gemini | AI-gen |
| | **TOTAL RAW** | **~912,000+** | | |

---

## STILL TO COLLECT (your task — Tier 2)

### Meta Ad Library — Manual Tagging
- Visit: https://facebook.com/ads/library
- Search brands: MamEarth, BabyChakra, Healofy, FirstCry, Pampers India
- For each ad seen, record in a Google Sheet with these columns:
  - brand, ad_format (video/image/carousel), creative_theme (testimonial/discount/expert/lifestyle), cta_text, language, has_offer (Y/N), has_expert (Y/N)
- Target: 20-30 ads minimum
- Why: Real competitor creative metadata that no Kaggle dataset has

### Google Ads Transparency Center
- Visit: https://adstransparency.google.com
- Same brands, same tagging method
- Why: Adds Google ad creative data to balance against Meta data

---

## NEXT STEPS (when data is collected)

1. Upload the manually-tagged Meta Ad Library + Google Ads Transparency data
2. Merge all 9 datasets + the new manual data into one unified training set
3. Retrain the hybrid model (real data for CTR/CPC/conversions, synthetic for D0/D1/IQS)
4. Update research paper Section 4 (Results) with new accuracy numbers
5. Update viva QA document with new numbers

---

## MODEL DELIVERABLES (already created — check shared outputs)

- `Ad_Performance_Prediction_Research_Paper.docx` — Full research paper (8 sections)
- `Ad_Prediction_Presentation_Sheet.xlsx` — Team contributions, layman reasons, results summary
- `hybrid_model_v2.py` — Trained ML pipeline (7 prediction models)
- `Viva_Preparation_QA.docx` — Viva preparation Q&A
