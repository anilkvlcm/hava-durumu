import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk

API_KEY = "2f419e4bdc487cb031f981306a829c44"
DB_PATH = "world.sqlite3"


def setup_user_table():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            location TEXT NOT NULL,
            temperature INTEGER,
            description TEXT,
            datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


current_user = None

def kayit_ekrani():
    def kaydol():
        user = entry_user.get()
        pwd = entry_pass.get()
        if user and pwd:
            try:
                conn = sqlite3.connect("users.db")
                cur = conn.cursor()
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
                conn.commit()
                conn.close()
                messagebox.showinfo("Kayıt", "Kayıt başarılı!")
                win.destroy()
                giris_ekrani()
            except sqlite3.IntegrityError:
                messagebox.showerror("Hata", "Bu kullanıcı adı zaten var.")
        else:
            messagebox.showwarning("Uyarı", "Tüm alanları doldurun.")

    win = tk.Tk()
    win.title("Kayıt Ol")
    win.geometry("300x200")
    tk.Label(win, text="Kullanıcı Adı").pack()
    entry_user = tk.Entry(win)
    entry_user.pack()
    tk.Label(win, text="Şifre").pack()
    entry_pass = tk.Entry(win, show="*")
    entry_pass.pack()
    tk.Button(win, text="Kaydol", command=kaydol).pack(pady=10)
    win.mainloop()


def giris_ekrani():
    def giris():
        global current_user
        user = entry_user.get()
        pwd = entry_pass.get()
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user, pwd))
        if cur.fetchone():
            current_user = user
            conn.close()
            win.destroy()
            hava_durumu_ekrani()
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı")
            conn.close()

    def kayit_git():
        win.destroy()
        kayit_ekrani()

    win = tk.Tk()
    win.title("Giriş Yap")
    win.geometry("300x200")
    tk.Label(win, text="Kullanıcı Adı").pack()
    entry_user = tk.Entry(win)
    entry_user.pack()
    tk.Label(win, text="Şifre").pack()
    entry_pass = tk.Entry(win, show="*")
    entry_pass.pack()
    tk.Button(win, text="Giriş", command=giris).pack(pady=5)
    tk.Button(win, text="Kayıt Ol", command=kayit_git).pack()
    win.mainloop()


def get_countries():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM countries ORDER BY name")
    countries = [row[0] for row in cur.fetchall()]
    conn.close()
    return countries


def get_states(country_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT s.name FROM states s
        JOIN countries c ON s.country_id = c.id
        WHERE c.name = ? ORDER BY s.name
    """, (country_name,))
    states = [row[0] for row in cur.fetchall()]
    conn.close()
    return states


def get_cities(state_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name FROM cities c
        JOIN states s ON c.state_id = s.id
        WHERE s.name = ? ORDER BY c.name
    """, (state_name,))
    cities = [row[0] for row in cur.fetchall()]
    conn.close()
    return cities


def weather_get(location):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {'q': location, 'appid': API_KEY, 'lang': 'tr'}
    data = requests.get(url, params=params).json()
    if data.get('cod') != 200:
        return None
    return {
        'name': data['name'],
        'country': data['sys']['country'],
        'temp': round(data['main']['temp'] - 273.15),
        'description': data['weather'][0]['description'],
        'icon': data['weather'][0]['icon']
    }


def hava_durumu_ekrani():
    bg_color = "#d0e7f9"
    win = tk.Tk()
    win.title("Hava Durumu Uygulaması")
    win.geometry("500x600")
    win.configure(bg=bg_color)

    def ulke_secildi(event):
        states = get_states(ulke_var.get())
        combo_eyalet['values'] = states
        eyalet_var.set("Eyalet Seçin")
        combo_sehir['values'] = []
        sehir_var.set("")

    def eyalet_secildi(event):
        cities = get_cities(eyalet_var.get())
        combo_sehir['values'] = cities
        sehir_var.set("")

    def sorgula():
        if sehir_var.get():
            hedef = sehir_var.get()
        elif eyalet_var.get() and eyalet_var.get() != "Eyalet Seçin":
            hedef = eyalet_var.get()
        else:
            messagebox.showwarning("Uyarı", "En azından bir eyalet seçmelisiniz.")
            return

        res = weather_get(hedef)
        if res:
            temp = res['temp']

            if temp <= 0:
                temp_icon = "❄️"
            elif temp <= 10:
                temp_icon = "🧥"
            elif temp <= 20:
                temp_icon = "🌤"
            elif temp <= 30:
                temp_icon = "☀️"
            else:
                temp_icon = "🔥"

            img = Image.open(requests.get(
                f"https://openweathermap.org/img/wn/{res['icon']}@2x.png", stream=True
            ).raw)
            icon = ImageTk.PhotoImage(img)
            lbl_icon.config(image=icon)
            lbl_icon.image = icon

            lbl_sonuc.config(
                text=f"{res['name']}, {res['country']}\n{temp_icon} {temp} °C, {res['description']}")

            conn = sqlite3.connect("users.db")
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO history (username, location, temperature, description)
                VALUES (?, ?, ?, ?)
            """, (current_user, res['name'], temp, res['description']))
            conn.commit()
            conn.close()
            guncelle_gecmis()
        else:
            lbl_icon.config(image="")
            lbl_sonuc.config(text="Konum bulunamadı.")

    def guncelle_gecmis():
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT location, temperature, description, datetime
            FROM history
            WHERE username = ?
            ORDER BY datetime DESC
        """, (current_user,))
        rows = cur.fetchall()
        conn.close()
        txt_gecmis.delete("1.0", tk.END)
        for r in rows:
            txt_gecmis.insert(tk.END, f"{r[3][:16]} - {r[0]}: {r[1]} °C, {r[2]}\n")

    ulke_var = tk.StringVar()
    eyalet_var = tk.StringVar()
    sehir_var = tk.StringVar()

    combo_ulke = ttk.Combobox(win, textvariable=ulke_var, values=get_countries(), state="readonly")
    combo_ulke.set("Ülke Seçin")
    combo_ulke.bind("<<ComboboxSelected>>", ulke_secildi)
    combo_ulke.pack(pady=5)

    combo_eyalet = ttk.Combobox(win, textvariable=eyalet_var, state="readonly")
    combo_eyalet.set("Eyalet Seçin")
    combo_eyalet.bind("<<ComboboxSelected>>", eyalet_secildi)
    combo_eyalet.pack(pady=5)

    combo_sehir = ttk.Combobox(win, textvariable=sehir_var, state="readonly")
    combo_sehir.set("Şehir Seçin (isteğe bağlı)")
    combo_sehir.pack(pady=5)

    ttk.Button(win, text="Sorgula", command=sorgula).pack(pady=10)

    lbl_icon = ttk.Label(win, background=bg_color)
    lbl_icon.pack(pady=10)

    lbl_sonuc = ttk.Label(win, background=bg_color, font=("Calibri", 14), justify="center")
    lbl_sonuc.pack(pady=10)

    ttk.Label(win, text="Sorgu Geçmişi:", background=bg_color).pack()
    txt_gecmis = tk.Text(win, height=10, width=60)
    txt_gecmis.pack(pady=5)

    guncelle_gecmis()

    win.mainloop()


if __name__ == "__main__":
    setup_user_table()
    giris_ekrani()
