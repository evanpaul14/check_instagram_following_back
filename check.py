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

    following = following_data["relationships_following"]
    followers = followers_data

    following_usernames = [entry["title"] for entry in following]
    followers_usernames = [entry["string_list_data"][0]["value"] for entry in followers]

    return [user for user in following_usernames if user not in followers_usernames]


class InstagramCheckerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Instagram Followback Checker")
        self.root.geometry("900x620")
        self.root.configure(bg="#0f1115")

        self.following_path = tk.StringVar()
        self.followers_path = tk.StringVar()
        # map tag names to URLs for hyperlink handling
        self._link_map: dict[str,str] = {}

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
            "Modern.TButton",
            background="#2d7dff",
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            font=("Avenir Next", 11, "bold"),
            padding=(12, 8),
        )
        style.map(
            "Modern.TButton",
            background=[("active", "#4c92ff"), ("pressed", "#225fc2")],
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
        tk.Entry(
            follow_row,
            textvariable=self.following_path,
            font=("Menlo", 11),
            background="#0f1115",
            foreground="#e5ebf5",
            insertbackground="#e5ebf5",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#2a3240",
            highlightcolor="#2d7dff",
        ).pack(side="left", fill="x", expand=True, ipady=6)
        ttk.Button(follow_row, text="Browse", style="Modern.TButton", command=self._browse_following).pack(
            side="left", padx=(10, 0)
        )

        ttk.Label(card, text="followers_1.json", style="Field.TLabel").pack(anchor="w")
        follower_row = ttk.Frame(card, style="Card.TFrame")
        follower_row.pack(fill="x", pady=(6, 18))
        tk.Entry(
            follower_row,
            textvariable=self.followers_path,
            font=("Menlo", 11),
            background="#0f1115",
            foreground="#e5ebf5",
            insertbackground="#e5ebf5",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#2a3240",
            highlightcolor="#2d7dff",
        ).pack(side="left", fill="x", expand=True, ipady=6)
        ttk.Button(follower_row, text="Browse", style="Modern.TButton", command=self._browse_followers).pack(
            side="left", padx=(10, 0)
        )

        ttk.Button(card, text="Check Followbacks", style="Modern.TButton", command=self._run_check).pack(
            anchor="w", pady=(0, 16)
        )

        self.summary_label = ttk.Label(card, text="Results will appear below.", style="Sub.TLabel")
        self.summary_label.pack(anchor="w", pady=(0, 8))

        result_frame = ttk.Frame(card, style="Card.TFrame")
        result_frame.pack(fill="both", expand=True)

        self.results = tk.Text(
            result_frame,
            bg="#0f1115",
            fg="#dfe6f3",
            insertbackground="#dfe6f3",
            selectbackground="#2d7dff",
            relief="flat",
            font=("Menlo", 11),
            padx=12,
            pady=10,
        )
        self.results.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.results.yview)
        scrollbar.pack(side="right", fill="y")
        self.results.configure(yscrollcommand=scrollbar.set)

        # hyperlink tags will be configured dynamically per-entry later
        # (keep default style for safety)

    def _browse_following(self):
        selected = filedialog.askopenfilename(
            title="Select following.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*")],
        )
        if selected:
            self.following_path.set(selected)

    def _browse_followers(self):
        selected = filedialog.askopenfilename(
            title="Select followers_1.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*")],
        )
        if selected:
            self.followers_path.set(selected)

    def _open_url(self, url: str):
        webbrowser.open_new_tab(url)

    def _on_link_click(self, event):
        tags = event.widget.tag_names("current")
        for t in tags:
            if t.startswith("link") and t in self._link_map:
                webbrowser.open_new_tab(self._link_map[t])
                return

    def _run_check(self):
        following = self.following_path.get().strip().replace("'", "")
        followers = self.followers_path.get().strip().replace("'", "")

        if not following or not followers:
            messagebox.showwarning("Missing files", "Please select both JSON files.")
            return

        following_path = Path(following)
        followers_path = Path(followers)

        if not following_path.exists() or not followers_path.exists():
            messagebox.showerror("File not found", "One or both selected files do not exist.")
            return

        try:
            not_following_back = find_not_following_back(following_path, followers_path)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            messagebox.showerror("Invalid JSON format", f"Could not parse Instagram JSON files.\n\n{error}")
            return
        except OSError as error:
            messagebox.showerror("Read error", f"Could not read one of the files.\n\n{error}")
            return

        self.results.delete("1.0", tk.END)
        if not not_following_back:
            self.summary_label.configure(text="Everyone you follow follows you back.")
            self.results.insert(tk.END, "No users found.\n")
            return

        self.summary_label.configure(
            text=f"{len(not_following_back)} account(s) do not follow you back."
        )
        for index, username in enumerate(not_following_back, start=1):
            # insert the numbered prefix
            self.results.insert(tk.END, f"{index}. ")
            tag = f"link{index}"
            profile_url = f"https://www.instagram.com/{username}/"
            self._link_map[tag] = profile_url
            self.results.insert(tk.END, username, (tag,))
            # style and bind this specific tag
            self.results.tag_configure(tag, foreground="#4c92ff", underline=True)
            self.results.tag_bind(tag, "<Button-1>", self._on_link_click)
            self.results.insert(tk.END, "\n")


def main():
    root = tk.Tk()
    InstagramCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()