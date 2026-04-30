# Datasets

9 Kaggle CSV files we used to train the ad performance prediction model.
Total raw rows ~912k before sampling.

## Files

| File | Source | Rows |
|---|---|---|
| 01_kaggle_facebook_ads_REAL.csv | Kaggle Facebook Ad Campaigns | 1,143 |
| 02_social_media_advertising_300k_REAL.csv | Kaggle multi-platform ads | 300,000 |
| 03_ad_click_prediction_10k_REAL.csv | Kaggle user-level click logs | 10,000 |
| 04_social_media_ad_optimization_REAL.csv | Kaggle engagement scores | 500 |
| 05a-d | Kaggle relational ad-campaign DB (4 tables) | 400k events |
| 06_marketing_campaign_200k_REAL.csv | Kaggle marketing benchmark | 200,000 |
| 07_chatgpt_main_ads_500_AIGEN.csv | Generated via ChatGPT for creative metadata | 500 |
| 08_claude_edge_cases_200_AIGEN.csv | Generated via Claude for edge cases | 200 |
| 09_gemini_competitors_300_AIGEN.csv | Generated via Gemini for competitor metadata | 300 |

## Manually collected (separate file in parent folder)

`Advertisement_Dataset_Expanded.xlsx` - 120 ads we tagged by hand from the Meta Ad
Library and Google Ads Transparency Center over 20-28 April 2026. Covers 20 Indian
brands across baby-care, parenting, and edtech.

## Sampling

For training we sample sources 2 and 6 down to 10,000 rows each so they don't
dominate the smaller files. The relational DB (source 5) is aggregated by ad_id.
See `hybrid_model.py` for the exact harmonisation.
