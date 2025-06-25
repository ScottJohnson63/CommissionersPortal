import customtkinter as ctk
from api_client import get_config, make_request
from leagueMenu import open_league_menu

def main():
    config = get_config()
    leagues = config.get('leagues', [])
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Leagues")
    root.geometry('400x600')
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    title_label = ctk.CTkLabel(main_frame, text="Leagues", font=("Consolas", 18, "bold"))
    title_label.pack(pady=(0, 20))
    for url in leagues:
        try:
            result = make_request(url)
            # Debug print to inspect the structure
            print(f"DEBUG: make_request({url}) returned: {result}")
            league_name = result['data'].get('name', 'Unknown League') if result['data'] else 'Unknown League'
            btn = ctk.CTkButton(
                main_frame,
                text=league_name,
                width=300,
                height=40,
                font=("Consolas", 14),
                command=lambda r=result: open_league_menu(r, root)
            )
            btn.pack(pady=8)
        except Exception as e:
            btn = ctk.CTkButton(main_frame, text=f"Error: {e}", width=300, height=40, font=("Consolas", 14))
            btn.pack(pady=8)
    root.mainloop()

if __name__ == '__main__':
    main()
