"""
AlarMed - Emergency Contacts Screen
Clean responsive design
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.app import App
import webbrowser

class EmergencyScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def on_enter(self):
        self.refresh_contacts()
    
    def build_ui(self):
        app = App.get_running_app()
        
        main_layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Emergency Contacts",
            left_action_items=[["arrow-left", lambda x: app.go_to_screen('dashboard')]],
            md_bg_color=[0.85, 0.33, 0.31, 1],
            elevation=0
        )
        main_layout.add_widget(toolbar)
        
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Add contact card
        add_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15]
        )
        
        add_title = MDLabel(
            text="Add New Contact",
            font_style="H6",
            size_hint_y=None,
            height=dp(35)
        )
        add_card.add_widget(add_title)
        
        self.contact_name = MDTextField(
            hint_text="Contact Name",
            required=True,
            size_hint_y=None,
            height=dp(56),
            mode="rectangle"
        )
        add_card.add_widget(self.contact_name)
        
        self.contact_phone = MDTextField(
            hint_text="Phone Number",
            required=True,
            input_filter='int',
            size_hint_y=None,
            height=dp(56),
            mode="rectangle"
        )
        add_card.add_widget(self.contact_phone)
        
        type_items = [
            {"text": t, "viewclass": "OneLineListItem", "on_release": lambda x=t: self.set_contact_type(x)}
            for t in ["Emergency", "Medical", "Family", "Friend", "Other"]
        ]
        
        self.type_menu = MDDropdownMenu(items=type_items, width_mult=4)
        
        self.type_btn = MDRaisedButton(
            text="Type: Emergency",
            size_hint_y=None,
            height=dp(48),
            md_bg_color=[0.15, 0.15, 0.15, 1],
            on_release=lambda x: self.type_menu.open()
        )
        self.type_menu.caller = self.type_btn
        add_card.add_widget(self.type_btn)
        
        add_btn = MDRaisedButton(
            text="ADD CONTACT",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=[0.18, 0.65, 0.45, 1],
            on_release=lambda x: self.add_contact()
        )
        add_card.add_widget(add_btn)
        
        add_card.height = dp(350)
        content.add_widget(add_card)
        
        list_label = MDLabel(
            text="Contact List",
            font_style="H6",
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(list_label)
        
        self.contacts_list = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None
        )
        self.contacts_list.bind(minimum_height=self.contacts_list.setter('height'))
        content.add_widget(self.contacts_list)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        self.refresh_contacts()
    
    def set_contact_type(self, contact_type):
        self.type_btn.text = f"Type: {contact_type}"
        self.type_menu.dismiss()
    
    def add_contact(self):
        app = App.get_running_app()
        
        name = self.contact_name.text.strip()
        phone = self.contact_phone.text.strip()
        contact_type = self.type_btn.text.replace("Type: ", "")
        
        if not name or not phone:
            dialog = MDDialog(
                title="Missing Information",
                text="Please fill in all fields",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            return
        
        try:
            app.db.add_emergency_contact(name, phone, contact_type)
            
            dialog = MDDialog(
                title="Success",
                text="Contact added successfully",
                buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            
            self.contact_name.text = ""
            self.contact_phone.text = ""
            self.type_btn.text = "Type: Emergency"
            
            self.refresh_contacts()
            
        except Exception as e:
            dialog = MDDialog(
                title="Error",
                text=f"Failed: {str(e)}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
    
    def refresh_contacts(self):
        app = App.get_running_app()
        self.contacts_list.clear_widgets()
        
        contacts = app.db.get_all_emergency_contacts()
        
        if not contacts:
            empty_card = MDCard(
                orientation='vertical',
                padding=dp(30),
                size_hint_y=None,
                height=dp(120),
                md_bg_color=[0.1, 0.1, 0.1, 1],
                radius=[15, 15, 15, 15]
            )
            
            empty_label = MDLabel(
                text="No contacts yet",
                halign='center',
                theme_text_color='Secondary',
                font_style="Body2"
            )
            empty_card.add_widget(empty_label)
            self.contacts_list.add_widget(empty_card)
            return
        
        type_colors = {
            "Emergency": [0.85, 0.33, 0.31, 1],
            "Medical": [0.12, 0.42, 0.65, 1],
            "Family": [0.18, 0.65, 0.45, 1],
            "Friend": [0.94, 0.68, 0.31, 1],
            "Other": [0.3, 0.3, 0.3, 1]
        }
        
        for contact in contacts:
            contact_id, name, phone, contact_type, priority = contact
            
            color = type_colors.get(contact_type, [0.1, 0.1, 0.1, 1])
            
            contact_card = MDCard(
                orientation='vertical',
                padding=dp(20),
                spacing=dp(12),
                size_hint_y=None,
                md_bg_color=[0.1, 0.1, 0.1, 1],
                radius=[15, 15, 15, 15]
            )
            
            header = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35)
            )
            
            name_label = MDLabel(
                text=name,
                font_style="H6",
                size_hint_x=0.7
            )
            header.add_widget(name_label)
            
            type_badge = MDLabel(
                text=contact_type,
                font_style="Caption",
                halign='right',
                theme_text_color='Secondary',
                size_hint_x=0.3
            )
            header.add_widget(type_badge)
            
            contact_card.add_widget(header)
            
            phone_card = MDCard(
                padding=dp(12),
                size_hint_y=None,
                height=dp(45),
                md_bg_color=[0.15, 0.15, 0.15, 1],
                radius=[10, 10, 10, 10]
            )
            
            phone_label = MDLabel(
                text=phone,
                halign='center',
                font_style="Body1"
            )
            phone_card.add_widget(phone_label)
            contact_card.add_widget(phone_card)
            
            btn_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(48)
            )
            
            call_btn = MDRaisedButton(
                text="CALL",
                md_bg_color=[0.18, 0.65, 0.45, 1],
                on_release=lambda x, p=phone: self.call_contact(p)
            )
            btn_layout.add_widget(call_btn)
            
            delete_btn = MDFlatButton(
                text="DELETE",
                theme_text_color='Error',
                on_release=lambda x, c_id=contact_id: self.confirm_delete_contact(c_id)
            )
            btn_layout.add_widget(delete_btn)
            
            contact_card.add_widget(btn_layout)
            
            contact_card.height = dp(180)
            self.contacts_list.add_widget(contact_card)
    
    def call_contact(self, phone):
        try:
            webbrowser.open(f"tel:{phone}")
        except:
            pass
        
        dialog = MDDialog(
            title="Calling",
            text=f"Opening phone dialer:\n{phone}",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def confirm_delete_contact(self, contact_id):
        dialog = MDDialog(
            title="Delete Contact",
            text="Are you sure you want to delete this contact?",
            buttons=[
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=[0.85, 0.33, 0.31, 1],
                    on_release=lambda x: self.delete_contact(contact_id, dialog)
                ),
                MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
            ],
        )
        dialog.open()
    
    def delete_contact(self, contact_id, dialog):
        app = App.get_running_app()
        
        try:
            app.db.delete_emergency_contact(contact_id)
            dialog.dismiss()
            self.refresh_contacts()
        except Exception as e:
            print(f"Error deleting: {e}")
