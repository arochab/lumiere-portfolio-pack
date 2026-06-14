# generate_lumiere_data.py
# Option B dataset generator for the LUMIÈRE GROUP portfolio pack.
# Output: CSVs for Power BI (daily media+sales, monthly MMM+equity).
#
# Usage:
#   python generate_lumiere_data.py "C:\path\to\LUMIERE_PORTFOLIO\data"
#
# Notes:
# - Deterministic seed for reproducibility.
# - Dates: 2024-01-01 to 2025-12-31.

import sys, math, datetime as dt
import numpy as np
import pandas as pd

def main(out_dir: str):
    out = out_dir.rstrip("\\/")

    start_date = dt.date(2024,1,1)
    end_date   = dt.date(2025,12,31)
    dates = pd.date_range(start_date, end_date, freq="D")
    rng = np.random.default_rng(42)

    # -------- DIM_Date
    dim_date = pd.DataFrame({"full_date": dates.date})
    dim_date["date_key"] = pd.to_datetime(dim_date["full_date"]).dt.strftime("%Y%m%d").astype("int64")
    dim_date["year"] = pd.to_datetime(dim_date["full_date"]).dt.year.astype("int64")
    dim_date["quarter"] = "Q" + pd.to_datetime(dim_date["full_date"]).dt.quarter.astype(str)
    dim_date["month_number"] = pd.to_datetime(dim_date["full_date"]).dt.month.astype("int64")
    dim_date["month_name"] = pd.to_datetime(dim_date["full_date"]).dt.strftime("%B")
    dim_date["week_number"] = pd.to_datetime(dim_date["full_date"]).dt.isocalendar().week.astype("int64")
    dim_date["day_of_week"] = pd.to_datetime(dim_date["full_date"]).dt.strftime("%A")
    dim_date["is_weekend"] = (pd.to_datetime(dim_date["full_date"]).dt.weekday >= 5)
    m = pd.to_datetime(dim_date["full_date"]).dt.month
    d = pd.to_datetime(dim_date["full_date"]).dt.day
    dim_date["is_holiday_peak"] = ((m==11) & (d>=20)) | ((m==12) & (d>=15)) | ((m==1) & (d<=5))
    dim_date["fiscal_year"] = np.where(dim_date["month_number"]>=7, dim_date["year"]+1, dim_date["year"]).astype("int64")

    def fiscal_qtr(mon):
        if 7<=mon<=9: return "FQ1"
        if 10<=mon<=12: return "FQ2"
        if 1<=mon<=3: return "FQ3"
        return "FQ4"
    dim_date["fiscal_quarter"] = dim_date["month_number"].map(fiscal_qtr)
    dim_date["year_month"] = pd.to_datetime(dim_date["full_date"]).dt.strftime("%Y-%m")
    dim_date["month_start_date"] = pd.to_datetime(dim_date["full_date"]).values.astype("datetime64[M]").astype("datetime64[D]")
    dim_date["month_start_key"] = pd.to_datetime(dim_date["month_start_date"]).dt.strftime("%Y%m%d").astype("int64")

    # -------- DIMs
    dim_brand = pd.DataFrame([
        dict(brand_key=1, brand_code="LEC", brand_name="Lumière Éclat", brand_category="Skincare",  brand_tier="Prestige", launch_year=2012, brand_color_hex="#FFD700", is_active=True),
        dict(brand_key=2, brand_code="AUS", brand_name="Aurora Skin",   brand_category="Skincare",  brand_tier="Masstige", launch_year=2018, brand_color_hex="#FF6B8A", is_active=True),
        dict(brand_key=3, brand_code="NAB", brand_name="Noir Absolu",   brand_category="Fragrance", brand_tier="Prestige", launch_year=2008, brand_color_hex="#1A1A2E", is_active=True),
        dict(brand_key=4, brand_code="VBL", brand_name="Velvet Bloom",  brand_category="Fragrance", brand_tier="Masstige", launch_year=2015, brand_color_hex="#B8336A", is_active=True),
        dict(brand_key=5, brand_code="PRS", brand_name="Prisme Studio", brand_category="Make-up",   brand_tier="Prestige", launch_year=2011, brand_color_hex="#5C80BC", is_active=True),
        dict(brand_key=6, brand_code="CPL", brand_name="Color Pop Lab", brand_category="Make-up",   brand_tier="Mass",     launch_year=2020, brand_color_hex="#00C2FF", is_active=True),
        dict(brand_key=7, brand_code="SDR", brand_name="Soie Dorée",    brand_category="Hair Care", brand_tier="Prestige", launch_year=2006, brand_color_hex="#C7A27C", is_active=True),
        dict(brand_key=8, brand_code="BTN", brand_name="Botaniq",       brand_category="Hair Care", brand_tier="Mass",     launch_year=2019, brand_color_hex="#2E8B57", is_active=True),
    ])

    dim_channel = pd.DataFrame([
        dict(channel_key=1, channel_code="PAID_SOC", channel_name="Paid Social",    channel_group="Digital", funnel_stage="Upper/Mid", is_paid=True),
        dict(channel_key=2, channel_code="PAID_SEA", channel_name="Paid Search",    channel_group="Digital", funnel_stage="Lower",     is_paid=True),
        dict(channel_key=3, channel_code="PROG",     channel_name="Programmatic",   channel_group="Digital", funnel_stage="Mid",       is_paid=True),
        dict(channel_key=4, channel_code="TV",       channel_name="TV",             channel_group="Offline", funnel_stage="Upper",     is_paid=True),
        dict(channel_key=5, channel_code="INFL",     channel_name="Influencer",     channel_group="Digital", funnel_stage="Upper/Mid", is_paid=True),
        dict(channel_key=6, channel_code="RET_MED",  channel_name="Retail Media",   channel_group="Digital", funnel_stage="Lower",     is_paid=True),
    ])

    dim_market = pd.DataFrame([
        dict(market_key=1, market_code="FR", market_name="France",          currency_code="EUR", fx_to_eur=1.00, region="EU"),
        dict(market_key=2, market_code="UK", market_name="United Kingdom",  currency_code="GBP", fx_to_eur=1.17, region="EU"),
        dict(market_key=3, market_code="US", market_name="United States",   currency_code="USD", fx_to_eur=0.92, region="NA"),
        dict(market_key=4, market_code="DE", market_name="Germany",         currency_code="EUR", fx_to_eur=1.00, region="EU"),
    ])

    # -------- Campaigns (quarterly)
    def quarter_start_end(year, q):
        if q==1: return dt.date(year,1,1), dt.date(year,3,31)
        if q==2: return dt.date(year,4,1), dt.date(year,6,30)
        if q==3: return dt.date(year,7,1), dt.date(year,9,30)
        return dt.date(year,10,1), dt.date(year,12,31)

    def year_q(date):
        y = date.year
        q = (date.month-1)//3 + 1
        return y, q

    objectives = {"Upper":["Awareness","Brand Lift"], "Mid":["Consideration","Traffic"], "Lower":["Conversion","Sales"], "Upper/Mid":["Awareness","Consideration"]}
    def funnel_group(stage):
        if stage=="Upper": return "Upper"
        if stage=="Mid": return "Mid"
        if stage=="Lower": return "Lower"
        return "Upper/Mid"

    creative_themes = ["Cinematic Launch","Glow Routine","Night Ritual","Bold Color","Fresh Botanics","Silk Repair","Signature Scent","Studio Pro"]

    campaign_rows=[]
    campaign_key=1
    camp_lookup={}
    for year in [2024,2025]:
        for q in [1,2,3,4]:
            q_start, q_end = quarter_start_end(year,q)
            for _, b in dim_brand.iterrows():
                for _, c in dim_channel.iterrows():
                    for _, mk in dim_market.iterrows():
                        obj = rng.choice(objectives[funnel_group(c["funnel_stage"])])
                        theme = rng.choice(creative_themes)
                        tier_mult = 1.25 if b["brand_tier"]=="Prestige" else (1.05 if b["brand_tier"]=="Masstige" else 0.85)
                        market_mult = 1.15 if mk["market_code"]=="US" else (1.05 if mk["market_code"]=="UK" else 1.0)
                        channel_base = {"TV":240000,"PROG":90000,"PAID_SOC":80000,"PAID_SEA":65000,"INFL":50000,"RET_MED":70000}[c["channel_code"]]
                        budget_plan = channel_base * tier_mult * market_mult * (0.85 + 0.30*rng.random())
                        campaign_code = f"{b['brand_code']}_{mk['market_code']}_{c['channel_code']}_{year}Q{q}"
                        campaign_rows.append({
                            "campaign_key": campaign_key,
                            "campaign_code": campaign_code,
                            "campaign_name": f"{b['brand_name']} — {mk['market_code']} — {c['channel_name']} — {year} Q{q}",
                            "brand_key": int(b["brand_key"]),
                            "channel_key": int(c["channel_key"]),
                            "market_key": int(mk["market_key"]),
                            "start_date": q_start.isoformat(),
                            "end_date": q_end.isoformat(),
                            "objective": obj,
                            "creative_theme": theme,
                            "budget_plan_eur": round(float(budget_plan),2),
                        })
                        camp_lookup[(int(b["brand_key"]), int(c["channel_key"]), int(mk["market_key"]), year, q)] = campaign_key
                        campaign_key += 1
    dim_campaign = pd.DataFrame(campaign_rows)

    # -------- Facts (Option B)
    seasonality = {1:0.90,2:0.92,3:0.98,4:1.02,5:1.08,6:1.00,7:0.95,8:0.97,9:1.05,10:1.10,11:1.30,12:1.45}
    chan_params = {
        "PAID_SOC": dict(cpm=6.5, ctr=0.012, cvr=0.018),
        "PAID_SEA": dict(cpc=0.85, ctr=None,  cvr=0.030),
        "PROG":     dict(cpm=4.2, ctr=0.006, cvr=0.012),
        "TV":       dict(cpm=14.0,ctr=0.0002,cvr=0.0012),
        "INFL":     dict(cpm=18.0,ctr=0.004, cvr=0.010),
        "RET_MED":  dict(cpc=0.65, ctr=None,  cvr=0.040),
    }

    brand_base={}
    for _, b in dim_brand.iterrows():
        tier_mult = 1.20 if b["brand_tier"]=="Prestige" else (1.00 if b["brand_tier"]=="Masstige" else 0.80)
        cat_mult = {"Skincare":1.05,"Fragrance":1.00,"Make-up":0.95,"Hair Care":0.90}[b["brand_category"]]
        for _, c in dim_channel.iterrows():
            ch_mult = {"TV":1.90,"PROG":0.90,"PAID_SOC":0.95,"PAID_SEA":0.85,"INFL":0.70,"RET_MED":0.80}[c["channel_code"]]
            for _, mk in dim_market.iterrows():
                m_mult = 1.35 if mk["market_code"]=="US" else (1.10 if mk["market_code"]=="UK" else 1.0)
                brand_base[(int(b["brand_key"]), c["channel_code"], int(mk["market_key"]))] = 650.0 * tier_mult * cat_mult * ch_mult * m_mult

    media_rows=[]
    for date in dates:
        ds = seasonality[date.month]
        weekend = date.weekday()>=5
        weekend_mult_digital = 1.05 if weekend else 1.0
        weekend_mult_tv = 0.80 if weekend else 1.0
        y,q = year_q(date.date())
        for _, b in dim_brand.iterrows():
            for _, c in dim_channel.iterrows():
                for _, mk in dim_market.iterrows():
                    base = brand_base[(int(b["brand_key"]), c["channel_code"], int(mk["market_key"]))]
                    vol = 0.08 if c["channel_code"]=="TV" else 0.14
                    spend = max(0, base * ds * (weekend_mult_tv if c["channel_code"]=="TV" else weekend_mult_digital) * (1 + float(rng.normal(0, vol))))
                    camp_key = camp_lookup[(int(b["brand_key"]), int(c["channel_key"]), int(mk["market_key"]), y, q)]
                    p = chan_params[c["channel_code"]]
                    if "cpm" in p and p["ctr"] is not None:
                        cpm = p["cpm"]*(0.85+0.30*rng.random())
                        impressions = int(round((spend/cpm)*1000)) if cpm>0 else 0
                        ctr = p["ctr"]*(0.80+0.40*rng.random())
                        clicks = int(round(impressions*ctr))
                        cvr = p["cvr"]*(0.80+0.40*rng.random())
                        conversions = int(round(clicks*cvr))
                        cpc = (spend/clicks) if clicks>0 else None
                    else:
                        cpc_base = p["cpc"]*(0.85+0.30*rng.random())
                        clicks = int(round(spend/cpc_base)) if cpc_base>0 else 0
                        ctr = (0.04 if c["channel_code"]=="PAID_SEA" else 0.025)*(0.80+0.40*rng.random())
                        impressions = int(round(clicks/ctr)) if ctr>0 else 0
                        cvr = p["cvr"]*(0.80+0.40*rng.random())
                        conversions = int(round(clicks*cvr))
                        cpm = (spend/impressions)*1000 if impressions>0 else None
                        cpc = cpc_base if clicks>0 else None

                    media_rows.append({
                        "date_key": int(date.strftime("%Y%m%d")),
                        "full_date": date.date().isoformat(),
                        "brand_key": int(b["brand_key"]),
                        "channel_key": int(c["channel_key"]),
                        "market_key": int(mk["market_key"]),
                        "campaign_key": int(camp_key),
                        "spend_eur": round(float(spend),2),
                        "impressions": impressions,
                        "clicks": clicks,
                        "conversions": conversions,
                        "cpm_eur": round(float(cpm),4) if cpm is not None else None,
                        "cpc_eur": round(float(cpc),4) if cpc is not None else None,
                        "ctr": round(float(clicks/impressions),6) if impressions>0 else None,
                        "cvr": round(float(conversions/clicks),6) if clicks>0 else None,
                    })
    fact_media_spend = pd.DataFrame(media_rows)

    spend_daily = (fact_media_spend.groupby(["date_key","brand_key","market_key"], as_index=False)["spend_eur"].sum()
                   .rename(columns={"spend_eur":"total_spend_eur"}))

    sales_rows=[]
    for date in dates:
        dk = int(date.strftime("%Y%m%d"))
        ds = seasonality[date.month]
        t = (date - dates[0]).days / (len(dates)-1)
        trend = 1.00 + 0.08*t
        for _, b in dim_brand.iterrows():
            tier = b["brand_tier"]
            avg_price = 78 if tier=="Prestige" else (42 if tier=="Masstige" else 24)
            margin_rate = 0.58 if tier=="Prestige" else (0.50 if tier=="Masstige" else 0.42)
            brand_base_rev = 14000 if tier=="Prestige" else (10000 if tier=="Masstige" else 7000)
            for _, mk in dim_market.iterrows():
                market_mult = 1.35 if mk["market_code"]=="US" else (1.10 if mk["market_code"]=="UK" else 1.0)
                spend_val = float(spend_daily.loc[(spend_daily["date_key"]==dk) & (spend_daily["brand_key"]==b["brand_key"]) & (spend_daily["market_key"]==mk["market_key"]), "total_spend_eur"].values[0])
                mkt_effect = 1 + 0.18 * math.log1p(spend_val/1000.0)
                promo = 1.0
                if date.month in (5,11) and date.day in (10,11,12,20,21,22):
                    promo = 1.10
                if date.month==12 and date.day in (18,19,20):
                    promo = 1.07
                revenue = max(0, brand_base_rev*market_mult*ds*trend*promo*mkt_effect*(1+float(rng.normal(0,0.06))))
                disc_base = 0.08 if tier=="Prestige" else (0.12 if tier=="Masstige" else 0.18)
                discount_rate = min(0.45, max(0.0, disc_base + (0.05 if promo>1 else 0.0) + float(rng.normal(0,0.015))))
                net_revenue = revenue*(1-discount_rate)
                units = int(round(net_revenue/avg_price))
                margin = net_revenue*margin_rate
                sales_rows.append({
                    "date_key": dk,
                    "full_date": date.date().isoformat(),
                    "brand_key": int(b["brand_key"]),
                    "market_key": int(mk["market_key"]),
                    "units": units,
                    "revenue_eur": round(float(net_revenue),2),
                    "margin_eur": round(float(margin),2),
                    "avg_price_eur": round(float(avg_price),2),
                    "discount_rate": round(float(discount_rate),4),
                })
    fact_sales = pd.DataFrame(sales_rows)

    months = pd.date_range("2024-01-01","2025-12-01", freq="MS")

    # KPI Targets
    target_rows=[]
    for mdate in months:
        mk_date_key = int(mdate.strftime("%Y%m%d"))
        month_mult = seasonality[mdate.month]
        for _, b in dim_brand.iterrows():
            tier_mult = 1.15 if b["brand_tier"]=="Prestige" else (1.02 if b["brand_tier"]=="Masstige" else 0.90)
            for _, mk in dim_market.iterrows():
                market_mult = 1.30 if mk["market_code"]=="US" else (1.08 if mk["market_code"]=="UK" else 1.0)
                base_target = 420000*tier_mult*market_mult*month_mult*(0.90+0.20*rng.random())
                target_roas = (2.8 if b["brand_tier"]=="Prestige" else (2.4 if b["brand_tier"]=="Masstige" else 2.1))*(0.92+0.16*rng.random())
                target_aw = (62 if b["brand_tier"]=="Prestige" else (54 if b["brand_tier"]=="Masstige" else 47)) + (mk["market_code"]=="US")*4 + float(rng.normal(0,2.2))
                target_sov = 0.08 + 0.03*rng.random()
                target_nps = (32 if b["brand_tier"]=="Prestige" else (22 if b["brand_tier"]=="Masstige" else 14)) + float(rng.normal(0,3))
                target_rows.append({
                    "date_key": mk_date_key,
                    "brand_key": int(b["brand_key"]),
                    "market_key": int(mk["market_key"]),
                    "target_revenue_eur": round(float(base_target),2),
                    "target_blended_roas": round(float(target_roas),3),
                    "target_awareness_index": round(float(target_aw),2),
                    "target_share_of_voice": round(float(target_sov),4),
                    "target_nps": round(float(target_nps),1),
                })
    dim_kpi_target = pd.DataFrame(target_rows)

    # MMM Output monthly
    fact_media_spend["month_start_key"] = pd.to_datetime(fact_media_spend["full_date"]).values.astype("datetime64[M]").astype("datetime64[D]")
    fact_media_spend["month_start_key"] = pd.to_datetime(fact_media_spend["month_start_key"]).dt.strftime("%Y%m%d").astype("int64")
    fact_sales["month_start_key"] = pd.to_datetime(fact_sales["full_date"]).values.astype("datetime64[M]").astype("datetime64[D]")
    fact_sales["month_start_key"] = pd.to_datetime(fact_sales["month_start_key"]).dt.strftime("%Y%m%d").astype("int64")

    monthly_spend_bcm = (fact_media_spend.groupby(["month_start_key","brand_key","channel_key","market_key"], as_index=False)["spend_eur"].sum()
                         .rename(columns={"month_start_key":"date_key","spend_eur":"monthly_spend_eur"}))
    monthly_rev_bm = (fact_sales.groupby(["month_start_key","brand_key","market_key"], as_index=False)["revenue_eur"].sum()
                      .rename(columns={"month_start_key":"date_key","revenue_eur":"monthly_revenue_eur"}))
    monthly_spend_bm = (fact_media_spend.groupby(["month_start_key","brand_key","market_key"], as_index=False)["spend_eur"].sum()
                        .rename(columns={"month_start_key":"date_key","spend_eur":"monthly_spend_eur_total"}))

    tmp = monthly_rev_bm.merge(monthly_spend_bm, on=["date_key","brand_key","market_key"], how="left")
    tmp["incr_factor"] = (0.08 + 0.08*np.log1p(tmp["monthly_spend_eur_total"]/120000.0)).clip(0.05,0.22)
    tmp["monthly_incremental_revenue_eur_total"] = (tmp["monthly_revenue_eur"]*tmp["incr_factor"]).round(2)

    channel_weight = {1:1.00,2:1.15,3:0.95,4:0.85,5:0.90,6:1.10}
    ms = monthly_spend_bcm.copy()
    ms["weighted_spend"] = ms["monthly_spend_eur"] * ms["channel_key"].map(channel_weight)
    den = ms.groupby(["date_key","brand_key","market_key"], as_index=False)["weighted_spend"].sum().rename(columns={"weighted_spend":"den_weighted_spend"})
    ms = ms.merge(den, on=["date_key","brand_key","market_key"], how="left")
    ms["spend_share_weighted"] = np.where(ms["den_weighted_spend"]>0, ms["weighted_spend"]/ms["den_weighted_spend"], 0)

    tmp2 = tmp[["date_key","brand_key","market_key","monthly_incremental_revenue_eur_total","monthly_revenue_eur"]]
    ms = ms.merge(tmp2, on=["date_key","brand_key","market_key"], how="left")

    ms["mmm_incremental_revenue_eur"] = (ms["monthly_incremental_revenue_eur_total"]*ms["spend_share_weighted"]).round(2)
    ms["mmm_roas"] = np.where(ms["monthly_spend_eur"]>0, ms["mmm_incremental_revenue_eur"]/ms["monthly_spend_eur"], np.nan)
    ms["optimal_spend_eur"] = (ms["monthly_spend_eur"] * (1.05 + 0.20*rng.random(len(ms)))).round(2)
    ms["saturation_index"] = np.where(ms["optimal_spend_eur"]>0, ms["monthly_spend_eur"]/ms["optimal_spend_eur"], np.nan)
    ms["marginal_roas"] = (ms["mmm_roas"] * (1.15 - 0.55*ms["saturation_index"].fillna(0))).clip(lower=0.05).round(3)
    ms["mmm_contribution_pct"] = np.where(ms["monthly_revenue_eur"]>0, ms["mmm_incremental_revenue_eur"]/ms["monthly_revenue_eur"], np.nan)

    fact_mmm_output = ms[[
        "date_key","brand_key","channel_key","market_key",
        "mmm_contribution_pct","mmm_incremental_revenue_eur","mmm_roas",
        "saturation_index","optimal_spend_eur","marginal_roas",
        "monthly_spend_eur","monthly_revenue_eur"
    ]].rename(columns={"monthly_spend_eur":"spend_eur","monthly_revenue_eur":"revenue_eur"})

    # Brand Equity monthly
    upper_channels=set([1,4,5])
    sp_upper = fact_mmm_output[fact_mmm_output["channel_key"].isin(list(upper_channels))].groupby(["date_key","brand_key","market_key"], as_index=False)["spend_eur"].sum().rename(columns={"spend_eur":"upper_spend_eur"})
    sp_total = fact_mmm_output.groupby(["date_key","market_key"], as_index=False)["spend_eur"].sum().rename(columns={"spend_eur":"market_total_spend_eur"})
    sp_bm = fact_mmm_output.groupby(["date_key","brand_key","market_key"], as_index=False)["spend_eur"].sum().rename(columns={"spend_eur":"brand_total_spend_eur"})

    memory={(bk,mk):0.0 for bk in dim_brand["brand_key"] for mk in dim_market["market_key"]}
    be_rows=[]
    for mdate in months:
        dk = int(mdate.strftime("%Y%m%d"))
        for _, b in dim_brand.iterrows():
            base_aw = 64 if b["brand_tier"]=="Prestige" else (55 if b["brand_tier"]=="Masstige" else 48)
            base_cons = base_aw - (7 if b["brand_tier"]=="Prestige" else 9)
            base_sent = 56 if b["brand_tier"]=="Prestige" else (52 if b["brand_tier"]=="Masstige" else 49)
            for _, mk in dim_market.iterrows():
                key=(int(b["brand_key"]), int(mk["market_key"]))
                up_sp = float(sp_upper.loc[(sp_upper["date_key"]==dk) & (sp_upper["brand_key"]==key[0]) & (sp_upper["market_key"]==key[1]), "upper_spend_eur"].values[0])
                memory[key] = 0.72*memory[key] + 0.28*(up_sp/250000.0)
                lift = 10*math.tanh(memory[key])
                market_bump = 2.5 if mk["market_code"]=="US" else (1.0 if mk["market_code"]=="UK" else 0.0)
                aw = base_aw + market_bump + lift + float(rng.normal(0,1.8))
                cons = base_cons + 0.60*lift + float(rng.normal(0,1.6))
                sent = base_sent + 0.35*lift + float(rng.normal(0,1.5))
                brand_sp = float(sp_bm.loc[(sp_bm["date_key"]==dk) & (sp_bm["brand_key"]==key[0]) & (sp_bm["market_key"]==key[1]), "brand_total_spend_eur"].values[0])
                mkt_tot = float(sp_total.loc[(sp_total["date_key"]==dk) & (sp_total["market_key"]==key[1]), "market_total_spend_eur"].values[0])
                sov = brand_sp/mkt_tot if mkt_tot>0 else 0
                nps = (28 if b["brand_tier"]=="Prestige" else (18 if b["brand_tier"]=="Masstige" else 12)) + 0.25*lift + float(rng.normal(0,2.8))
                be_rows.append({
                    "date_key": dk,
                    "brand_key": key[0],
                    "market_key": key[1],
                    "awareness_index": round(float(np.clip(aw,0,100)),2),
                    "consideration_index": round(float(np.clip(cons,0,100)),2),
                    "sentiment_index": round(float(np.clip(sent,0,100)),2),
                    "share_of_voice": round(float(np.clip(sov,0,1)),4),
                    "nps": round(float(np.clip(nps,-20,80)),1),
                })
    fact_brand_equity = pd.DataFrame(be_rows)

    # -------- Write CSVs
    dim_date.to_csv(f"{out}/dim_date.csv", index=False)
    dim_brand.to_csv(f"{out}/dim_brand.csv", index=False)
    dim_market.to_csv(f"{out}/dim_market.csv", index=False)
    dim_channel.to_csv(f"{out}/dim_channel.csv", index=False)
    dim_campaign.to_csv(f"{out}/dim_campaign.csv", index=False)
    dim_kpi_target.to_csv(f"{out}/dim_kpi_target.csv", index=False)

    fact_media_spend.to_csv(f"{out}/fact_media_spend_daily.csv", index=False)
    fact_sales.to_csv(f"{out}/fact_sales_daily.csv", index=False)
    fact_mmm_output.to_csv(f"{out}/fact_mmm_output_monthly.csv", index=False)
    fact_brand_equity.to_csv(f"{out}/fact_brand_equity_monthly.csv", index=False)

    print("✅ Done. Wrote CSVs to:", out)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_lumiere_data.py <output_folder>")
        sys.exit(1)
    main(sys.argv[1])
