# Data Dictionary (short)

## Keys
- date_key: YYYYMMDD (int)
- month_start_key: YYYYMM01 (int) derived in dim_date

## Grain
- fact_media_spend_daily: day × brand × channel × market × campaign
- fact_sales_daily: day × brand × market
- fact_mmm_output_monthly: month_start × brand × channel × market
- fact_brand_equity_monthly: month_start × brand × market
- dim_kpi_target: month_start × brand × market

## Notes
- All monetary fields are stored in EUR for simplicity (portfolio use).
- Markets include currency metadata (currency_code, fx_to_eur) if you want to extend.
