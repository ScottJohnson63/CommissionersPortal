from functools import partial

from readchar import config
from lib.utils import make_request
from lib.utils import load_configs
import json
import tkinter as tk
from types import SimpleNamespace

# CONFIG_FILE = 'config.json'

# def load_leagues():
#     with open(CONFIG_FILE, 'r') as f:
#         config = json.load(f)
#     return config.get('leagues', {})

# def load_descriptions():
#     with open('setting_descriptions.json', 'r') as f:
#         setting_desc = json.load(f)
#     with open('scoring_descriptions.json', 'r') as f:
#         scoring_desc = json.load(f)
#     return setting_desc, scoring_desc

def on_league_click(result, config):
    url = result.get('url')
    league_data = json.loads(json.dumps(result.get('json', {})), object_hook=lambda d: SimpleNamespace(**d))  # Convert to SimpleNamespace for easier attribute access
    # Pull setting_desc and scoring_desc from config
    setting_desc = config.setting_descriptions
    scoring_desc = config.scoring_descriptions
    popup = tk.Toplevel()
    popup.title(league_data.name)
    popup.geometry('500x500')
    popup.resizable(False, False)
    settings = league_data.settings
    scoring_settings = league_data.scoring_settings
    # Track edits for this league
    updated_settings = dict(settings)
    updated_scoring = dict(scoring_settings)
    settings_items = list(settings.items()) if settings else []
    scoring_items = list(scoring_settings.items()) if scoring_settings else []
    current_index = {'idx': 0, 'mode': 'settings'}
    info_label = tk.Label(popup, text=f"{league_data.name}\nURL: {url}\nStatus: {result['status_code']}", anchor='w', justify='left')
    info_label.pack(padx=10, pady=10)
    # Full Name (bold, underlined) and value (editable)
    full_name_var = tk.StringVar()
    value_var = tk.StringVar()
    def font_bold_underline():
        f = tk.font.Font(family='Helvetica', size=14, weight='bold', underline=1)
        return f
    full_name_label = tk.Label(popup, textvariable=full_name_var, font=font_bold_underline(), anchor='w', justify='left')
    full_name_label.pack(padx=10, pady=(10,0), anchor='w')
    value_entry = tk.Entry(popup, textvariable=value_var, width=40, font=("Consolas", 12))
    value_entry.pack(padx=10, pady=(0,5), anchor='w')
    # Key (small italic)
    key_var = tk.StringVar()
    key_label = tk.Label(popup, textvariable=key_var, font=("Helvetica", 9, "italic"), fg="gray")
    key_label.pack(padx=10, pady=(0,5), anchor='w')
    # Description
    desc_var = tk.StringVar()
    desc_label = tk.Label(popup, textvariable=desc_var, anchor='w', justify='left', wraplength=480)
    desc_label.pack(padx=10, pady=(0,10), anchor='w')
    def save_current():
        if current_index['mode'] == 'settings' and settings_items:
            key = settings_items[current_index['idx']][0]
            updated_settings[key] = value_var.get()
        elif current_index['mode'] == 'scoring' and scoring_items:
            key = scoring_items[current_index['idx']][0]
            updated_scoring[key] = value_var.get()
        # Save to file
        output = {
            'league': league_data.name,
            'settings': updated_settings,
            'scoring_settings': updated_scoring
        }
        with open(f'{league_data.name.replace(" ", "_").lower()}_updates.json', 'w') as f:
            json.dump(output, f, indent=2)
    def show_setting():
        if current_index['mode'] == 'settings':
            if not settings_items:
                full_name_var.set("No settings found in response.")
                value_var.set("")
                key_var.set("")
                desc_var.set("")
                next_btn.config(text="Review Scoring Settings", command=start_scoring)
                save_btn.config(state=tk.DISABLED)
            elif current_index['idx'] < len(settings_items):
                key, value = settings_items[current_index['idx']]
                desc_obj = setting_desc.get(key, {})
                full_name = desc_obj.get('full_name', key)
                description = desc_obj.get('description', 'No description available.')
                full_name_var.set(f"{full_name}: ")
                value_var.set(str(updated_settings.get(key, value)))
                key_var.set(key)
                desc_var.set(description)
                next_btn.config(text="Next", command=next_setting)
                save_btn.config(state=tk.NORMAL)
            else:
                full_name_var.set("End of settings.")
                value_var.set("")
                key_var.set("")
                desc_var.set("")
                next_btn.config(text="Review Scoring Settings", command=start_scoring)
                save_btn.config(state=tk.DISABLED)
        elif current_index['mode'] == 'scoring':
            if not scoring_items:
                full_name_var.set("No scoring settings found in response.")
                value_var.set("")
                key_var.set("")
                desc_var.set("")
                next_btn.config(text="Close", command=popup.destroy)
                save_btn.config(state=tk.DISABLED)
            elif current_index['idx'] < len(scoring_items):
                key, value = scoring_items[current_index['idx']]
                desc_obj = scoring_desc.get(key, {})
                full_name = desc_obj.get('full_name', key)
                description = desc_obj.get('description', 'No description available.')
                full_name_var.set(f"{full_name}: ")
                value_var.set(str(updated_scoring.get(key, value)))
                key_var.set(key)
                desc_var.set(description)
                next_btn.config(text="Next", command=next_scoring)
                save_btn.config(state=tk.NORMAL)
            else:
                full_name_var.set("End of scoring settings.")
                value_var.set("")
                key_var.set("")
                desc_var.set("")
                next_btn.config(text="Close", command=popup.destroy)
                save_btn.config(state=tk.DISABLED)
    def next_setting():
        if current_index['idx'] < len(settings_items):
            current_index['idx'] += 1
        show_setting()
    def start_scoring():
        current_index['mode'] = 'scoring'
        current_index['idx'] = 0
        show_setting()
    def next_scoring():
        if current_index['idx'] < len(scoring_items):
            current_index['idx'] += 1
        show_setting()
    def show_raw_data():
        raw_popup = tk.Toplevel(popup)
        raw_popup.title(f"Raw Data - {league_data.name}")
        raw_popup.geometry('700x500')
        raw_popup.resizable(True, True)
        text_widget = tk.Text(raw_popup, wrap=tk.WORD)
        text_widget.pack(expand=True, fill='both', padx=10, pady=10)
        raw_json = json.dumps(result.get('json', {}), indent=2)
        text_widget.insert(tk.END, raw_json)
        text_widget.config(state=tk.NORMAL)
        # Right-click context menu for copy/paste
        context_menu = tk.Menu(raw_popup, tearoff=0)
        def copy_selected():
            try:
                selected = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                raw_popup.clipboard_clear()
                raw_popup.clipboard_append(selected)
            except tk.TclError:
                pass  # No selection
        def copy_all():
            raw_popup.clipboard_clear()
            raw_popup.clipboard_append(text_widget.get('1.0', tk.END))
        def paste():
            try:
                text_widget.insert(tk.INSERT, raw_popup.clipboard_get())
            except tk.TclError:
                pass
        context_menu.add_command(label="Copy Selected", command=copy_selected)
        context_menu.add_command(label="Copy All", command=copy_all)
        context_menu.add_command(label="Paste", command=paste)
        def show_context_menu(event):
            context_menu.tk_popup(event.x_root, event.y_root)
        text_widget.bind("<Button-3>", show_context_menu)
        close_btn = tk.Button(raw_popup, text="Close", command=raw_popup.destroy)
        close_btn.pack(pady=5)
    next_btn = tk.Button(popup, text="Next", command=next_setting)
    next_btn.pack(pady=5)
    save_btn = tk.Button(popup, text="Save", command=save_current)
    save_btn.pack(pady=5)
    raw_btn = tk.Button(popup, text="Raw Data", command=show_raw_data)
    raw_btn.pack(pady=5)
    close_btn = tk.Button(popup, text="Close", command=popup.destroy)
    close_btn.pack(pady=5)
    show_setting()

def main():
    config = load_configs()
    leagues = config.leagues
    root = tk.Tk()
    root.title("Leagues")
    for url in leagues:
        try:
            result = make_request(url)
            league_name = result.get('json', {}).get('name')
            title_label = 'Review {}'.format(league_name)
            btn = tk.Button(root, text=title_label, width=30, command=partial(lambda: on_league_click(result, config)))
            btn.pack(pady=5)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

    root.mainloop()

if __name__ == '__main__':
    main()