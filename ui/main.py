import flet as ft
from signin_form import *
from signup_form import *
from users_db import *
from chat_message import *
import socket
import json

server_ip = '127.0.0.1'
server_port = 8889

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

def send_to_server(message):
    client_socket.sendall((message + '\r\n').encode())
    response = ""
    while True:
        data = client_socket.recv(32)
        if data:
            response += data.decode()
            if response[-2:] == '\r\n':
                break
    return response.strip()

def main(page: ft.Page):
    page.title = "Multi Realm Chat"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Functions
    def dropdown_changed(e):
        new_message.value = new_message.value + emoji_list.value
        page.update()

    def close_banner(e):
        page.banner.open = False
        page.update()

    def open_dlg():
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dlg(e):
        dlg.open = False
        page.route = "/"
        page.update()

    def sign_in(user: str, password: str):
        db = UsersDB()
        if not db.read_db(user, password):
            print("User no exist ...")
            page.banner.open = True
            page.update()
        else:
            print("Redirecting to chat...")
            page.session.set("user", user)
            page.route = "/chat"
            page.pubsub.send_all(
                Message(
                    user=user,
                    text=f"{user} has joined the chat.",
                    message_type="login_message",
                )
            )
            send_to_server(json.dumps({"type": "login", "user": user}))
            page.update()

    def sign_up(user: str, password: str):
        db = UsersDB()
        if db.write_db(user, password):
            print("Successfully Registered User...")
            open_dlg()
            send_to_server(json.dumps({"type": "signup", "user": user}))

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.WHITE, size=12)
        chat.controls.append(m)
        page.update()

    page.pubsub.subscribe(on_message)

    def send_message_click(e):
        message = new_message.value
        page.pubsub.send_all(
            Message(
                user=page.session.get("user"),
                text=message,
                message_type="chat_message",
            )
        )
        send_to_server(json.dumps({"type": "message", "user": page.session.get("user"), "message": message}))
        new_message.value = ""
        page.update()

    def btn_signin(e):
        page.route = "/"
        page.update()

    def btn_signup(e):
        page.route = "/signup"
        page.update()

    def btn_exit(e):
        page.session.remove("user")
        page.route = "/"
        page.update()


    """
    Application UI
    """
    principal_content = ft.Column(
        [
            ft.Text(value="Multi Realm Chat", size=50, color=ft.colors.WHITE),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    emoji_list = ft.Dropdown(
        on_change=dropdown_changed,
        options=[
            ft.dropdown.Option("😃"),
            ft.dropdown.Option("😊"),
            ft.dropdown.Option("😂"),
            ft.dropdown.Option("🤔"),
            ft.dropdown.Option("😭"),
            ft.dropdown.Option("😉"),
            ft.dropdown.Option("🤩"),
            ft.dropdown.Option("🥰"),
            ft.dropdown.Option("😎"),
            ft.dropdown.Option("❤️"),
            ft.dropdown.Option("🔥"),
            ft.dropdown.Option("✅"),
            ft.dropdown.Option("✨"),
            ft.dropdown.Option("👍"),
            ft.dropdown.Option("🎉"),
            ft.dropdown.Option("👉"),
            ft.dropdown.Option("⭐"),
            ft.dropdown.Option("☀️"),
            ft.dropdown.Option("👀"),
            ft.dropdown.Option("👇"),
            ft.dropdown.Option("🚀"),
            ft.dropdown.Option("🎂"),
            ft.dropdown.Option("💕"),
            ft.dropdown.Option("🏡"),
            ft.dropdown.Option("🍎"),
            ft.dropdown.Option("🎁"),
            ft.dropdown.Option("💯"),
            ft.dropdown.Option("💤"),
        ],
        width=50,
        value="😃",
        alignment=ft.alignment.center,
        border_color=ft.colors.AMBER,
        color=ft.colors.AMBER,
    )

    signin_UI = SignInForm(sign_in, btn_signup)
    signup_UI = SignUpForm(sign_up, btn_signin)

    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    page.banner = ft.Banner(
        bgcolor=ft.colors.BLACK45,
        leading=ft.Icon(ft.icons.ERROR, color=ft.colors.RED, size=40),
        content=ft.Text("Log in failed, Incorrect User Name or Password"),
        actions=[
            ft.TextButton("Ok", on_click=close_banner),
        ],
    )

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Container(
            content=ft.Icon(
                name=ft.icons.CHECK_CIRCLE_OUTLINED, color=ft.colors.GREEN, size=100
            ),
            width=120,
            height=120,
        ),
        content=ft.Text(
            value="Congratulations,\n your account has been successfully created\n Please Sign In",
            text_align=ft.TextAlign.CENTER,
        ),
        actions=[
            ft.ElevatedButton(
                text="Continue", color=ft.colors.WHITE, on_click=close_dlg
            )
        ],
        actions_alignment="center",
        on_dismiss=lambda e: print("Dialog dismissed!"),
    )

    """
    Routes
    """
    def route_change(route):
        if page.route == "/":
            page.clean()
            page.add(
                ft.Column(
                    [
                        principal_content,
                        signin_UI
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        if page.route == "/signup":
            page.clean()
            page.add(
                ft.Column(
                    [
                        principal_content,
                        signup_UI
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        if page.route == "/chat":
            if page.session.contains_key("user"):
                page.clean()
                page.add(
                    ft.Row(
                        [
                            ft.Text(value="Multi Realm Chat", color=ft.colors.WHITE),
                            ft.ElevatedButton(
                                text="Log Out",
                                bgcolor=ft.colors.RED_800,
                                on_click=btn_exit,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    )
                )
                page.add(
                    ft.Container(
                        content=chat,
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        border_radius=5,
                        padding=10,
                        expand=True,
                    )
                )
                page.add(
                    ft.Row(
                        controls=[
                            emoji_list,
                            new_message,
                            ft.IconButton(
                                icon=ft.icons.SEND_ROUNDED,
                                tooltip="Send message",
                                on_click=send_message_click,
                            ),
                        ],
                    )
                )

            else:
                page.route = "/"
                page.update()

    page.on_route_change = route_change
    page.add(
        ft.Column(
            [
                principal_content,
                signin_UI
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

ft.app(target=main, view=ft.WEB_BROWSER)