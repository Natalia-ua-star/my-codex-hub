# Toast POS — Config Registry

| key | spreadsheet_id | apps_script_constant | webapp_url | system | description | notes |
|-----|---------------|---------------------|-----------|--------|-------------|-------|
| Toast Master Data | `1qyf8Up1Zlz36k5xGH7AbSCep3Xvaw7JWXbkHtwkCE0I` | `MASTER_SS_ID` / `DASHBOARD_MASTER_SS_ID` | — | Google Sheets | Central master database | Primary data warehouse |
| BREAD & DOUGH FORECASTING | `1Eu_O5uSxFV9xW8VAePQTjsDHoUhROV3Wb_jGF2Qt6g0` | `BDF_SS_ID` | — | Google Sheets | Weekly bread/dough production forecasting | |
| Forecast_Archive | `1L3CGuue04gVP27uaYzxS-Xm0lwp0T0fW2mKe6NXuz3g` | — | — | Google Sheets | Archived BD_MMDD_MMDD reports | |
| DAILY SALES DASHBOARD | `1kDNakI3hrWYz2UCILBIuX4AOX3kVWtnGYUx4jRor1Tk` | `DASHBOARD_SS_ID` | — | Google Sheets | Executive KPI dashboard | |
| SALES - FORECAST | `1_hZvCM6R-Jizfk2ddx1KuekuBjtUZeRk2XYSYnZvHzw` | `[FILL IN]` | — | Google Sheets | Weekly sales forecasting workbook | |
| Toast_WebApp | — | — | `https://script.google.com/macros/s/AKfycbzig5ngyLVpmWN1gXe0Gdb-nDRyJQg2I.../exec` | Apps Script | Receives data from Make, runs `runToastDailyAfterMake()` | After any code change — redeploy: Deploy → New version |
| Bread_WebApp | — | — | `https://script.google.com/macros/s/AKfycbzmP65FQgKHAq-xvXZFY5AT8A62XovFYl7vVIEtINwbdEWkUwHclobrptZ6zmuWq_7QBw/exec` | Apps Script | Runs `runBreadDailyReportsAfterToast()` | Separate Apps Script project |
| Make_Scenario | `993647` | — | `https://us2.make.com/993647/scenarios/5065003/edit` | Make.com | Toast — Pull Daily Orders (main data import scenario) | |
| Make_DataStore | `97428` | — | `https://us2.make.com/993647/data-stores/browse/97428` | Make.com | Toast API credentials | |
| Drive_Folder | `1OOtP-dGV2e_NWFaMG97qMslh5UqWFssm` | — | `https://drive.google.com/drive/folders/1OOtP-dGV2e_NWFaMG97qMslh5UqWFssm` | Google Drive | Project files folder | File IDs do not change when moved to Shared Drive — verify access permissions |
