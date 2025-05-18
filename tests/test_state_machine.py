import pytest
from app.state_machine import ConversationManager, State

def test_initial_state():
    cm = ConversationManager()
    # The first prompt should be to collect the city/property
    state, response = cm.handle_input("")
    assert state == State.COLLECT_CITY.name
    assert "city" in response.lower() or "property" in response.lower()

def test_collect_city_valid():
    cm = ConversationManager()
    cm.handle_input("")  # Move to COLLECT_CITY
    # Provide a valid property/city
    state, response = cm.handle_input("Indiranagar")
    assert state == State.COLLECT_NAME.name
    assert "name" in response.lower()

def test_collect_city_invalid():
    cm = ConversationManager()
    cm.handle_input("")  # Move to COLLECT_CITY
    # Provide an invalid property/city
    state, response = cm.handle_input("Atlantis")
    assert state == State.COLLECT_CITY.name
    assert "do not have any property" in response.lower()

def test_collect_name_and_confirm():
    cm = ConversationManager()
    cm.handle_input("")  # COLLECT_CITY
    cm.handle_input("Indiranagar")  # COLLECT_NAME
    state, response = cm.handle_input("Aryamann")  # Name provided
    assert "confirm" in response.lower() and "aryamann" in response.lower()
    # Confirm the name
    state, response = cm.handle_input("yes")
    assert state == State.COLLECT_PHONE.name
    assert "phone" in response.lower()

def test_collect_phone_invalid():
    cm = ConversationManager()
    cm.handle_input("")  # COLLECT_CITY
    cm.handle_input("Indiranagar")  # COLLECT_NAME
    cm.handle_input("Aryamann")  # Name
    cm.handle_input("yes")  # Confirm name
    # Provide invalid phone
    state, response = cm.handle_input("12345")
    assert state == State.COLLECT_PHONE.name
    assert "valid 10 digit phone" in response.lower()

def test_collect_phone_and_confirm():
    cm = ConversationManager()
    cm.handle_input("")  # COLLECT_CITY
    cm.handle_input("Indiranagar")  # COLLECT_NAME
    cm.handle_input("Aryamann")  # Name
    cm.handle_input("yes")  # Confirm name
    # Provide valid phone
    state, response = cm.handle_input("9876543210")
    assert state == State.CONFIRM_CONTACT.name
    assert "9876543210" in response
    # Confirm phone and name
    state, response = cm.handle_input("yes")
    assert state == State.END.name
    assert "thank you" in response.lower()

def test_correction_flow():
    cm = ConversationManager()
    cm.handle_input("")  # COLLECT_CITY
    cm.handle_input("Indiranagar")  # COLLECT_NAME
    cm.handle_input("Aryamann")  # Name
    cm.handle_input("yes")  # Confirm name
    cm.handle_input("9876543210")  # Phone
    # User says phone is wrong
    state, response = cm.handle_input("no")
    assert state == State.COLLECT_PHONE.name
    assert "phone" in response.lower()

