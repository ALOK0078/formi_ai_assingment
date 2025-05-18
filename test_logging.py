# test_logging.py
from app.google_sheet import log_to_sheet

test_data = {
    "modality": "Chatbot",
    "call_time": "2025-05-20 14:30:00",
    "phone_number": "9876543210",
    "call_outcome": "Enquiry",
    "room_name": "BBQ Nation Indiranagar",
    "booking_date": "NA",
    "booking_time": "NA",
    "num_guests": "NA",
    "customer_name": "Alok",
    "call_summary": "Test enquiry about booking."
}

log_to_sheet(test_data)
