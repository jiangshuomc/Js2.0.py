from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, ListProperty
import os
import json
import hashlib
from datetime import datetime, date

# ─── 路径设置（兼容 Android） ───
def get_data_dir():
    try:
        return os.path.join(App.get_running_app().user_data_dir, "data")
    except:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

DATA_DIR = None

def ensure_data_dir():
    global DATA_DIR
    if DATA_DIR is None:
        try:
            DATA_DIR = os.path.join(App.get_running_app().user_data_dir, "data")
        except:
            DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(filename):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── 颜色主题 ───
BG = get_color_from_hex("#0a0a1a")
CARD = get_color_from_hex("#12122a")
ACCENT = get_color_from_hex("#4fc3f7")
ACCENT_DIM = get_color_from_hex("#263238")
TEXT = (1, 1, 1, 1)
TEXT_DIM = get_color_from_hex("#546e7a")
DANGER = get_color_from_hex("#ef5350")
SUCCESS = get_color_from_hex("#66bb6a")

Window.clearcolor = BG

# ═══════════════════════════════════════════════
# SPLASH SCREEN（你的原始代码，微调适配）
# ═══════════════════════════════════════════════
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "splash"
        self.opacity = 0

        layout = BoxLayout(orientation="vertical", spacing=dp(10))

        self.logo = Label(
            text="JS",
            font_size=dp(42),
            color=ACCENT,
            size_hint=(1, 0.55),
            halign="center",
            valign="middle",
        )
        self.en = Label(
            text="JS STUDIO",
            font_size=dp(14),
            color=get_color_from_hex("#546e7a"),
            size_hint=(1, 0.15),
            halign="center",
        )
        self.foot = Label(
            text="Your world, your rules",
            font_size=dp(12),
            color=get_color_from_hex("#37474f"),
            size_hint=(1, 0.15),
            halign="center",
            opacity=0,
        )

        layout.add_widget(self.logo)
        layout.add_widget(self.en)
        layout.add_widget(self.foot)
        self.add_widget(layout)

        Clock.schedule_once(self.step1, 0.2)

    def step1(self, dt):
        Animation(opacity=1, duration=0.7).start(self)
        self.logo.font_size = dp(55)
        Animation(font_size=dp(42), duration=0.8, t="out_bounce").start(self.logo)
        Clock.schedule_once(self.step2, 1.0)

    def step2(self, dt):
        Animation(opacity=1, duration=0.6).start(self.foot)
        Clock.schedule_once(self.step3, 2.0)

    def step3(self, dt):
        anim = Animation(opacity=0, duration=0.6)
        anim.bind(on_complete=lambda *a: self._switch_to_main())
        anim.start(self)

    def _switch_to_main(self):
        if self.manager:
            self.manager.current = 'home'

# ═══════════════════════════════════════════════
# HOME SCREEN
# ═══════════════════════════════════════════════
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"

        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(20))

        # 顶部标题
        title = Label(
            text="JS STUDIO",
            font_size=dp(28),
            color=ACCENT,
            size_hint=(1, 0.15),
            halign="center",
        )
        root.add_widget(title)

        # 卡片容器
        cards = BoxLayout(orientation="vertical", spacing=dp(16), size_hint=(1, 0.7))

        for name, target in [("MEMO", "memo"), ("DIARY", "diary"), ("VAULT", "vault")]:
            btn = Button(
                text=name,
                font_size=dp(20),
                background_color=CARD,
                color=TEXT,
                size_hint=(1, None),
                height=dp(70),
                on_press=lambda x, t=target: self.go_to(t),
            )
            btn.bind(on_press=lambda x, t=target: None)
            cards.add_widget(btn)

        root.add_widget(cards)
        root.add_widget(Label(text="", size_hint=(1, 0.15)))
        self.add_widget(root)

    def go_to(self, screen_name):
        self.manager.current = screen_name

# ═══════════════════════════════════════════════
# MEMO SCREEN
# ═══════════════════════════════════════════════
class MemoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "memo"
        self.memos = load_json("memos.json") if self._loaded() else []

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        header = Label(text="MEMO", font_size=dp(24), color=ACCENT, size_hint=(1, 0.1))
        root.add_widget(header)

        self.scroll = ScrollView(size_hint=(1, 0.75))
        self.list_layout = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        root.add_widget(self.scroll)

        add_btn = Button(
            text="+ NEW MEMO",
            font_size=dp(16),
            background_color=ACCENT,
            color=BG,
            size_hint=(1, 0.1),
            on_press=self.add_memo,
        )
        root.add_widget(add_btn)

        self.add_widget(root)
        self.refresh()

    def _loaded(self):
        ensure_data_dir()
        return os.path.exists(os.path.join(DATA_DIR, "memos.json"))

    def refresh(self):
        self.list_layout.clear_widgets()
        for i, memo in enumerate(self.memos):
            item = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                spacing=dp(8),
            )
            # 勾选
            check = Button(
                text="✓" if memo.get("done") else "○",
                size_hint=(None, 1),
                width=dp(40),
                background_color=SUCCESS if memo.get("done") else ACCENT_DIM,
                color=TEXT,
                on_press=lambda x, idx=i: self.toggle_done(idx),
            )
            # 内容
            text = memo.get("text", "")[:30]
            if memo.get("done"):
                text = f"[s]{text}[/s]"
            lbl = Label(
                text=text,
                color=TEXT_DIM if memo.get("done") else TEXT,
                size_hint=(1, 1),
                halign="left",
                valign="middle",
            )
            lbl.bind(size=lbl.setter('text_size'))
            # 删除
            delete = Button(
                text="✕",
                size_hint=(None, 1),
                width=dp(40),
                background_color=DANGER,
                color=TEXT,
                on_press=lambda x, idx=i: self.delete_memo(idx),
            )
            item.add_widget(check)
            item.add_widget(lbl)
            item.add_widget(delete)
            self.list_layout.add_widget(item)

    def add_memo(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        ti = TextInput(
            hint_text="Type your memo...",
            multiline=True,
            background_color=(0.1, 0.1, 0.15, 1),
            foreground_color=TEXT,
            hint_text_color=TEXT_DIM,
        )
        btn = Button(text="SAVE", background_color=ACCENT, color=BG)
        content.add_widget(ti)
        content.add_widget(btn)

        popup = Popup(title="New Memo", content=content, size_hint=(0.85, 0.5))
        btn.bind(on_press=lambda x: self._save_new(ti.text, popup))
        popup.open()

    def _save_new(self, text, popup):
        if text.strip():
            self.memos.append({
                "text": text.strip(),
                "done": False,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            save_json("memos.json", self.memos)
            self.refresh()
        popup.dismiss()

    def toggle_done(self, idx):
        self.memos[idx]["done"] = not self.memos[idx].get("done", False)
        save_json("memos.json", self.memos)
        self.refresh()

    def delete_memo(self, idx):
        self.memos.pop(idx)
        save_json("memos.json", self.memos)
        self.refresh()

# ═══════════════════════════════════════════════
# DIARY SCREEN
# ═══════════════════════════════════════════════
class DiaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "diary"
        self.entries = load_json("diary.json") if self._loaded() else {}

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        header = Label(text="DIARY", font_size=dp(24), color=ACCENT, size_hint=(1, 0.1))
        root.add_widget(header)

        today = str(date.today())
        self.today_label = Label(
            text=f"Today: {today}",
            font_size=dp(14),
            color=TEXT_DIM,
            size_hint=(1, 0.08),
        )
        root.add_widget(self.today_label)

        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.content_area = BoxLayout(orientation="vertical", spacing=dp(8))
        self.scroll.add_widget(self.content_area)
        root.add_widget(self.scroll)

        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=dp(10))
        self.write_btn = Button(
            text="WRITE TODAY" if today not in self.entries else "EDIT TODAY",
            background_color=ACCENT,
            color=BG,
            font_size=dp(16),
            on_press=self.write_today,
        )
        self.history_btn = Button(
            text="HISTORY",
            background_color=CARD,
            color=TEXT,
            font_size=dp(16),
            on_press=self.show_history,
        )
        btn_layout.add_widget(self.write_btn)
        btn_layout.add_widget(self.history_btn)
        root.add_widget(btn_layout)

        self.add_widget(root)
        self.refresh()

    def _loaded(self):
        ensure_data_dir()
        return os.path.exists(os.path.join(DATA_DIR, "diary.json"))

    def refresh(self):
        self.content_area.clear_widgets()
        today = str(date.today())
        if today in self.entries:
            preview = self.entries[today][:100] + "..." if len(self.entries[today]) > 100 else self.entries[today]
            lbl = Label(
                text=preview,
                color=TEXT,
                size_hint_y=None,
                height=dp(80),
                halign="left",
                valign="top",
            )
            lbl.bind(size=lbl.setter('text_size'))
            self.content_area.add_widget(lbl)
        else:
            self.content_area.add_widget(Label(text="No entry today", color=TEXT_DIM))
        self.write_btn.text = "EDIT TODAY" if today in self.entries else "WRITE TODAY"

    def write_today(self, instance):
        today = str(date.today())
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        ti = TextInput(
            text=self.entries.get(today, ""),
            multiline=True,
            background_color=(0.1, 0.1, 0.15, 1),
            foreground_color=TEXT,
            hint_text_color=TEXT_DIM,
            hint_text="Write your day...",
        )
        btn = Button(text="SAVE", background_color=ACCENT, color=BG)
        content.add_widget(ti)
        content.add_widget(btn)

        popup = Popup(title=today, content=content, size_hint=(0.9, 0.7))
        btn.bind(on_press=lambda x: self._save_entry(today, ti.text, popup))
        popup.open()

    def _save_entry(self, day, text, popup):
        if text.strip():
            self.entries[day] = text.strip()
            save_json("diary.json", self.entries)
            self.refresh()
        popup.dismiss()

    def show_history(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(5))
        scroll = ScrollView()
        layout = BoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for day in sorted(self.entries.keys(), reverse=True):
            preview = self.entries[day][:50] + "..."
            item = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
            item.add_widget(Label(text=day, color=ACCENT, size_hint=(0.35, 1)))
            item.add_widget(Label(text=preview, color=TEXT_DIM, size_hint=(0.65, 1), halign="left"))
            layout.add_widget(item)

        scroll.add_widget(layout)
        content.add_widget(scroll)
        close = Button(text="CLOSE", background_color=DANGER, color=TEXT, size_hint=(1, 0.15))
        popup = Popup(title="History", content=content, size_hint=(0.85, 0.7))
        close.bind(on_press=popup.dismiss)
        content.add_widget(close)
        popup.open()

# ═══════════════════════════════════════════════
# VAULT SCREEN
# ═══════════════════════════════════════════════
class VaultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "vault"
        self.unlocked = False
        self.config = load_json("config.json") if self._loaded_config() else {}
        self.items = load_json("vault.json") if self._loaded_items() else []

        self.root_layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        self.add_widget(self.root_layout)
        self.show_lock_screen()

    def _loaded_config(self):
        ensure_data_dir()
        return os.path.exists(os.path.join(DATA_DIR, "config.json"))

    def _loaded_items(self):
        ensure_data_dir()
        return os.path.exists(os.path.join(DATA_DIR, "vault.json"))

    def clear_root(self):
        self.root_layout.clear_widgets()

    def show_lock_screen(self):
        self.clear_root()
        self.unlocked = False

        content = BoxLayout(orientation="vertical", spacing=dp(15), padding=dp(20))

        title = Label(text="🔒 VAULT LOCKED", font_size=dp(22), color=ACCENT, size_hint=(1, 0.2))
        content.add_widget(title)

        if self.config.get("has_password"):
            self.pw_input = TextInput(
                hint_text="Enter password",
                password=True,
                background_color=(0.1, 0.1, 0.15, 1),
                foreground_color=TEXT,
                hint_text_color=TEXT_DIM,
                size_hint=(1, 0.2),
            )
            content.add_widget(self.pw_input)
            unlock_btn = Button(text="UNLOCK", background_color=ACCENT, color=BG, size_hint=(1, 0.15))
            unlock_btn.bind(on_press=self.unlock)
            content.add_widget(unlock_btn)
        else:
            self.pw_input = TextInput(
                hint_text="Set new password (min 4 chars)",
                password=True,
                background_color=(0.1, 0.1, 0.15, 1),
                foreground_color=TEXT,
                hint_text_color=TEXT_DIM,
                size_hint=(1, 0.2),
            )
            self.pw_confirm = TextInput(
                hint_text="Confirm password",
                password=True,
                background_color=(0.1, 0.1, 0.15, 1),
                foreground_color=TEXT,
                hint_text_color=TEXT_DIM,
                size_hint=(1, 0.2),
            )
            content.add_widget(self.pw_input)
            content.add_widget(self.pw_confirm)
            set_btn = Button(text="SET PASSWORD", background_color=SUCCESS, color=BG, size_hint=(1, 0.15))
            set_btn.bind(on_press=self.set_password)
            content.add_widget(set_btn)

        self.root_layout.add_widget(content)

    def set_password(self, instance):
        pw1 = self.pw_input.text
        pw2 = self.pw_confirm.text
        if pw1 != pw2:
            self._show_msg("Passwords don't match")
            return
        if len(pw1) < 4:
            self._show_msg("Password too short")
            return
        self.config["has_password"] = True
        self.config["hash"] = hashlib.sha256(pw1.encode()).hexdigest()
        save_json("config.json", self.config)
        self._show_msg("Password set!")
        Clock.schedule_once(lambda dt: self.show_vault(), 0.5)

    def unlock(self, instance):
        pw = self.pw_input.text
        if hashlib.sha256(pw.encode()).hexdigest() == self.config.get("hash"):
            self.show_vault()
        else:
            self._show_msg("Wrong password")

    def show_vault(self):
        self.clear_root()
        self.unlocked = True

        header = Label(text="VAULT", font_size=dp(24), color=ACCENT, size_hint=(1, 0.08))
        self.root_layout.add_widget(header)

        lock_btn = Button(
            text="🔒 LOCK",
            background_color=DANGER,
            color=TEXT,
            size_hint=(1, 0.08),
            on_press=lambda x: self.show_lock_screen(),
        )
        self.root_layout.add_widget(lock_btn)

        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.list_layout = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        self.root_layout.add_widget(self.scroll)

        add_btn = Button(
            text="+ ADD ENTRY",
            background_color=ACCENT,
            color=BG,
            size_hint=(1, 0.1),
            on_press=self.add_entry,
        )
        self.root_layout.add_widget(add_btn)
        self.refresh()

    def refresh(self):
        self.list_layout.clear_widgets()
        for i, item in enumerate(self.items):
            box = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                spacing=dp(5),
            )
            title_lbl = Label(text=item.get("title", ""), color=TEXT, size_hint=(0.4, 1), halign="left")
            pwd_lbl = Label(text="••••••", color=TEXT_DIM, size_hint=(0.3, 1))
            view_btn = Button(text="👁", size_hint=(0.15, 1), background_color=CARD, color=TEXT,
                             on_press=lambda x, idx=i: self.view_entry(idx))
            del_btn = Button(text="✕", size_hint=(0.15, 1), background_color=DANGER, color=TEXT,
                            on_press=lambda x, idx=i: self.delete_entry(idx))
            box.add_widget(title_lbl)
            box.add_widget(pwd_lbl)
            box.add_widget(view_btn)
            box.add_widget(del_btn)
            self.list_layout.add_widget(box)

    def add_entry(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        title_in = TextInput(hint_text="Title", background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        user_in = TextInput(hint_text="Username/Email", background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        pwd_in = TextInput(hint_text="Password", password=True, background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        note_in = TextInput(hint_text="Note", background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        btn = Button(text="SAVE", background_color=ACCENT, color=BG)

        content.add_widget(title_in)
        content.add_widget(user_in)
        content.add_widget(pwd_in)
        content.add_widget(note_in)
        content.add_widget(btn)

        popup = Popup(title="New Vault Entry", content=content, size_hint=(0.85, 0.7))
        btn.bind(on_press=lambda x: self._save_entry(title_in.text, user_in.text, pwd_in.text, note_in.text, popup))
        popup.open()

    def _save_entry(self, title, user, pwd, note, popup):
        if title.strip() and pwd.strip():
            self.items.append({"title": title, "user": user, "password": pwd, "note": note})
            save_json("vault.json", self.items)
            self.refresh()
        popup.dismiss()

    def view_entry(self, idx):
        item = self.items[idx]
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text=f"Title: {item.get('title','')}", color=TEXT))
        content.add_widget(Label(text=f"User: {item.get('user','')}", color=TEXT))
        content.add_widget(Label(text=f"Password: {item.get('password','')}", color=ACCENT))
        content.add_widget(Label(text=f"Note: {item.get('note','')}", color=TEXT_DIM))
        close = Button(text="CLOSE", background_color=CARD, color=TEXT)
        popup = Popup(title="Details", content=content, size_hint=(0.8, 0.5))
        close.bind(on_press=popup.dismiss)
        content.add_widget(close)
        popup.open()

    def delete_entry(self, idx):
        self.items.pop(idx)
        save_json("vault.json", self.items)
        self.refresh()

    def _show_msg(self, msg):
        popup = Popup(title="", content=Label(text=msg), size_hint=(0.6, 0.3))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

# ═══════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════
class JSStudioApp(App):
    def build(self):
        self.title = "JS Studio"
        sm = ScreenManager()
        sm.add_widget(SplashScreen())
        sm.add_widget(HomeScreen())
        sm.add_widget(MemoScreen())
        sm.add_widget(DiaryScreen())
        sm.add_widget(VaultScreen())
        sm.current = "splash"
        return sm

    def on_start(self):
        # 确保数据目录在app启动时就创建
        ensure_data_dir()

    def on_back_pressed(self):
        sm = self.root
        if sm.current == "home":
            return False  # 退出app
        elif sm.current == "splash":
            return False
        else:
            sm.current = "home"
            return True

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # ESC / 返回键
            return self.on_back_pressed()
        return False

if __name__ == "__main__":
    JSStudioApp().run()
