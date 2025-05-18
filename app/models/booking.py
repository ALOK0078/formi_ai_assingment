from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional
import re

class BookingRequest(BaseModel):
    # Core booking/customer fields
    city: str
    property_name: str
    customer_name: str
    phone_number: str = Field(..., pattern=r'^\d{10}$')
    booking_date: Optional[str] = "NA"   # YYYY-MM-DD or "NA"
    booking_time: Optional[str] = "NA"   # HH:MM or "NA"
    num_guests: Optional[int] = None

    # Post-call logging fields
    modality: str                        # "Call" or "Chatbot"
    call_time: str                       # e.g., "2025-01-03 12:44:55"
    call_outcome: str                    # "Enquiry", "Availability", "Post-Booking", "Misc"
    call_summary: Optional[str] = None   # Short summary of the call

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: str) -> str:
        if v == "NA":
            return v
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError("booking_date must be YYYY-MM-DD or 'NA'")
        return v

    @field_validator('booking_time')
    @classmethod
    def validate_booking_time(cls, v: str) -> str:
        if v == "NA":
            return v
        if not re.match(r'^\d{2}:\d{2}$', v):
            raise ValueError("booking_time must be HH:MM or 'NA'")
        return v

    @field_validator('modality')
    @classmethod
    def validate_modality(cls, v: str) -> str:
        if v not in ["Call", "Chatbot"]:
            raise ValueError("modality must be 'Call' or 'Chatbot'")
        return v

    @field_validator('call_outcome')
    @classmethod
    def validate_call_outcome(cls, v: str) -> str:
        allowed = ["Enquiry", "Availability", "Post-Booking", "Misc"]
        if v not in allowed:
            raise ValueError(f"call_outcome must be one of: {', '.join(allowed)}")
        return v
