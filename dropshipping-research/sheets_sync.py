"""Appends new winner rows into live Google Sheets (not a local .xlsx).

Uses a Google service account (Sheets API v4) so rows get APPENDED every run
instead of overwriting the whole file — this is what makes "every day adds
new products" possible. A regular OAuth "Drive connector" can only create or
replace whole files, not append rows, so this needs its own credential.

Setup (one-time, done by the account owner — see README "Google Sheets sync"):
1. Google Cloud Console -> new/existing project -> Enable "Google Sheets API".
2. IAM & Admin -> Service Accounts -> Create service account -> Keys -> Create
   key (JSON) -> download it, save as e.g. service_account.json.
3. Create two Google Sheets (or let this script create them, see
   `ensure_spreadsheet`) and Share each with the service account's email
   (looks like xxx@yyy.iam.gserviceaccount.com) as Editor.
4. Put the JSON path and both spreadsheet IDs in .env:
   GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
   MAIN_SPREADSHEET_ID=...
   ALIEXPRESS_SPREADSHEET_ID=...
"""

import logging

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_service():
    if not config.GOOGLE_SERVICE_ACCOUNT_FILE:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_FILE is not set in .env — see sheets_sync.py "
            "module docstring for one-time setup steps."
        )
    creds = Credentials.from_service_account_file(config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def ensure_spreadsheet(service, spreadsheet_id: str, title: str) -> str:
    """Returns spreadsheet_id if it's usable, otherwise creates a new spreadsheet
    with that title and returns its new ID (print it — save it back into .env)."""
    if spreadsheet_id:
        try:
            service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            return spreadsheet_id
        except HttpError:
            logger.warning("Configured spreadsheet_id %s is not accessible; creating a new one.", spreadsheet_id)

    body = {"properties": {"title": title}}
    created = service.spreadsheets().create(body=body, fields="spreadsheetId").execute()
    new_id = created["spreadsheetId"]
    logger.warning(
        "Created new spreadsheet %r (id=%s). Save this ID into your .env so future "
        "runs append to the same sheet instead of creating a new one each time.",
        title, new_id,
    )
    return new_id


def _ensure_sheet_tab(service, spreadsheet_id: str, sheet_name: str, header: list):
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing_titles = [s["properties"]["title"] for s in meta.get("sheets", [])]

    if sheet_name not in existing_titles:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]},
        ).execute()
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [header]},
        ).execute()


def append_dataframe(service, spreadsheet_id: str, sheet_name: str, df: pd.DataFrame):
    """Appends df as new rows at the bottom of sheet_name (creating the tab
    with a header row on first use). Existing rows are never touched."""
    if df.empty:
        logger.info("Skipping Sheets append for %r — no rows.", sheet_name)
        return

    df = df.astype(object).where(pd.notnull(df), "")
    header = list(df.columns)
    _ensure_sheet_tab(service, spreadsheet_id, sheet_name, header)

    rows = df.values.tolist()
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()
    logger.info("Appended %d rows to %r in spreadsheet %s.", len(rows), sheet_name, spreadsheet_id)


def sync_all(main_sheets: dict, aliexpress_df: pd.DataFrame):
    """main_sheets: {"TikTok_Winners": df, "Instagram_Winners": df, ...}
    (Shopify_Competitors and Summary included). AliExpress goes to its own
    spreadsheet, per spec ("окрема таблиця по алі експрес")."""
    service = _get_service()

    main_id = ensure_spreadsheet(service, config.MAIN_SPREADSHEET_ID, "Dropshipping Research — Winners")
    for sheet_name, df in main_sheets.items():
        append_dataframe(service, main_id, sheet_name, df)

    aliexpress_id = ensure_spreadsheet(service, config.ALIEXPRESS_SPREADSHEET_ID, "Dropshipping Research — AliExpress")
    append_dataframe(service, aliexpress_id, "AliExpress_Winners", aliexpress_df)

    return main_id, aliexpress_id
