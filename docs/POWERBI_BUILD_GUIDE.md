# Power BI Build Guide (60–90 min)

## 0) Put the pack on Google Drive (recommended)
1. Create a dedicated Drive folder: `LUMIERE_PORTFOLIO/`
2. Install **Google Drive for Desktop** (Windows).
3. Mark that folder as **Available offline**.
4. Note the local path, e.g. `G:\My Drive\LUMIERE_PORTFOLIO\data`

> Power BI works best with a local path (Drive sync) vs direct web URLs.

## 1) Import data (Power BI Desktop)
- Home → Get data → Text/CSV
- Import all CSVs in `/data`
- Load as tables (don’t auto-detect relationships yet)

## 2) Create relationships (Model view)
**Active 1:* relationships**
- dim_date[date_key] → fact_media_spend_daily[date_key]
- dim_date[date_key] → fact_sales_daily[date_key]
- dim_date[month_start_key] → fact_mmm_output_monthly[date_key]   (use month_start_key from dim_date)
- dim_date[month_start_key] → fact_brand_equity_monthly[date_key]
- dim_date[month_start_key] → dim_kpi_target[date_key]

- dim_brand[brand_key] → (facts)[brand_key]
- dim_market[market_key] → (facts)[market_key]
- dim_channel[channel_key] → fact_media_spend_daily[channel_key]
- dim_channel[channel_key] → fact_mmm_output_monthly[channel_key]
- dim_campaign[campaign_key] → fact_media_spend_daily[campaign_key]

**Filter direction**: Single (DIM → FACT).

## 3) Mark date table
- Table tools → Mark as date table → `dim_date[full_date]`

## 4) Create measures
- Create an empty table `_Measures`
- Paste DAX from `/dax/measures_dax.txt` into new measures (or copy/paste per folder).

## 5) Apply theme
- View → Themes → Browse for themes → select `/theme/lumiere_dark_glass.json`

## 6) Pages (recommended 6 pages)
1. Executive Overview (cards + trends + RAG)
2. Revenue & Profitability (daily + YoY)
3. Media Performance (spend, CPM/CPC, funnel, ROAS)
4. MMM Insights (incremental revenue, saturation, optimal spend)
5. Brand Equity (awareness/consideration/sentiment, SoV, NPS)
6. Drill-through: Brand Detail (single brand deep dive)

## 7) Export screenshots
- File → Export → PDF (optional)
- Or take clean screenshots (16:9) into `exports/screenshots/`
