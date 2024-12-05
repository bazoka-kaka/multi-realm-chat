import flet as ft
from users_db import *

# SignUp Form
class JoinForm(ft.UserControl):
    def __init__(self, submit_values,btn_create):
        super().__init__()
        #Return values user and password
        self.submit_values = submit_values
        #Route to signup Form
        self.btn_create = btn_create

    def btn_join(self, e):
        if not self.dropdown_realm.value:
            self.dropdown_realm.error_text="Please select a group!"
            self.dropdown_realm.update()
        else:
            #Return values 'user' and 'password' as arguments
            self.submit_values(self.dropdown_realm.value)
    def build(self):
        self.title_form=ft.Text(value="Join a group!",text_align=ft.TextAlign.CENTER,size=30, )
        db = UsersDB()
        options = []
        for group in db.groups_list:
            options.append(ft.dropdown.Option(group['name']))
        self.dropdown_realm = ft.Dropdown(
            label="Choose The Group",
            options=options
        )
        self.text_join=ft.ElevatedButton(text="Join Group",color=ft.colors.WHITE,width=150,height=50,on_click=self.btn_join)
        self.text_create=ft.Row(controls=[ft.Text(value="Want to create a new group?"),ft.TextButton(text="Create here",on_click=self.btn_create)],alignment=ft.MainAxisAlignment.CENTER)

        return ft.Container(
            width=500,
            height=560,
            bgcolor=ft.colors.TEAL_400,
            padding=30,
            border_radius=10,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    self.title_form,
                    ft.Container(height=30),
                    self.dropdown_realm,
                    ft.Container(height=10),
                    self.text_join,
                    ft.Container(height=20),
                    self.text_create,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )