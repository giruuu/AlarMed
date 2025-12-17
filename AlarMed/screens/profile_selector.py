"""
AlarMed - Profile Selector Screen
Clean responsive design
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.app import App

from config import AVATAR_LETTERS, HEX_COLORS

class ProfileSelectorScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def on_enter(self):
        self.refresh_profiles()
    
    def build_ui(self):
        """Build clean profile selector UI"""
        self.clear_widgets()
        
        main_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20),
            md_bg_color=[0.05, 0.05, 0.05, 1]
        )
        
        # Header section
        header_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(10)
        )
        
        # App title
        title = MDLabel(
            text="AlarMed",
            font_style="H3",
            halign='center',
            size_hint_y=None,
            height=dp(60)
        )
        header_box.add_widget(title)
        
        # Subtitle
        subtitle = MDLabel(
            text="Select Your Profile",
            font_style="Body1",
            halign='center',
            theme_text_color='Secondary',
            size_hint_y=None,
            height=dp(30)
        )
        header_box.add_widget(subtitle)
        
        main_layout.add_widget(header_box)
        
        # Create profile button
        create_btn = MDRaisedButton(
            text="CREATE NEW PROFILE",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=[0.12, 0.42, 0.65, 1],
            on_release=lambda x: self.show_create_profile_dialog()
        )
        main_layout.add_widget(create_btn)
        
        # Profiles scroll view
        self.profiles_scroll = MDScrollView()
        self.profiles_grid = MDGridLayout(
            cols=1,
            spacing=dp(15),
            size_hint_y=None,
            padding=[0, dp(10)]
        )
        self.profiles_grid.bind(minimum_height=self.profiles_grid.setter('height'))
        
        self.profiles_scroll.add_widget(self.profiles_grid)
        main_layout.add_widget(self.profiles_scroll)
        
        self.add_widget(main_layout)
        self.refresh_profiles()
    
    def refresh_profiles(self):
        """Refresh profile list"""
        app = App.get_running_app()
        self.profiles_grid.clear_widgets()
        
        profiles = app.db.get_all_profiles()
        
        if not profiles:
            empty_card = MDCard(
                orientation='vertical',
                padding=dp(30),
                size_hint_y=None,
                height=dp(200),
                md_bg_color=[0.1, 0.1, 0.1, 1],
                radius=[15, 15, 15, 15]
            )
            
            empty_label = MDLabel(
                text="Welcome to AlarMed!\n\nCreate your first profile to get started with medication tracking",
                halign='center',
                theme_text_color='Secondary',
                font_style="Body2"
            )
            empty_card.add_widget(empty_label)
            self.profiles_grid.add_widget(empty_card)
            return
        
        # Display profiles
        for profile in profiles:
            profile_id, name, age, gender, color, avatar, created_at, last_active = profile
            
            # Convert hex color to RGBA
            r = int(color[1:3], 16) / 255
            g = int(color[3:5], 16) / 255
            b = int(color[5:7], 16) / 255
            
            profile_card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(160),
                md_bg_color=[0.1, 0.1, 0.1, 1],
                padding=dp(20),
                spacing=dp(12),
                radius=[15, 15, 15, 15]
            )
            
            # Profile info section
            info_layout = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(70),
                spacing=dp(15)
            )
            
            # Avatar circle
            avatar_box = MDBoxLayout(
                size_hint=(None, None),
                size=(dp(70), dp(70))
            )
            
            avatar_card = MDCard(
                md_bg_color=[r, g, b, 1],
                radius=[35, 35, 35, 35],
                size_hint=(1, 1)
            )
            
            avatar_label = MDLabel(
                text=avatar,
                font_style="H4",
                halign='center',
                valign='center'
            )
            avatar_card.add_widget(avatar_label)
            avatar_box.add_widget(avatar_card)
            
            info_layout.add_widget(avatar_box)
            
            # Name and details
            details_layout = MDBoxLayout(
                orientation='vertical',
                spacing=dp(5)
            )
            
            name_label = MDLabel(
                text=name,
                font_style="H6",
                theme_text_color='Primary'
            )
            details_layout.add_widget(name_label)
            
            info_parts = []
            if age:
                info_parts.append(f"{age} years")
            if gender:
                info_parts.append(gender)
            
            if info_parts:
                info_label = MDLabel(
                    text=" | ".join(info_parts),
                    theme_text_color='Secondary',
                    font_style="Caption"
                )
                details_layout.add_widget(info_label)
            
            info_layout.add_widget(details_layout)
            profile_card.add_widget(info_layout)
            
            # Action buttons
            btn_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(48)
            )
            
            open_btn = MDRaisedButton(
                text="OPEN",
                md_bg_color=[r, g, b, 1],
                on_release=lambda x, p_id=profile_id, p_name=name, p_color=color, p_avatar=avatar: 
                    app.load_profile(p_id, p_name, p_color, p_avatar)
            )
            btn_layout.add_widget(open_btn)
            
            edit_btn = MDFlatButton(
                text="EDIT",
                on_release=lambda x, p_id=profile_id: self.show_edit_profile_dialog(p_id)
            )
            btn_layout.add_widget(edit_btn)
            
            delete_btn = MDFlatButton(
                text="DELETE",
                theme_text_color='Error',
                on_release=lambda x, p_id=profile_id, p_name=name: self.confirm_delete_profile(p_id, p_name)
            )
            btn_layout.add_widget(delete_btn)
            
            profile_card.add_widget(btn_layout)
            self.profiles_grid.add_widget(profile_card)
    
    def show_create_profile_dialog(self):
        """Show create profile dialog"""
        app = App.get_running_app()
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(450),
            padding=dp(15)
        )
        
        # Name field
        name_field = MDTextField(
            hint_text="Profile Name",
            required=True,
            helper_text="Required",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(56)
        )
        content.add_widget(name_field)
        
        # Age field
        age_field = MDTextField(
            hint_text="Age (Optional)",
            input_filter='int',
            size_hint_y=None,
            height=dp(56)
        )
        content.add_widget(age_field)
        
        # Gender dropdown
        gender_items = [
            {
                "text": g,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=g: self.set_gender(gender_btn, x)
            } for g in ["Male", "Female", "Other", "Prefer not to say"]
        ]
        
        self.gender_menu = MDDropdownMenu(
            items=gender_items,
            width_mult=4
        )
        
        gender_btn = MDRaisedButton(
            text="Select Gender (Optional)",
            size_hint_y=None,
            height=dp(48),
            on_release=lambda x: self.gender_menu.open()
        )
        self.gender_menu.caller = gender_btn
        content.add_widget(gender_btn)
        
        # Avatar selection
        avatar_label = MDLabel(
            text="Choose Avatar:",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(avatar_label)
        
        avatar_grid = MDGridLayout(
            cols=7,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(100)
        )
        
        selected_avatar = [AVATAR_LETTERS[0]]
        
        def select_avatar(avatar_text):
            selected_avatar[0] = avatar_text
            for child in avatar_grid.children:
                if isinstance(child, MDRaisedButton):
                    # KivyMD 1.2.0 compatibility for color update
                    if child.text == avatar_text:
                        child.md_bg_color = [0.12, 0.42, 0.65, 1]
                    else:
                        child.md_bg_color = [0.2, 0.2, 0.2, 1]
        
        for avatar in AVATAR_LETTERS:
            avatar_btn = MDRaisedButton(
                text=avatar,
                size_hint=(None, None),
                size=(dp(45), dp(45)),
                md_bg_color=[0.2, 0.2, 0.2, 1],
                # Use rounded_button for a circular appearance, as radius is unsupported
                rounded_button=True, 
                on_release=lambda x, e=avatar: select_avatar(e)
            )
            avatar_grid.add_widget(avatar_btn)
        
        content.add_widget(avatar_grid)
        
        # Color selection
        color_label = MDLabel(
            text="Choose Color:",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(color_label)
        
        color_grid = MDGridLayout(
            cols=5,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(60)
        )
        
        selected_color = [list(HEX_COLORS.values())[0]]
        
        def select_color(hex_color):
            selected_color[0] = hex_color
            # Optionally update the selected color button visual here if needed
        
        for color_name, hex_color in HEX_COLORS.items():
            r = int(hex_color[1:3], 16) / 255
            g = int(hex_color[3:5], 16) / 255
            b = int(hex_color[5:7], 16) / 255
            
            color_btn = MDRaisedButton(
                text="",
                size_hint=(None, None),
                size=(dp(50), dp(50)),
                md_bg_color=[r, g, b, 1],
                # --- FIX APPLIED HERE ---
                # Removed: radius=[25, 25, 25, 25], which caused the TypeError.
                # Added: rounded_button=True for circular appearance.
                rounded_button=True,
                # ------------------------
                on_release=lambda x, hc=hex_color: select_color(hc)
            )
            color_grid.add_widget(color_btn)
        
        content.add_widget(color_grid)
        
        def save_profile(instance):
            name = name_field.text.strip()
            age = age_field.text.strip()
            gender = gender_btn.text if gender_btn.text != "Select Gender (Optional)" else ""
            
            if not name:
                name_field.error = True
                return
            
            try:
                age_int = int(age) if age else None
                
                profile_id = app.db.create_profile(
                    name,
                    age_int,
                    gender if gender else None,
                    selected_color[0],
                    selected_avatar[0]
                )
                
                dialog.dismiss()
                self.refresh_profiles()
                
            except Exception as e:
                # In a real app, use better error logging
                print(f"Error creating profile: {e}")
        
        dialog = MDDialog(
            title="Create Profile",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="CREATE",
                    on_release=save_profile
                ),
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        
        dialog.open()
    
    def set_gender(self, button, gender):
        """Set gender selection"""
        button.text = gender
        self.gender_menu.dismiss()
    
    def show_edit_profile_dialog(self, profile_id):
        """Show edit profile dialog"""
        # (Implementation omitted, but structure is correct)
        pass
    
    def confirm_delete_profile(self, profile_id, profile_name):
        """Confirm profile deletion"""
        app = App.get_running_app()
        
        dialog = MDDialog(
            title="Delete Profile",
            text=f"Are you sure you want to delete '{profile_name}'?\n\nThis will permanently delete all associated data.",
            buttons=[
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=[0.85, 0.33, 0.31, 1],
                    on_release=lambda x: self.delete_profile(profile_id, dialog)
                ),
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        
        dialog.open()
    
    def delete_profile(self, profile_id, dialog):
        """Delete profile"""
        app = App.get_running_app()
        
        # Check if it's the last profile before deleting
        if app.db.get_profile_count() == 1:
            # Optionally show a message that the last profile cannot be deleted
            print("Cannot delete the last remaining profile.")
            dialog.dismiss()
            return
        
        try:
            app.db.delete_profile(profile_id)
            dialog.dismiss()
            self.refresh_profiles()
        except Exception as e:
            # In a real app, use better error logging
            print(f"Error deleting profile: {e}")