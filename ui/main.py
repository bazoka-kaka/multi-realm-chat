import flet as ft
from create_group_form import *
from signin_form import *
from signup_form import *
from join_form import *
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
            print("Redirecting to list...")
            page.session.set("user", user)
            page.route = "/list"
            page.pubsub.send_all(
                Message(
                    user=user,
                    text=f"{user} has joined the chat.",
                    message_type="login_message",
                )
            )
            # send_to_server(json.dumps({"type": "auth", "username": user, "password": password}))
            res = send_to_server(f"auth {user} {password}")
            data = json.loads(res)
            page.session.set("session", data['tokenid'])
            print(data['status'], data['tokenid'])
            page.update()
            
    def create_grp(group_name: str):
        db = UsersDB()
        if db.read_group(group_name):
            print("Group already exists ...")
            page.banner.open = True
            page.update()
        else:
            print("Redirecting to list...")
            page.route = "/list"
            # send_to_server(json.dumps({"type": "create_group", "group_name": group_name}))
            session = page.session.get("session")
            print(session)
            send_to_server(f"create_group {session} {group_name}")
            db.write_group(group_name)
            page.update()
            
    def get_group_messages(group_name:str):
        sessid = page.session.get("session")
        res = send_to_server(f"group_inbox {sessid} {group_name}")
        print(res)
        data = json.loads(res)
        return data['messages']

    def join_grp(group_name: str):
        db = UsersDB()
        if not db.read_group(group_name):
            print("Group doesn't exists ...")
            page.banner.open = True
            page.update()
        else:
            print("Redirecting to group chat...")
            page.route = "/chat"
            # send_to_server(json.dumps({"type": "create_group", "group_name": group_name}))
            session = page.session.get("session")
            print(session)
            send_to_server(f"join_group {session} {group_name}")
            db.write_group(group_name)
            page.session.set("group", group_name)
            messages = get_group_messages(group_name=group_name)
            db.set_messages(group_name=group_name, group_messages=messages)
            # implement messages to ui
            for message in messages:
                print(message)
                msg = Message(user=message['msg_from'], text=message['msg'], message_type="chat_message")
                m = ChatMessage(msg)
                chat.controls.append(m)
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
        # m = ChatMessage(message)
        # chat.controls.append(m)
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
        group_name = page.session.get("group")
        session = page.session.get("session")
        send_to_server(f"send_group {session} {group_name} {message}")

        # send_to_server(json.dumps({"type": "message", "user": page.session.get("user"), "message": message}))
        new_message.value = ""
        page.update()

    def btn_signin(e):
        page.route = "/"
        page.update()
        
    def btn_join(e):
        page.route = "/join"
        page.update()

    def btn_create(e):
        page.route = "/create-group"
        page.update()

    def btn_signup(e):
        page.route = "/signup"
        page.update()

    def btn_exit(e):
        page.session.remove("user")
        page.route = "/"
        page.update()

    def create_group_chat(e):
        def close_and_redirect(e):
          page.dialog.open = False
          page.route = "/create-group"
          page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Send Group Message"),
            content=ft.Text("Functionality to send a group message will be implemented here."),
            actions=[ft.TextButton("OK", on_click=close_and_redirect)],
        )
        page.dialog.open = True
        page.update()

    def join_group_chat(e):
        def close_and_redirect(e):
          page.dialog.open = False
          page.route = "/join"
          page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Send Group Message"),
            content=ft.Text("Functionality to send a group message will be implemented here."),
            actions=[ft.TextButton("OK", on_click=close_and_redirect)],
        )
        page.dialog.open = True
        page.update()

    def send_private_message(e):
        def close_and_redirect(e):
            page.dialog.open = False
            page.route = "/chat"
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Send Private Message"),
            content=ft.Text("Functionality to send a private message will be implemented here."),
            actions=[ft.TextButton("OK", on_click=close_and_redirect)],
        )
        page.dialog.open = True
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
    create_group = CreateGroup(create_grp, btn_join)
    join_group = JoinForm(join_grp, btn_create)

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
        content=ft.Text("An error occured!"),
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

        if page.route == "/create-group":
            page.clean()
            page.add(
                ft.Column(
                    [
                        principal_content,
                        create_group
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        if page.route == "/join":
            page.clean()
            page.add(
                ft.Column(
                    [
                        principal_content,
                        join_group
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
        
        if page.route == "/list":
            page.clean()
            page.add(
                ft.Column(
                    [
                        ft.TextButton("Send Private Message", on_click=send_private_message),
                        ft.TextButton("Create New Group Chat", on_click=create_group_chat),
                        ft.TextButton("Join Group Chat", on_click=join_group_chat),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                )
            )

    
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