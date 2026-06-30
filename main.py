import threading
import tkinter as tk
from tkinter import messagebox, ttk
import ai_service
import database


class VocabApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Wortschatz-App")
        self.root.geometry("500x400")

        self.current_page = 1 

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.create_search_tab()
        self.create_list_tab()
        self.create_top50_tab()

    # --- 1. 검색 페이지 ---
    def create_search_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 Suchen")

        ttk.Label(tab, text="Deutsches Wort eingeben:", font=("Arial", 12)).pack(
            pady=20
        )
        self.entry_word = ttk.Entry(tab, font=("Arial", 14), width=25)
        self.entry_word.bind("<Return>", lambda e: self.on_search())
        self.entry_word.pack(pady=5)

        ttk.Button(tab, text="Suchen & Speichern", command=self.on_search).pack(
            pady=15
        )

        self.lbl_result = ttk.Label(
            tab, text="", font=("Arial", 12), foreground="blue"
        )
        self.lbl_result.pack(pady=20)

    def on_search(self):
        user_input = self.entry_word.get().strip()
        if not user_input:
            return

        self.lbl_result.config(text="AI analysiert...")

        # apply background thread to avoid freezing the UI
        def bg_task():
            corrected_word, meaning = ai_service.search_word_via_ai(user_input)

            if corrected_word and meaning:
                database.save_or_update_word(corrected_word, meaning)

                # UI 업데이트는 안전하게 메인 스레드 큐(after)에 넘겨줍니다.
                self.root.after(
                    0,
                    lambda: self.lbl_result.config(
                        text=f"Ergebnis: {corrected_word} = {meaning}"
                    ),
                )
                self.root.after(0, lambda: self.entry_word.delete(0, tk.END))
                self.root.after(0, self.refresh_lists)
            else:
                self.root.after(
                    0,
                    lambda: self.lbl_result.config(
                        text="Suche fehlgeschlagen."
                    ),
                )

        # 백그라운드 일꾼에게 일을 던지고 바로 출발시킵니다.
        # 이 덕분에 메인 스레드는 0.0001초만에 자유로워져서 유저의 다른 클릭을 계속 감지합니다.
        threading.Thread(target=bg_task, daemon=True).start()

    # --- 2. entire Wortebuch page ---
    def create_list_tab(self):
        self.tab_list = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_list, text="📖 Mein Buch")

        self.listbox_all = tk.Listbox(self.tab_list, font=("Arial", 11))
        self.listbox_all.pack(expand=True, fill="both", padx=10, pady=10)

        ttk.Button(
            self.tab_list, text="Als gelernt markieren (Löschen)", command=self.on_delete_all
        ).pack(pady=5)

    def on_delete_all(self):
        selected = self.listbox_all.curselection()
        if not selected:
            return
        idx = selected[0]
        word_id = self.all_word_ids[idx]

        database.delete_word_by_id(word_id)
        self.refresh_lists()

    # --- 3. Heufig gesucht(Top 50) page ---
    def create_top50_tab(self):
        self.tab_top50 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_top50, text="🔥 Top 50")

        self.listbox_top50 = tk.Listbox(self.tab_top50, font=("Arial", 11))
        self.listbox_top50.pack(expand=True, fill="both", padx=10, pady=10)

        ttk.Button(
            self.tab_top50,
            text="Als gelernt markieren (Löschen)",
            command=self.on_delete_top50,
        ).pack(pady=5)

    def on_delete_top50(self):
        selected = self.listbox_top50.curselection()
        if not selected:
            return
        idx = selected[0]
        word_id = self.top50_word_ids[idx]

        database.delete_word_by_id(word_id)
        self.refresh_lists()

    # --- renew page ---
    def refresh_lists(self):
        self.listbox_all.delete(0, tk.END)
        
        words = database.get_all_words_paged(page=self.current_page, limit=50)
        
        self.all_word_ids = [w[0] for w in words]
        for w in words:
            self.listbox_all.insert(tk.END, f"🇩🇪 {w[1]} : {w[2]}")

        self.listbox_top50.delete(0, tk.END)
        top_words = database.get_top_50_words()
        self.top50_word_ids = [w[0] for w in top_words]
        for w in top_words:
            self.listbox_top50.insert(
                tk.END, f"[{w[3]}-mal] {w[1]} : {w[2]}"
            )


if __name__ == "__main__":
    database.init_db()  # DB renewal
    root = tk.Tk()
    app = VocabApp(root)
    app.refresh_lists()
    root.mainloop()