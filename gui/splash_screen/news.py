import customtkinter as ctk


class NewsPanel:
    """ Manages the news section on the splash screen. """

    def __init__(self):
        self.frame = None
        self.news_box = None

    def build(self, parent) -> ctk.CTkFrame:
        news = ctk.CTkFrame(parent)
        news.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)

        news.rowconfigure(1, weight=1)
        news.columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            news,
            text='News',
            font=('Segoe UI', 14, 'bold'),
        ).grid(row=0, column=0, pady=(4, 8), sticky='w')

        # Content
        self.news_box = ctk.CTkTextbox(news, wrap='word')
        self.news_box.insert('end', 'Welcome to ProtoX GDK!\n')
        self.news_box.configure(state='disabled')
        self.news_box.grid(row=1, column=0, sticky='nsew', padx=2, pady=2)

        return news
