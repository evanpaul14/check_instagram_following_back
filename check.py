import json
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def find_not_following_back(following_path: Path, followers_path: Path):
    following_data = load_json(following_path)
    followers_data = load_json(followers_path)

    following = following_data.get("relationships_following", [])
    followers = followers_data

    following_usernames = {entry.get("title") for entry in following if "title" in entry}

    followers_usernames = {
        entry.get("string_list_data", [{}])[0].get("value")
        for entry in followers
        if entry.get("string_list_data")
    }

    return sorted([u for u in following_usernames if u and u not in followers_usernames])


class InstagramCheckerApp:

    def __init__(self, root: tk.Tk):

        self.root = root
        self.root.title("Instagram Followback Checker")
        self.root.geometry("900x620")
        self.root.configure(bg="#0f1115")

        self.following_path = tk.StringVar()
        self.followers_path = tk.StringVar()

        self._configure_style()
        self._build_ui()

    def _configure_style(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Root.TFrame", background="#0f1115")
        style.configure("Card.TFrame", background="#171a21")

        style.configure(
            "Title.TLabel",
            background="#171a21",
            foreground="#f5f7fa",
            font=("Avenir Next", 22, "bold"),
        )

        style.configure(
            "Sub.TLabel",
            background="#171a21",
            foreground="#9aa3b2",
            font=("Avenir Next", 11),
        )

        style.configure(
            "Field.TLabel",
            background="#171a21",
            foreground="#d2d9e4",
            font=("Avenir Next", 11),
        )

        style.configure(
            "Link.TLabel",
            background="#171a21",
            foreground="#4c92ff",
            font=("Avenir Next", 11),
        )

        style.configure(
            "Modern.TButton",
            background="#2d7dff",
            foreground="#ffffff",
            borderwidth=0,
            font=("Avenir Next", 11, "bold"),
            padding=(12, 8),
        )

        style.map(
            "Modern.TButton",
            background=[("active", "#4c92ff"), ("pressed", "#225fc2")],
        )

        style.configure(
            "Dark.TEntry",
            fieldbackground="#0f1115",
            foreground="#e5ebf5",
        )

        # custom scrollbar colors to blend with dark theme
        style.configure(
            "Vertical.TScrollbar",
            background="#171a21",
            troughcolor="#0f1115",
            bordercolor="#171a21",
            arrowcolor="#d2d9e4",
            gripcount=0,
            darkcolor="#171a21",
            lightcolor="#171a21",
            width=16,
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", "#2d7dff")],
        )

    def _build_ui(self):

        root_frame = ttk.Frame(self.root, style="Root.TFrame", padding=24)
        root_frame.pack(fill="both", expand=True)

        card = ttk.Frame(root_frame, style="Card.TFrame", padding=24)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Instagram Followback Checker", style="Title.TLabel").pack(anchor="w")

        ttk.Label(
            card,
            text="Load your Instagram export files and find who does not follow you back.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(6, 20))

        ttk.Label(card, text="following.json", style="Field.TLabel").pack(anchor="w")

        follow_row = ttk.Frame(card, style="Card.TFrame")
        follow_row.pack(fill="x", pady=(6, 14))

        ttk.Entry(
            follow_row,
            textvariable=self.following_path,
            font=("Menlo", 11),
            style="Dark.TEntry",
        ).pack(side="left", fill="x", expand=True, ipady=6)

        ttk.Button(
            follow_row,
            text="Browse",
            style="Modern.TButton",
            command=self._browse_following,
        ).pack(side="left", padx=(10, 0))

        ttk.Label(card, text="followers_1.json", style="Field.TLabel").pack(anchor="w")

        follower_row = ttk.Frame(card, style="Card.TFrame")
        follower_row.pack(fill="x", pady=(6, 18))

        ttk.Entry(
            follower_row,
            textvariable=self.followers_path,
            font=("Menlo", 11),
            style="Dark.TEntry",
        ).pack(side="left", fill="x", expand=True, ipady=6)

        ttk.Button(
            follower_row,
            text="Browse",
            style="Modern.TButton",
            command=self._browse_followers,
        ).pack(side="left", padx=(10, 0))


        ttk.Button(
            card,
            text="Check Followbacks",
            style="Modern.TButton",
            command=self._run_check,
        ).pack(anchor="w", pady=(0, 16))

        self.summary_label = ttk.Label(card, text="Results will appear below.", style="Sub.TLabel")
        self.summary_label.pack(anchor="w", pady=(0, 8))

        result_frame = ttk.Frame(card, style="Card.TFrame")
        result_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(result_frame, bg="#0f1115", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.canvas.yview,
            style="Vertical.TScrollbar",
        )
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        # enable mouse wheel scrolling; bind globally so the scroll works even
        # when the pointer is over child widgets inside the canvas.  the helper
        # computes a signed unit value and guards against small deltas on macOS.
        def _on_mousewheel(event):
            delta = event.delta
            if delta:
                move = int(-1 * (delta / 120))
                if move == 0:
                    move = -1 if delta > 0 else 1
            else:
                move = 0
            self.canvas.yview_scroll(move, "units")

        # bind once for the lifetime of the app
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # also support other scroll events (Linux)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        self.scrollable_frame = ttk.Frame(self.canvas, style="Card.TFrame")

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

    def _browse_following(self):

        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])

        if file:
            self.following_path.set(file)

    def _browse_followers(self):

        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])

        if file:
            self.followers_path.set(file)




    def _unfollow_user(self, username):
        """Open the user's profile in the browser and remind the user to unfollow.

        The app no longer attempts any automatic network requests; all unfollowing is
        handled manually by the user in their browser.
        """

        webbrowser.open_new_tab(f"https://www.instagram.com/{username}/")
        messagebox.showinfo(
            "Unfollow",
            "Instagram opened in your browser.\nClick 'Following' → 'Unfollow'.",
        )


    def _run_check(self):

        following = self.following_path.get().strip()
        followers = self.followers_path.get().strip()

        if not following or not followers:

            messagebox.showwarning("Missing files", "Please select both JSON files.")

            return

        following_path = Path(following)
        followers_path = Path(followers)

        if not following_path.exists() or not followers_path.exists():

            messagebox.showerror("File error", "Selected files do not exist.")

            return

        try:

            users = find_not_following_back(following_path, followers_path)

        except Exception as e:

            messagebox.showerror("Error", str(e))

            return

        for child in self.scrollable_frame.winfo_children():
            child.destroy()

        if not users:

            self.summary_label.configure(text="Everyone follows you back.")

            return

        self.summary_label.configure(
            text=f"{len(users)} account(s) do not follow you back."
        )

        for i, username in enumerate(users, 1):

            row = ttk.Frame(self.scrollable_frame, style="Card.TFrame")
            row.pack(fill="x", pady=2)

            ttk.Label(
                row,
                text=f"{i}.",
                style="Field.TLabel",
            ).pack(side="left")

            user_label = ttk.Label(
                row,
                text=username,
                style="Link.TLabel",
                cursor="hand2",
            )

            user_label.pack(side="left", padx=6)

            user_label.bind(
                "<Button-1>",
                lambda e, u=username: webbrowser.open_new_tab(
                    f"https://www.instagram.com/{u}/"
                ),
            )

            ttk.Button(
                row,
                text="Unfollow",
                style="Modern.TButton",
                command=lambda u=username: self._unfollow_user(u),
            ).pack(side="right")


def main():

    root = tk.Tk()

    InstagramCheckerApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()