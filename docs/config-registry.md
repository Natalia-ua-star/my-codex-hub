# Toast POS — Config Registry

## Spreadsheets & Dashboards

| key | spreadsheet_id | apps_script_constant | description |
|-----|---------------|---------------------|-------------|
| Toast Master Data | `1qyf8Up1Zlz36k5xGH7AbSCep3Xvaw7JWXbkHtwkCE0I` | `MASTER_SS_ID` / `DASHBOARD_MASTER_SS_ID` | Central master database — raw Toast data, lookups, assignments, facts, config, weather, events, logs |
| BREAD & DOUGH FORECASTING | `1Eu_O5uSxFV9xW8VAePQTjsDHoUhROV3Wb_jGF2Qt6g0` | `BDF_SS_ID` | Weekly bread/dough production forecasting |
| Forecast_Archive | `1L3CGuue04gVP27uaYzxS-Xm0lwp0T0fW2mKe6NXuz3g` | — | Archived BD_MMDD_MMDD weekly forecast sheets |
| DAILY SALES DASHBOARD | `1kDNakI3hrWYz2UCILBIuX4AOX3kVWtnGYUx4jRor1Tk` | `DASHBOARD_SS_ID` | Executive KPI dashboard: forecast vs actual, weather, events |
| SALES - FORECAST | `1_hZvCM6R-Jizfk2ddx1KuekuBjtUZeRk2XYSYnZvHzw` | `[FILL IN]` | Weekly sales forecasting workbook |

## Apps Script Web Apps

| key | url | description | notes |
|-----|-----|-------------|-------|
| Toast_WebApp | `https://script.google.com/macros/s/AKfycbzig5ngyLVpmWN1gXe0Gdb-nDRyJQg2I.../exec` | Receives data from Make, runs `runToastDailyAfterMake()` | After any code change — must redeploy: Deploy → New version |
| Bread_WebApp | `https://script.google.com/macros/s/AKfycbzmP65FQgKHAq-xvXZFY5AT8A62XovFYl7vVIEtINwbdEWkUwHclobrptZ6zmuWq_7QBw/exec` | Runs `runBreadDailyReportsAfterToast()` | Separate Apps Script project |

## Make.com

| key | id | url | description |
|-----|----|-----|-------------|
| Make_Scenario | 5065003 | `https://us2.make.com/993647/scenarios/5065003/edit` | Toast — Pull Daily Orders (main data import scenario) |
| Make_DataStore | — | — | Toast API credentials |
| Make_Team | 993647 | — | Make organization/team |

## Google Drive

| key | folder_id | url | description | notes |
|-----|-----------|-----|-------------|-------|
| Drive_Folder | `1OOtP-dGV2e_NWFaMG97qMslh5UqWFssm` | `https://drive.google.com/drive/folders/1OOtP-dGV2e_NWFaMG97qMslh5UqWFssm` | Project files folder | File IDs do not change when moved — only verify access permissions |
