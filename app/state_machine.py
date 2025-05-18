

from enum import Enum, auto
from jinja2 import Environment, FileSystemLoader
from app.knowledge_base import KnowledgeBase
from app.utils import validate_phone, validate_date, validate_time
from app.google_sheet import log_to_sheet
from datetime import datetime


class State(Enum):
    INIT = auto()
    COLLECT_CITY = auto()
    COLLECT_PROPERTY = auto()
    COLLECT_NAME = auto()
    COLLECT_PHONE = auto()
    CONFIRM_CONTACT = auto()
    HANDLE_ENQUIRY = auto()
    COLLECT_BOOKING_DATE = auto()
    COLLECT_BOOKING_TIME = auto()
    COLLECT_GUESTS = auto()
    CONFIRM_BOOKING = auto()
    MODIFY_BOOKING = auto()
    CANCEL_BOOKING = auto()
    ANSWER_FAQ = auto()
    END = auto()


class ConversationManager:
    def __init__(self):
        self.state = State.INIT
        self.context = {}
        self.env = Environment(loader=FileSystemLoader('prompts'))
        self.kb = KnowledgeBase()

    def handle_input(self, user_input):
        try:
            if self.state == State.INIT:
                return self._handle_init()

            elif self.state == State.COLLECT_CITY:
                return self._handle_city(user_input)

            elif self.state == State.COLLECT_PROPERTY:
                return self._handle_property(user_input)

            elif self.state == State.HANDLE_ENQUIRY:
                return self._handle_enquiry(user_input)

            elif self.state == State.COLLECT_NAME:
                return self._handle_name(user_input)

            elif self.state == State.COLLECT_PHONE:
                return self._handle_phone(user_input)

            elif self.state == State.CONFIRM_CONTACT:
                return self._handle_contact_confirmation(user_input)

            elif self.state == State.COLLECT_BOOKING_DATE:
                return self._handle_booking_date(user_input)

            elif self.state == State.COLLECT_BOOKING_TIME:
                return self._handle_booking_time(user_input)

            elif self.state == State.COLLECT_GUESTS:
                return self._handle_guests(user_input)

            elif self.state == State.CONFIRM_BOOKING:
                return self._handle_booking_confirmation(user_input)

            elif self.state in (State.MODIFY_BOOKING, State.CANCEL_BOOKING):
                return self._handle_modification_cancellation(user_input)

            elif self.state == State.ANSWER_FAQ:
                return self._handle_faq(user_input)

            else:
                return State.END.name, "Conversation ended. Thank you!"

        except Exception as e:
            self._log_error(e)
            return State.END.name, "An error occurred. Please start over."

    def _handle_init(self):
        self.state = State.COLLECT_CITY
        return self._render("collect_city.jinja")

    def _handle_modification_cancellation(self, user_input):
        if 'retrieved_booking' not in self.context:
            if validate_phone(user_input):
                booking = self._retrieve_booking(user_input)
                if booking:
                    self.context['retrieved_booking'] = True
                    self.context.update(booking)
                    action = "modify" if self.state == State.MODIFY_BOOKING else "cancel"
                    return self.state.name, f"Found booking for {self.context['booking_date']} with {self.context['guests']} guests. {action.capitalize()} this booking? (yes/no)"
                return self.state.name, "No booking found"
            return self.state.name, "Invalid phone number"

        if user_input.lower() in ['yes', 'y']:
            if self.state == State.MODIFY_BOOKING:
                self.state = State.COLLECT_BOOKING_DATE
                return self._render("collect_booking_date.jinja")
            else:
                self._cancel_booking()
                self.state = State.END
                return State.END.name, "Booking cancelled successfully"

        self.state = State.HANDLE_ENQUIRY
        return self._render("handle_enquiry.jinja")

    def _handle_faq(self, user_input):
        answer = self.kb.answer_faq(user_input, self.context.get('city'))
        if answer:
            self.context['faq_answer'] = answer
            self.state = State.HANDLE_ENQUIRY
            return self._render("answer_faq.jinja")
        return self.state.name, "I couldn't find an answer to that question"

    def _retrieve_booking(self, phone):
        return {
            'booking_date': '2025-06-01',
            'guests': '4',
            'property_name': self.context.get('property_name', 'BBQ Nation Indiranagar'),
            'phone': phone
        }

    def _cancel_booking(self):
        self.context['booking_status'] = 'cancelled'
        self._log_conversation()

    def _handle_faq(self, user_input):
        """Handles FAQ questions using knowledge base"""
        answer = self.kb.answer_faq(user_input, self.context.get('city'))
        if answer:
            self.context['faq_answer'] = answer
            self.state = State.HANDLE_ENQUIRY
            return self._render("answer_faq.jinja")
        return self.state.name, "I couldn't find an answer to that. Please try another question."

    # Helper methods
    def _retrieve_booking(self, phone):
        """Simulates booking retrieval from database"""
        # In real implementation, query your booking system
        return {
            'date': self.context.get('booking_date', '2025-06-01'),
            'guests': self.context.get,}

    def _handle_city(self, user_input):
        if self.kb.is_valid_city(user_input):
            self.context['city'] = user_input
            self.state = State.COLLECT_PROPERTY
            return self._render("collect_property.jinja", city=user_input)
        return self.state.name, "We don't operate in that city. Please choose Delhi or Bangalore."

    def _handle_property(self, user_input):
        prop = self.kb.get_property(self.context['city'], user_input)
        if prop:
            self.context.update(prop)
            self.state = State.HANDLE_ENQUIRY
            return self._render("handle_enquiry.jinja")
        return self.state.name, "Invalid property. Please choose from: " + ", ".join(
            self.kb.get_properties(self.context['city']))

    def _handle_enquiry(self, user_input):
        if user_input == '1':
            self.state = State.COLLECT_NAME
            return self._render("collect_name.jinja")
        elif user_input == '2':
            self.state = State.MODIFY_BOOKING
            return self._render("retrieve_booking.jinja")
        elif user_input == '3':
            self.state = State.CANCEL_BOOKING
            return self._render("retrieve_booking.jinja")
        elif user_input == '4':
            self.state = State.ANSWER_FAQ
            return self._render("answer_faq.jinja")
        return self.state.name, "Invalid choice. Please select 1-4."

    def _handle_name(self, user_input):
        self.context['name'] = user_input.strip()
        self.state = State.COLLECT_PHONE
        return self._render("collect_phone.jinja")

    def _handle_phone(self, user_input):
        if validate_phone(user_input):
            self.context['phone'] = user_input
            self.state = State.CONFIRM_CONTACT
            return self._render("confirm_contact.jinja",
                                name=self.context['name'],
                                phone=self.context['phone'])
        return self.state.name, "Invalid phone number. Please enter 10 digits."

    def _handle_contact_confirmation(self, user_input):
        if user_input.lower() in ['yes', 'y']:
            self.state = State.COLLECT_BOOKING_DATE
            return self._render("collect_booking_date.jinja")
        self.state = State.COLLECT_PHONE
        return self._render("collect_phone.jinja")

    def _handle_booking_date(self, user_input):
        if validate_date(user_input):
            self.context['booking_date'] = user_input
            self.state = State.COLLECT_BOOKING_TIME
            return self._render("collect_booking_time.jinja")
        return self.state.name, "Invalid date format. Use YYYY-MM-DD."

    def _handle_booking_time(self, user_input):
        if validate_time(user_input):
            self.context['booking_time'] = user_input
            self.state = State.COLLECT_GUESTS
            return self._render("collect_guests.jinja")
        return self.state.name, "Invalid time format. Use HH:MM."

    def _handle_guests(self, user_input):
        if user_input.isdigit() and int(user_input) > 0:
            self.context['guests'] = user_input
            self.state = State.CONFIRM_BOOKING
            return self._render("confirm_booking.jinja", **self.context)
        return self.state.name, "Invalid number. Please enter positive integer."

    def _handle_booking_confirmation(self, user_input):
        if user_input.lower() in ['yes', 'y']:
            self._log_conversation()
            self.state = State.END
            return self.state.name, "Booking confirmed! Details sent via SMS."
        self.state = State.COLLECT_BOOKING_DATE
        return self._render("collect_booking_date.jinja")

    def _log_conversation(self):
        log_data = {
            'modality': 'Chatbot',
            'call_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'phone_number': self.context.get('phone', 'NA'),
            'call_outcome': 'Booking' if 'booking_date' in self.context else 'Enquiry',
            'room_name': self.context.get('property_name', 'NA'),
            'booking_date': self.context.get('booking_date', 'NA'),
            'booking_time': self.context.get('booking_time', 'NA'),
            'num_guests': self.context.get('guests', 'NA'),
            'customer_name': self.context.get('name', ''),
            'call_summary': self._generate_summary()
        }
        log_to_sheet(log_data)

    def _generate_summary(self):
        return f"{self.context.get('name', 'User')} booked for {self.context.get('guests', 'N/A')} guests on {self.context.get('booking_date', 'N/A')} at {self.context.get('booking_time', 'N/A')}"

    def _render(self, template_name, **kwargs):
        template = self.env.get_template(template_name)
        return self.state.name, template.render(context=self.context,State=State, **kwargs)

    def _log_error(self, error):
        print(f"Error in state {self.state.name}: {str(error)}")
