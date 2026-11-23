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
from datetime import datetime, date

# ─── 颜色 ───
BG = get_color_from_hex("#0a0a1a")
CARD = get_color_from_hex("#12122a")
ACCENT = get_color_from_hex("#4fc3f7")
ACCENT_DIM = get_color_from_hex("#263238")
TEXT = (1, 1, 1, 1)
TEXT_DIM = get_color_from_hex("#546e7a")
DANGER = get_color_from_hex("#ef5350")
SUCCESS = get_color_from_hex("#66bb6a")
Window.clearcolor = BG

# ─── 数据存储 ───
DATA_DIR = None

def get_dir():
    global DATA_DIR
    if DATA_DIR is None:
        try:
            DATA_DIR = os.path.join(App.get_running_app().user_data_dir, "data")
        except Exception:
            DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(DATA_DIR, exist_ok=True)
    return DATA_DIR

def load_json(name):
    path = os.path.join(get_dir(), name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_json(name, data):
    path = os.path.join(get_dir(), name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ═══════════════════════════════════════════
# SPLASH
# ═══════════════════════════════════════════
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
                          color=get_color_from_hex("#37474f"), size_hint=(1, 0.15),
                          halign="center", opacity=0)
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
        anim.bind(on_complete=lambda *a: self._go())
        anim.start(self)

    def _go(self):
        if self.manager:
            self.manager.current = "home"

# ═══════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(20))
        root.add_widget(Label(text="JS STUDIO", font_size=dp(28), color=ACCENT,
                              size_hint=(1, 0.15), halign="center"))
        cards = BoxLayout(orientation="vertical", spacing=dp(16), size_hint=(1, 0.7))
        for name, target in [("MEMO", "memo"), ("DIARY", "diary"), ("VAULT", "vault")]:
            btn = Button(text=name, font_size=dp(20), background_color=CARD, color=TEXT,
                         size_hint=(1, None), height=dp(70))
            btn.bind(on_press=lambda x, t=target: setattr(self.manager, "current", t))
            cards.add_widget(btn)
        root.add_widget(cards)
        root.add_widget(Label(text="", size_hint=(1, 0.15)))
        self.add_widget(root)

# ═══════════════════════════════════════════
# MEMO
# ═══════════════════════════════════════════
class MemoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "memo"
        self.memos = load_json("memos.json") or []
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(Label(text="MEMO", font_size=dp(24), color=ACCENT, size_hint=(1, 0.1)))
        self.scroll = ScrollView(size_hint=(1, 0.75))
        self.box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        root.add_widget(self.scroll)
        root.add_widget(Button(text="+ NEW MEMO", font_size=dp(16), background_color=ACCENT, color=BG,
                               size_hint=(1, 0.1), on_press=self.add_memo))
        self.add_widget(root)
        self.refresh()

    def refresh(self):
        self.box.clear_widgets()
        for i, m in enumerate(self.memos):
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
            row.add_widget(Button(text="✓" if m.get("done") else "○", size_hint=(None, 1), width=dp(40),
                                  background_color=SUCCESS if m.get("done") else ACCENT_DIM,
                                  on_press=lambda x, idx=i: self.toggle(idx)))
            lbl = Label(text=m.get("text", "")[:35], color=TEXT_DIM if m.get("done") else TEXT,
                        size_hint=(1, 1), halign="left")
            lbl.bind(size=lbl.setter("text_size"))
            row.add_widget(lbl)
            row.add_widget(Button(text="✕", size_hint=(None, 1), width=dp(40), background_color=DANGER,
                                  on_press=lambda x, idx=i: self.delete(idx)))
            self.box.add_widget(row)

    def add_memo(self, instance):
        ti = TextInput(hint_text="Type your memo...", multiline=True,
                       background_color=(0.1, 0.1, 0.15, 1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        popup = Popup(title="New Memo", content=ti, size_hint=(0.85, 0.4))
        popup.content = BoxLayout(orientation="vertical", spacing=dp(10))
        popup.content.add_widget(ti)
        btn = Button(text="SAVE", background_color=ACCENT, color=BG)
        popup.content.add_widget(btn)
        btn.bind(on_press=lambda x: self._save(ti.text, popup))
        popup.open()

    def _save(self, text, popup):
        if text.strip():
            self.memos.append({"text": text.strip(), "done": False})
            save_json("memos.json", self.memos)
            self.refresh()
        popup.dismiss()

    def toggle(self, idx):
        self.memos[idx]["done"] = not self.memos[idx].get("done", False)
        save_json("memos.json", self.memos)
        self.refresh()

    def delete(self, idx):
        self.memos.pop(idx)
        save_json("memos.json", self.memos)
        self.refresh()

# ═══════════════════════════════════════════
# DIARY
# ═══════════════════════════════════════════
class DiaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "diary"
        self.entries = load_json("diary.json") or {}
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(Label(text="DIARY", font_size=dp(24), color=ACCENT, size_hint=(1, 0.1)))
        root.add_widget(Label(text=str(date.today()), font_size=dp(14), color=TEXT_DIM, size_hint=(1, 0.08)))
        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.box = BoxLayout(orientation="vertical", spacing=dp(8))
        self.scroll.add_widget(self.box)
        root.add_widget(self.scroll)
        btns = BoxLayout(size_hint=(1, 0.15), spacing=dp(10))
        self.wbtn = Button(text="EDIT TODAY" if str(date.today()) in self.entries else "WRITE TODAY",
                           background_color=ACCENT, color=BG, on_press=self.write_today)
        btns.add_widget(self.wbtn)
        btns.add_widget(Button(text="HISTORY", background_color=CARD, color=TEXT, on_press=self.history))
        root.add_widget(btns)
        self.add_widget(root)
        self.refresh()

    def refresh(self):
        self.box.clear_widgets()
        today = str(date.today())
        txt = self.entries.get(today, "No entry today")
        lbl = Label(text=txt[:120] + ("..." if len(txt) > 120 else ""), color=TEXT,
                    size_hint_y=None, height=dp(80), halign="left", valign="top")
        lbl.bind(size=lbl.setter("text_size"))
        self.box.add_widget(lbl)
        self.wbtn.text = "EDIT TODAY" if today in self.entries else "WRITE TODAY"

    def write_today(self, instance):
        today = str(date.today())
        ti = TextInput(text=self.entries.get(today, ""), multiline=True,
                       background_color=(0.1, 0.1, 0.15, 1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        popup = Popup(title=today, content=BoxLayout(orientation="vertical", spacing=dp(10)), size_hint=(0.9, 0.7))
        popup.content.add_widget(ti)
        btn = Button(text="SAVE", background_color=ACCENT, color=BG)
        popup.content.add_widget(btn)
        btn.bind(on_press=lambda x: self._save(today, ti.text, popup))
        popup.open()

    def _save(self, day, text, popup):
        if text.strip():
            self.entries[day] = text.strip()
            save_json("diary.json", self.entries)
            self.refresh()
        popup.dismiss()

    def history(self, instance):
        box = BoxLayout(orientation="vertical", spacing=dp(5))
        sc = ScrollView()
        lay = BoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None)
        lay.bind(minimum_height=lay.setter("height"))
        for d in sorted(self.entries.keys(), reverse=True):
            row = BoxLayout(size_hint_y=None, height=dp(40))
            row.add_widget(Label(text=d, color=ACCENT, size_hint=(0.35, 1)))
            row.add_widget(Label(text=self.entries[d][:40], color=TEXT_DIM, size_hint=(0.65, 1), halign="left"))
            lay.add_widget(row)
        sc.add_widget(lay)
        box.add_widget(sc)
        close = Button(text="CLOSE", background_color=DANGER, color=TEXT, size_hint=(1, 0.15))
        popup = Popup(title="History", content=box, size_hint=(0.85, 0.7))
        close.bind(on_press=popup.dismiss)
        box.add_widget(close)
        popup.open()

# ═══════════════════════════════════════════
# VAULT
# ═══════════════════════════════════════════
class VaultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "vault"
        self.unlocked = False
        self.cfg = load_json("config.json") or {}
        self.items = load_json("vault.json") or []
        self.root_lay = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        self.add_widget(self.root_lay)
        self.show_lock()

    def clear(self):
        self.root_lay.clear_widgets()

    def show_lock(self):
        self.clear()
        self.unlocked = False
        self.root_lay.add_widget(Label(text="🔒 VAULT LOCKED", font_size=dp(22), color=ACCENT, size_hint=(1, 0.2)))
        if self.cfg.get("hash"):
            self.pw = TextInput(hint_text="Enter password", password=True,
                                background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
            self.root_lay.add_widget(self.pw)
            btn = Button(text="UNLOCK", background_color=ACCENT, color=BG, size_hint=(1, 0.15))
            btn.bind(on_press=self.unlock)
            self.root_lay.add_widget(btn)
        else:
            self.pw = TextInput(hint_text="Set password (min 4)", password=True,
                                background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
            self.pw2 = TextInput(hint_text="Confirm", password=True,
                                 background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
            self.root_lay.add_widget(self.pw)
            self.root_lay.add_widget(self.pw2)
            btn = Button(text="SET PASSWORD", background_color=SUCCESS, color=BG, size_hint=(1, 0.15))
            btn.bind(on_press=self.set_pw)
            self.root_lay.add_widget(btn)

    def set_pw(self, instance):
        if self.pw.text != self.pw2.text:
            return self.msg("No match")
        if len(self.pw.text) < 4:
            return self.msg("Too short")
        self.cfg["hash"] = hashlib.sha256(self.pw.text.encode()).hexdigest()
        save_json("config.json", self.cfg)
        Clock.schedule_once(lambda dt: self.show_vault(), 0.3)

    def unlock(self, instance):
        if hashlib.sha256(self.pw.text.encode()).hexdigest() == self.cfg.get("hash"):
            self.show_vault()
        else:
            self.msg("Wrong")

    def show_vault(self):
        self.clear()
        self.unlocked = True
        self.root_lay.add_widget(Label(text="VAULT", font_size=dp(24), color=ACCENT, size_hint=(1, 0.08)))
        self.root_lay.add_widget(Button(text="🔒 LOCK", background_color=DANGER, color=TEXT,
                                        size_hint=(1, 0.08), on_press=lambda x: self.show_lock()))
        sc = ScrollView(size_hint=(1, 0.7))
        self.vbox = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.vbox.bind(minimum_height=self.vbox.setter("height"))
        sc.add_widget(self.vbox)
        self.root_lay.add_widget(sc)
        self.root_lay.add_widget(Button(text="+ ADD ENTRY", background_color=ACCENT, color=BG,
                                        size_hint=(1, 0.1), on_press=self.add_entry))
        self.refresh()

    def refresh(self):
        self.vbox.clear_widgets()
        for i, it in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
            row.add_widget(Label(text=it.get("title",""), color=TEXT, size_hint=(0.4,1), halign="left"))
            row.add_widget(Label(text="••••", color=TEXT_DIM, size_hint=(0.3,1)))
            row.add_widget(Button(text="👁", size_hint=(0.15,1), background_color=CARD, on_press=lambda x,idx=i: self.view(idx)))
            row.add_widget(Button(text="✕", size_hint=(0.15,1), background_color=DANGER, on_press=lambda x,idx=i: self.delete(idx)))
            self.vbox.add_widget(row)

    def add_entry(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(8))
        t = TextInput(hint_text="Title", background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        u = TextInput(hint_text="Username", background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        p = TextInput(hint_text="Password", password=True, background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        n = TextInput(hint_text="Note", background_color=(0.1,0.1,0.15,1), foreground_color=TEXT, hint_text_color=TEXT_DIM)
        content.add_widget(t); content.add_widget(u); content.add_widget(p); content.add_widget(n)
        popup = Popup(title="New Entry", content=content, size_hint=(0.85, 0.7))
        btn = Button(text="SAVE", background_color=ACCENT, color=BG)
        content.add_widget(btn)
        btn.bind(on_press=lambda x: self._save(t.text,u.text,p.text,n.text,popup))
        popup.open()

    def _save(self, title, user, pwd, note, popup):
        if title.strip() and pwd.strip():
            self.items.append({"title":title,"user":user,"password":pwd,"note":note})
            save_json("vault.json", self.items)
            self.refresh()
        popup.dismiss()

    def view(self, idx):
        it = self.items[idx]
        box = BoxLayout(orientation="vertical", spacing=dp(10))
        for k in ["title","user","password","note"]:
            box.add_widget(Label(text=f"{k.upper()}: {it.get(k,'')}", color=ACCENT if k=="password" else TEXT))
        popup = Popup(title="Details", content=box, size_hint=(0.8, 0.5))
        close = Button(text="CLOSE", background_color=CARD, color=TEXT)
        close.bind(on_press=popup.dismiss)
        box.add_widget(close)
        popup.open()

    def delete(self, idx):
        self.items.pop(idx)
        save_json("vault.json", self.items)
        self.refresh()

    def msg(self, text):
        popup = Popup(content=Label(text=text), size_hint=(0.5, 0.3))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.2)

# ═══════════════════════════════════════════
# APP
# ═══════════════════════════════════════════
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
        get_dir()

    def on_keyboard(self, window, key, *args):
        if key == 27:
            sm = self.root
            if sm.current in ("home", "splash"):
                return False
            sm.current = "home"
            return True
        return False

if __name__ == "__main__":
    JSStudioApp().run()
