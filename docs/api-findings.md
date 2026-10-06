# EirGrid dashboard API: findings (tested 6 Oct 2026)

Endpoint: `https://www.smartgriddashboard.com/DashboardService.svc/data`
This is the service behind the public dashboard. It is not an official, documented API and can change without warning.

## Series

| Area | Field name | Interval | Data confirmed |
|---|---|---|---|
| windactual | WIND_ACTUAL | 15 min | Feb 2021 onwards (spot checks) |
| windforecast | WIND_FCAST | 15 min | Feb 2021 onwards (spot checks) |
| demandactual | SYSTEM_DEMAND | 15 min | Feb 2021 onwards (spot checks) |
| generationactual | GEN_EXP | 15 min | Feb 2021 onwards (spot checks) |
| SnspALL | SNSP_ALL | 30 min | First full day seen: 1 Mar 2021 |
| interconnection | INTER_EWIC, INTER_GRNLK, INTER_MOYLE, INTER_NET | 15 min | Empty on 13 Feb 2023 and 13 Feb 2024. Values from 13 Aug 2024 (Greenlink from 13 Feb 2025) |

"Confirmed" means one day per year or month was checked, not every day.

## Behaviour observed

- Timestamps are Irish local time. 31 Mar 2024 returned 92 wind and 46 SNSP readings (one hour missing).
- 27 Oct 2024 returned 96 wind readings, all timestamps unique. The repeated hour appears once, even in a narrow query. The second pass is not retrievable this way.
- The server sometimes returns status 503 with an HTML page instead of JSON. Retrying later worked. 26 Oct 2024 failed once and succeeded earlier.
- SNSP had 47 readings (one missing) on 1 Apr, 1 May and 1 Jun 2021.

## Open questions

- SNSP on 18 and 21 Feb 2021 stayed at 503 after four retries.
- The exact start date of interconnection data.
- How many other days have missing readings (to be measured in the cleaning stage).