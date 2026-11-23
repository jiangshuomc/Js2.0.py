"""JS Studio - Memo / Diary / Vault
Single-file Kivy application. Android only, English UI, local JSON storage.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.core.window import Window

import os
import json
import hashlib
from datetime import date

# ---------------- Theme ----------------
BG         = get_color_from_hex("#0a0a1a")
CARD       = get_color_from_hex("#12122a")
ACCENT     = get_color_from_hex("#4fc3f7")
ACCENT_DIM = get_color_from_hex("#263238")
TEXT       = (1, 1, 1, 1)
TEXT_DIM   = get_color_from_hex("#546e7a")
DANGER     = get_color_from_hex("#ef5350")
SUCCESS    = get_color_from_hex("#66bb6a")
INPUT_BG   = (0.10, 0.10, 0.15, 1)

Window.clearcolor = BG


# ---------------- Storage ----------------
def get_data_dir():
    """App-private directory. Works on desktop and Android."""
    try:
        base = App.get_running_app().user_data_dir
    except Exception:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "data")
    os.makedirs(path, exist_ok=True)
    return path


def load_json(filename, default):
    path = os.path.join(get_data_dir(), filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (ValueError, OSError):
            return default
    return default


def save_json(filename, data):
    path = os.path.join(get_data_dir(), filename)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def make_field(hint, multiline=False, password=False):
    return TextInput(
        hint_text=hint,
        multiline=multiline,
        password=password,
        background_color=INPUT_BG,
        foreground_color=TEXT,
        hint_text_color=TEXT_DIM,
        cursor_color=ACCENT,
        padding=(dp(10), dp(10)),
        size_hint=(1, None),
        height=dp(84) if multiline else dp(44),
    )


def popup_with(title, content_widgets, height=0.6):
    box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
    for w in content_widgets:
        box.add_widget(w)
    return Popup(title=title, content=box, size_hint=(0.9, height))


# ---------------- Splash ----------------
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "splash"
        self.opacity = 0

        layout = BoxLayout(orientation="vertical", spacing=dp(10))
        self.logo = Label(text="JS", font_size=dp(42), color=ACCENT,
                          size_hint=(1, 0.55), halign="center", valign="middle")
        self.en = Label(text="JS STUDIO", font_size=dp(14), color=TEXT_DIM,
                        size_hint=(1, 0.15), halign="center")
        self.foot = Label(text="Your world, your rules", font_size=dp(12),
                          color=get_color_from_hex("#37474f"),
                          size_hint=(1, 0.15), halign="center", opacity=0)
        layout.add_widget(self.logo)
        layout.add_widget(self.en)
        layout.add_widget(self.foot)
        self.add_widget(layout)

        Clock.schedule_once(self._step1, 0.2)

    def _step1(self, dt):
        Animation(opacity=1, duration=0.7).start(self)
        self.logo.font_size = dp(55)
        Animation(font_size=dp(42), duration=0.8, t="out_bounce").start(self.logo)
        Clock.schedule_once(self._step2, 1.0)

    def _step2(self, dt):
        Animation(opacity=1, duration=0.6).start(self.foot)
        Clock.schedule_once(self._step3, 2.0)

    def _step3(self, dt):
        anim = Animation(opacity=0, duration=0.6)
        anim.bind(on_complete=lambda *a: self._switch())
        anim.start(self)

    def _switch(self):
        if self.manager:
            self.manager.current = "home"


# ---------------- Home ----------------
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"

        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(20))
        root.add_widget(Label(text="JS STUDIO", font_size=dp(28), color=ACCENT,
                              size_hint=(1, 0.12), halign="center"))
        root.add_widget(Label(text="Your world, your rules", font_size=dp(12),
                              color=TEXT_DIM, size_hint=(1, 0.06), halign="center"))

        cards = BoxLayout(orientation="vertical", spacing=dp(14), size_hint=(1, 0.7))
        for label, target in (("MEMO", "memo"), ("DIARY", "diary"), ("VAULT", "vault")):
            btn = Button(text=label, font_size=dp(20), background_color=CARD,
                         color=TEXT, size_hint=(1, None), height=dp(72))
            btn.bind(on_press=lambda inst, t=target: self._go(t))
            cards.add_widget(btn)
        root.add_widget(cards)
        root.add_widget(Label(text="", size_hint=(1, 0.12)))
        self.add_widget(root)

    def _go(self, target):
        if self.manager:
            self.manager.current = target


# ---------------- Memo ----------------
class MemoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "memo"
        self.memos = load_json("memos.json", [])

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(Label(text="MEMO", font_size=dp(24), color=ACCENT,
                              size_hint=(1, 0.08), halign="center"))

        scroller = ScrollView(size_hint=(1, 0.78))
        self.box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        scroller.add_widget(self.box)
        root.add_widget(scroller)

        add = Button(text="+ NEW MEMO", font_size=dp(16), background_color=ACCENT,
                     color=BG, size_hint=(1, 0.1))
        add.bind(on_press=self._ask_new)
        root.add_widget(add)
        self.add_widget(root)
        self._refresh()

    def _refresh(self):
        self.box.clear_widgets()
        if not self.memos:
            self.box.add_widget(Label(text="No memo yet", color=TEXT_DIM,
                                      size_hint_y=None, height=dp(40)))
            return
        for i, memo in enumerate(self.memos):
            row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
            done = memo.get("done", False)
            check = Button(text="DONE" if done else "OPEN", size_hint=(None, 1),
                           width=dp(64), font_size=dp(11),
                           background_color=SUCCESS if done else ACCENT_DIM, color=TEXT)
            check.bind(on_press=lambda inst, idx=i: self._toggle(idx))
            lbl = Label(text=str(memo.get("text", ""))[:36],
                        color=TEXT_DIM if done else TEXT,
                        size_hint=(1, 1), halign="left", valign="middle")
            lbl.bind(size=lbl.setter("text_size"))
            delete = Button(text="X", size_hint=(None, 1), width=dp(44),
                            background_color=DANGER, color=TEXT)
            delete.bind(on_press=lambda inst, idx=i: self._delete(idx))
            row.add_widget(check)
            row.add_widget(lbl)
            row.add_widget(delete)
            self.box.add_widget(row)

    def _ask_new(self, inst):
        ti = make_field("Type your memo...", multiline=True)
        save = Button(text="SAVE", background_color=ACCENT, color=BG)
        popup = popup_with("New Memo", [ti, save], height=0.45)
        save.bind(on_press=lambda i: self._save(ti.text, popup))
        popup.open()

    def _save(self, text, popup):
        if text.strip():
            self.memos.append({"text": text.strip(), "done": False})
            save_json("memos.json", self.memos)
            self._refresh()
        popup.dismiss()

    def _toggle(self, idx):
        if 0 <= idx < len(self.memos):
            self.memos[idx]["done"] = not self.memos[idx].get("done", False)
            save_json("memos.json", self.memos)
            self._refresh()

    def _delete(self, idx):
        if 0 <= idx < len(self.memos):
            self.memos.pop(idx)
            save_json("memos.json", self.memos)
            self._refresh()


# ---------------- Diary ----------------
class DiaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "diary"
        self.entries = load_json("diary.json", {})

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(Label(text="DIARY", font_size=dp(24), color=ACCENT,
                              size_hint=(1, 0.08), halign="center"))
        self.today = str(date.today())
        root.add_widget(Label(text=self.today, font_size=dp(13), color=TEXT_DIM,
                              size_hint=(1, 0.05), halign="center"))

        scroller = ScrollView(size_hint=(1, 0.62))
        self.box = BoxLayout(orientation="vertical", spacing=dp(8))
        scroller.add_widget(self.box)
        root.add_widget(scroller)

        actions = BoxLayout(size_hint=(1, 0.14), spacing=dp(10))
        self.write_btn = Button(text="WRITE", background_color=ACCENT, color=BG, font_size=dp(15))
        self.write_btn.bind(on_press=self._write)
        history = Button(text="HISTORY", background_color=CARD, color=TEXT, font_size=dp(15))
        history.bind(on_press=self._history)
        actions.add_widget(self.write_btn)
        actions.add_widget(history)
        root.add_widget(actions)
        self.add_widget(root)
        self._refresh()

    def _refresh(self):
        self.box.clear_widgets()
        today = str(date.today())
        text = self.entries.get(today)
        self.write_btn.text = "EDIT" if text else "WRITE"
        lbl = Label(text=(text if text else "No entry today."),
                    color=TEXT if text else TEXT_DIM, size_hint_y=None, height=dp(90),
                    halign="left", valign="top")
        lbl.bind(size=lbl.setter("text_size"))
        self.box.add_widget(lbl)

    def _write(self, inst):
        today = str(date.today())
        ti = make_field("Write your day...", multiline=True)
        ti.text = self.entries.get(today, "")
        save = Button(text="SAVE", background_color=ACCENT, color=BG)
        popup = popup_with(today, [ti, save], height=0.7)
        save.bind(on_press=lambda i: self._save(today, ti.text, popup))
        popup.open()

    def _save(self, day, text, popup):
        if text.strip():
            self.entries[day] = text.strip()
            save_json("diary.json", self.entries)
            self._refresh()
        popup.dismiss()

    def _history(self, inst):
        lay = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        lay.bind(minimum_height=lay.setter("height"))
        scroller = ScrollView()
        scroller.add_widget(lay)
        close = Button(text="CLOSE", background_color=DANGER, color=TEXT, size_hint=(1, 0.12))
        popup = popup_with("History", [scroller, close], height=0.75)

        if not self.entries:
            lay.add_widget(Label(text="No records", color=TEXT_DIM,
                                 size_hint_y=None, height=dp(36)))
        for day in sorted(self.entries.keys(), reverse=True):
            row = BoxLayout(size_hint_y=None, height=dp(38))
            row.add_widget(Label(text=day, color=ACCENT, size_hint=(0.3, 1)))
            preview = self.entries[day].replace("\n", " ")[:32]
            row.add_widget(Label(text=preview, color=TEXT_DIM,
                                 size_hint=(0.7, 1), halign="left"))
            lay.add_widget(row)
        close.bind(on_press=popup.dismiss)
        popup.open()


# ---------------- Vault ----------------
class VaultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "vault"
        self.unlocked = False
        self.cfg = load_json("config.json", {})
        self.items = load_json("vault.json", [])
        self.root_lay = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        self.add_widget(self.root_lay)
        self._show_lock()

    # -- lock / unlock --
    def _show_lock(self):
        self.unlocked = False
        self.root_lay.clear_widgets()
        self.root_lay.add_widget(Label(text="VAULT LOCKED", font_size=dp(22),
                                       color=ACCENT, size_hint=(1, 0.18)))
        self.pw = make_field("Enter password" if self.cfg.get("hash") else "Set password (min 4)")
        self.pw.password = True
        self.root_lay.add_widget(self.pw)

        if self.cfg.get("hash"):
            action = Button(text="UNLOCK", background_color=ACCENT, color=BG, size_hint=(1, 0.14))
            action.bind(on_press=self._unlock)
            self.root_lay.add_widget(action)
        else:
            self.pw2 = make_field("Confirm password")
            self.pw2.password = True
            self.root_lay.add_widget(self.pw2)
            action = Button(text="SET PASSWORD", background_color=SUCCESS, color=BG, size_hint=(1, 0.14))
            action.bind(on_press=self._set_password)
            self.root_lay.add_widget(action)

    def _set_password(self, inst):
        p1, p2 = self.pw.text, getattr(self, "pw2", self.pw).text
        if p1 != p2:
            return self._toast("Passwords do not match")
        if len(p1) < 4:
            return self._toast("Password too short")
        self.cfg["hash"] = hashlib.sha256(p1.encode("utf-8")).hexdigest()
        save_json("config.json", self.cfg)
        self.pw.text = ""
        self._toast("Password set")
        Clock.schedule_once(lambda dt: self._show_vault(), 0.6)

    def _unlock(self, inst):
        if hashlib.sha256(self.pw.text.encode("utf-8")).hexdigest() == self.cfg.get("hash"):
            self.pw.text = ""
            self._show_vault()
        else:
            self.pw.text = ""
            self._toast("Wrong password")

    # -- main --
    def _show_vault(self):
        self.unlocked = True
        self.root_lay.clear_widgets()
        self.root_lay.add_widget(Label(text="VAULT", font_size=dp(24), color=ACCENT,
                                       size_hint=(1, 0.07)))
        lock = Button(text="LOCK", background_color=DANGER, color=TEXT, size_hint=(1, 0.07))
        lock.bind(on_press=lambda inst: self._show_lock())
        self.root_lay.add_widget(lock)

        scroller = ScrollView(size_hint=(1, 0.72))
        self.box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        scroller.add_widget(self.box)
        self.root_lay.add_widget(scroller)

        add = Button(text="+ ADD ENTRY", background_color=ACCENT, color=BG, size_hint=(1, 0.1))
        add.bind(on_press=self._ask_new)
        self.root_lay.add_widget(add)
        self._refresh()

    def _refresh(self):
        self.box.clear_widgets()
        if not self.items:
            self.box.add_widget(Label(text="No entry yet", color=TEXT_DIM,
                                      size_hint_y=None, height=dp(40)))
            return
        for i, item in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(4))
            title = Label(text=str(item.get("title", ""))[:18], color=TEXT,
                          size_hint=(0.36, 1), halign="left")
            title.bind(size=title.setter("text_size"))
            view = Button(text="VIEW", size_hint=(0.22, 1), font_size=dp(11),
                          background_color=CARD, color=ACCENT)
            view.bind(on_press=lambda inst, idx=i: self._view(idx))
            delete = Button(text="X", size_hint=(0.14, 1), background_color=DANGER)
            delete.bind(on_press=lambda inst, idx=i: self._delete(idx))
            row.add_widget(title)
            row.add_widget(Label(text="******", color=TEXT_DIM, size_hint=(0.28, 1)))
            row.add_widget(view)
            row.add_widget(delete)
            self.box.add_widget(row)

    def _ask_new(self, inst):
        t = make_field("Title")
        u = make_field("Username / Email")
        p = make_field("Password", password=True)
        n = make_field("Note")
        save = Button(text="SAVE", background_color=ACCENT, color=BG)
        popup = popup_with("New Entry", [t, u, p, n, save], height=0.8)
        save.bind(on_press=lambda i: self._save(t.text, u.text, p.text, n.text, popup))
        popup.open()

    def _save(self, title, user, pwd, note, popup):
        if title.strip() and pwd.strip():
            self.items.append({"title": title.strip(), "user": user.strip(),
                               "password": pwd, "note": note.strip()})
            save_json("vault.json", self.items)
            self._refresh()
        popup.dismiss()

    def _view(self, idx):
        if not (0 <= idx < len(self.items)):
            return
        item = self.items[idx]
        widgets = [
            Label(text="TITLE: " + str(item.get("title", "")), color=TEXT, size_hint=(1, None), height=dp(30)),
            Label(text="USER: " + str(item.get("user", "")), color=TEXT, size_hint=(1, None), height=dp(30)),
            Label(text="PASSWORD: " + str(item.get("password", "")), color=ACCENT,
                  size_hint=(1, None), height=dp(30)),
            Label(text="NOTE: " + str(item.get("note", "")), color=TEXT_DIM,
                  size_hint=(1, None), height=dp(60)),
        ]
        close = Button(text="CLOSE", background_color=CARD, color=TEXT)
        popup = popup_with("Details", widgets + [close], height=0.5)
        close.bind(on_press=popup.dismiss)
        popup.open()

    def _delete(self, idx):
        if 0 <= idx < len(self.items):
            self.items.pop(idx)
            save_json("vault.json", self.items)
            self._refresh()

    @staticmethod
    def _toast(msg):
        popup = Popup(content=Label(text=msg), size_hint=(0.55, 0.25))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.2)


# ---------------- App ----------------
class JSStudioApp(App):
    def build(self):
        self.title = "JS Studio"
        Window.bind(on_keyboard=self._on_key)
        sm = ScreenManager()
        sm.add_widget(SplashScreen())
        sm.add_widget(HomeScreen())
        sm.add_widget(MemoScreen())
        sm.add_widget(DiaryScreen())
        sm.add_widget(VaultScreen())
        sm.current = "splash"
        return sm

    def on_start(self):
        get_data_dir()

    def _on_key(self, window, key, *args):
        # Android BACK key == ESC (27)
        if key == 27:
            sm = self.root
            if sm is None or sm.current in ("splash", "home"):
                return False
            if sm.current == "vault" and sm.get_screen("vault").unlocked:
                sm.get_screen("vault")._show_lock()
                return True
            sm.current = "home"
            return True
        return False


if __name__ == "__main__":
    JSStudioApp().run()
