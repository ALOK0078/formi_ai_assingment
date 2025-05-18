import logging
import gspread
import os
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SHEET_COLUMNS = [
    "Modality", "Call Time", "Phone Number", "Call Outcome",
    "Room Name", "Booking Date", "Booking Time",
    "Number of Guests", "Customer Name", "Call Summary"
]


def log_to_sheet(data: Dict, sheet_name: str = "ConversationLogs") -> None:
    """
    Logs conversation data to Google Sheets according to Postcall-configuration.pdf requirements

    Args:
        data: Dictionary containing conversation details
        sheet_name: Name of the target Google Sheet
    """
    credentials_path = os.path.abspath("credentials.json")
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        # Validate critical fields
        if not _validate_data(data):
            logging.error("Invalid data format, skipping logging")
            return

        # Authenticate
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Access spreadsheet
        spreadsheet = client.open(sheet_name)
        worksheet = _get_worksheet(spreadsheet)

        # Prepare and validate row data
        row = _prepare_row_data(data)
        if not row:
            return

        # Append data with retry mechanism
        _append_with_retry(worksheet, row)

    except Exception as e:
        logging.error(f"Critical logging error: {str(e)}")
        # Implement your alert system here


def _validate_data(data: Dict) -> bool:
    """Validate data against Postcall-configuration.pdf requirements"""
    required_fields = ['modality', 'call_time', 'phone_number', 'call_outcome']
    return all(field in data for field in required_fields)


def _get_worksheet(spreadsheet):
    """Get first worksheet and ensure headers exist"""
    worksheet = spreadsheet.sheet1
    if worksheet.row_values(1) != SHEET_COLUMNS:
        worksheet.clear()
        worksheet.append_row(SHEET_COLUMNS)
    return worksheet


def _prepare_row_data(data: Dict) -> list:
    """Convert data dict to properly ordered list with validation"""
    try:
        return [
            data.get("modality", "Chatbot"),
            data["call_time"],  # Mandatory field
            data["phone_number"],  # Mandatory field
            data["call_outcome"],  # Mandatory field
            data.get("room_name", "NA"),
            _normalize_field(data, "booking_date", "%Y-%m-%d"),
            _normalize_field(data, "booking_time", "%H:%M"),
            str(data.get("num_guests", "NA")),
            data.get("customer_name", ""),
            data.get("call_summary", "No summary")
        ]
    except KeyError as e:
        logging.error(f"Missing required field: {str(e)}")
        return []


def _normalize_field(data: Dict, field: str, fmt: str) -> str:
    """Normalize date/time fields to required format"""
    value = data.get(field, "NA")
    if value == "NA":
        return value

    try:
        datetime.strptime(value, fmt)
        return value
    except ValueError:
        logging.warning(f"Invalid {field} format: {value}")
        return "NA"


def _append_with_retry(worksheet, row: list, max_retries: int = 2) -> None:
    """Attempt append with retries for transient errors"""
    for attempt in range(max_retries + 1):
        try:
            worksheet.append_row(row)
            logging.info(f"Logged successfully: {row}")
            return
        except gspread.exceptions.APIError as e:
            if attempt == max_retries:
                raise
            logging.warning(f"Retry {attempt + 1}/{max_retries} for API error: {str(e)}")
