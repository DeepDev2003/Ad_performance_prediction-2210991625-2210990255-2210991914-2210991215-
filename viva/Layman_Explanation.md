# Layman Explanation — How to Explain the Project to a Non-Technical Examiner

If a panellist is from a non-ML background, use these. Each block has a 30-second
version (the elevator pitch) and a follow-up if they want detail.

---

## What does the project do?

**30-second**: We built a machine-learning system that predicts how a digital advertisement
will perform — its click rate, its cost, how many users will install the app, and whether
those users will stick around — *before* the ad is launched. Think of it as a forecast tool
for marketing teams who are about to spend money on Meta or Google ads.

**Detail**: Today, marketing teams launch ads, watch the dashboard for 2–3 days, and kill
anything that's underperforming. That wastes budget. Our model takes the ad's attributes
(theme, format, audience, language, platform) and predicts 15 different performance metrics
upfront, with a confidence interval on each one. If the predicted metrics are weak, the
team can rework the creative *before* spending.

---

## What data did you train on?

**30-second**: About nine hundred thousand ad records combined from six public Kaggle
datasets, plus one hundred and twenty competitor ads we observed manually on the Meta Ad
Library and Google Ads Transparency Center.

**Detail**: The Kaggle datasets cover real Facebook campaigns, multi-platform social media
campaigns, click-prediction logs, an ad-campaign relational database with 400,000 events,
and a marketing-campaign benchmark with 200,000 rows. The Indian competitor data is what
makes this project different — no Kaggle dataset has theme-level metadata for brands like
Mamaearth, FirstCry, Pampers, BabyChakra, or Healofy.

---

## What is "machine learning" doing in this project, in simple terms?

**30-second**: We give the computer thousands of past advertisements along with their
performance, and let it learn the patterns. Once it has seen enough examples, it can
predict the performance of a new ad it has never seen.

**Detail**: We use *gradient-boosted trees* — a method that builds a series of simple
yes/no decision rules (like "if the platform is Pinterest then CPM is around $190") and
combines them. We then stack four different versions of this method together so they can
correct each other's mistakes. The combination gives a more accurate and more stable
prediction than any single method.

---

## What are the 15 things you predict?

**30-second**: Standard ad metrics (click rate, cost per click, conversion rate, cost per
mille, cost per acquisition, return on investment), three quality classifiers (will this
ad land in the top quarter for clicks, engagement, or conversion?), and five user-quality
metrics (day-1 retention, day-7 retention, day-30 retention, install quality score, and a
cross-platform travel-lift score).

**Detail**: The first seven are about *acquisition* — how cheaply the ad pulls users in.
The classifiers help marketers spot likely winners early. The five user-quality metrics
are about *retention* — once those users install the app, how many stick around for a
day, a week, a month? A high-retention ad is worth more to the business than a high-click
ad that brings users who immediately leave.

---

## How accurate is the model?

**30-second**: On the well-defined targets, our R² scores sit between 0.65 and 0.81,
which is strong for ad performance prediction. The high-CTR classifier reaches 99% AUC,
meaning it almost never confuses winning ads with losing ones.

**Detail**: R² measures how much of the variance in the metric the model explains —
0.81 on cost-per-click means the model captures 81% of the variation. We also report
5-fold cross-validation scores and 95% bootstrap confidence intervals, so the headline
numbers are not single-split flukes.

---

## What were the biggest challenges?

**30-second**: Three. First, every Kaggle source defines impression and click slightly
differently. Second, public datasets don't include post-install retention, so we had to
synthesise it using a published heuristic. Third, the return-on-investment column in one
of the datasets is essentially random, so our ROI model is weak — and we report that
honestly instead of hiding it.

---

## What would a marketing team do with this?

**30-second**: Score five candidate ads before the campaign launches, pick the two with
the best predicted CTR and D1 retention, and launch only those. The model also warns
when a creative is likely to fatigue early, which lets the team rotate creative on
schedule instead of reactively.

---

## Why is this project different from "just downloading a Kaggle dataset and running sklearn"?

**30-second**: Three reasons. We merged nine separate datasets, not one. We added 120
manually-tagged competitor ads — original data that doesn't exist on Kaggle. And we
predict 15 different metrics jointly, not just one — covering both the cheap-clicks side
and the user-quality side that most public ad papers ignore.

---

## Common follow-up questions and short answers

| Question | Answer |
|---|---|
| "Is this real-time?" | The model itself runs in milliseconds. Productionising it requires monitoring infrastructure that we did not build. |
| "Could it work for non-Indian brands?" | The campaign-level models yes, the creative-metadata models would need re-tagging because our manual file is India-focused. |
| "What's the carbon footprint?" | Training takes 4 minutes on a laptop CPU — a fraction of one kilowatt-hour. |
| "Did you use ChatGPT to write the code?" | We used LLMs to generate auxiliary creative data (clearly labelled in the dataset inventory) but the modelling code, leakage audit, and statistical reporting are our own work. |
| "Why didn't you use a neural network?" | Tabular datasets of this size favour gradient boosting, which also gives feature importance — important for marketers who need explanations. |
