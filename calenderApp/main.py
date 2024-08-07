from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import platform
from datetime import datetime
import calendar
import json

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass

class MonthGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

class CalendarApp(App):
    def build(self):
        if platform == 'android':
            request_permissions([Permission.SEND_SMS, Permission.RECEIVE_SMS, Permission.READ_SMS])
        self.main_layout = BoxLayout(orientation='vertical')
        
        # Year selection
        year_layout = BoxLayout(size_hint_y=None, height=30)
        self.year_input = TextInput(text=str(datetime.now().year), multiline=False)
        year_button = Button(text="Go to Year")
        year_button.bind(on_press=self.update_calendar)
        year_layout.add_widget(self.year_input)
        year_layout.add_widget(year_button)
        
        # Calendar grid inside ScrollView
        scroll_view = ScrollView(size_hint=(1, 1))
        self.calendar_grid = GridLayout(cols=3, spacing=10, size_hint_y=None)
        self.calendar_grid.bind(minimum_height=self.calendar_grid.setter('height'))
        scroll_view.add_widget(self.calendar_grid)
        
        # Peer phone number input
        connection_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.phone_input = TextInput(multiline=False, hint_text="Enter peer phone number")
        self.connect_button = Button(text="Set Peer")
        self.connect_button.bind(on_press=self.set_peer)
        
        connection_layout.add_widget(self.phone_input)
        connection_layout.add_widget(self.connect_button)
        
        self.main_layout.add_widget(year_layout)
        self.main_layout.add_widget(scroll_view)
        self.main_layout.add_widget(connection_layout)
        
        self.calendar_data = {}
        self.peer_phone = None

        if platform == 'android':
            self.setup_sms_receiver()

        self.update_calendar()
        return self.main_layout

    def update_calendar(self, instance=None):
        self.calendar_grid.clear_widgets()
        year = int(self.year_input.text)
        for month in range(1, 13):
            month_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
            month_layout.bind(minimum_height=month_layout.setter('height'))
            
            month_label = Label(text=calendar.month_name[month], size_hint_y=None, height=40)
            month_layout.add_widget(month_label)
            
            days_label = BoxLayout(size_hint_y=None, height=30)
            for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
                days_label.add_widget(Label(text=day))
            month_layout.add_widget(days_label)
            
            month_grid = MonthGrid()
            month_layout.add_widget(month_grid)
            
            # Add blank spaces for days before the 1st
            first_day = calendar.weekday(year, month, 1)
            for _ in range(first_day):
                month_grid.add_widget(Label(text='', size_hint_y=None, height=40))
            
            # Add day buttons
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                date = datetime(year, month, day)
                date_str = date.strftime("%Y-%m-%d")
                btn = Button(text=str(day), size_hint_y=None, height=40)
                if date_str in self.calendar_data:
                    btn.text += f"\n{self.calendar_data[date_str][:10]}..."  # Show first 10 chars
                btn.bind(on_press=lambda x, date=date: self.show_date_popup(date))
                month_grid.add_widget(btn)
            
            # Add blank spaces for remaining days
            remaining_spaces = 7 - (month_grid.children.__len__() % 7)
            if remaining_spaces < 7:
                for _ in range(remaining_spaces):
                    month_grid.add_widget(Label(text='', size_hint_y=None, height=40))
            
            self.calendar_grid.add_widget(month_layout)


    def show_date_popup(self, date):
        content = BoxLayout(orientation='vertical')
        text_input = TextInput(text=self.calendar_data.get(date.strftime("%Y-%m-%d"), ""))
        save_button = Button(text="Save")
        
        popup = Popup(title=date.strftime("%Y-%m-%d"), content=content, size_hint=(None, None), size=(300, 200))
        
        save_button.bind(on_press=lambda x: self.save_date_entry(date, text_input.text, popup))
        
        content.add_widget(text_input)
        content.add_widget(save_button)
        
        popup.open()

    def save_date_entry(self, date, text, popup):
        date_str = date.strftime("%Y-%m-%d")
        self.calendar_data[date_str] = text
        popup.dismiss()
        self.update_calendar()
        self.sync_calendar_data()

    def set_peer(self, instance):
        self.peer_phone = self.phone_input.text
        print(f"Peer phone number set to: {self.peer_phone}")

    def sync_calendar_data(self):
        if self.peer_phone:
            message = json.dumps(self.calendar_data)
            if platform == 'android':
                self.send_sms(self.peer_phone, message)
            else:
                print(f"Would send SMS to {self.peer_phone}: {message}")
        else:
            print("Peer phone number not set")

    def setup_sms_receiver(self):
        if platform == 'android':
            MyPythonActivity = autoclass('org.test.smsreceiver.MyPythonActivity')
            SMSReceiver = autoclass('org.test.smsreceiver.SMSReceiver')
            SMSReceiver.start(MyPythonActivity.mActivity, 'on_sms_received')

    def on_sms_received(self, sender, message):
        try:
            received_data = json.loads(message)
            self.calendar_data.update(received_data)
            Clock.schedule_once(lambda dt: self.update_calendar())
        except json.JSONDecodeError:
            print("Received SMS is not valid calendar data")

    def send_sms(self, phone_number, message):
        if platform == 'android':
            MyPythonActivity = autoclass('org.test.smsreceiver.MyPythonActivity')
            SmsManager = autoclass('android.telephony.SmsManager')
            sms_manager = SmsManager.getDefault()
            sms_manager.sendTextMessage(phone_number, None, message, None, None)

if __name__ == '__main__':
    CalendarApp().run()
