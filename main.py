from functools import partial
from lib.utils import make_request
from lib.utils import load_config
import json
import tkinter as tk
import customtkinter as ctk
from types import SimpleNamespace
import os

# New: Load results_keys_descriptions.json directly
with open(os.path.join('conf', 'results_keys_descriptions.json'), encoding='utf-8') as f:
    results_descriptions = json.load(f)

class LeagueEditorPopup:
    def __init__(self, result, config):
        self.result = result
        self.config = config
        self.descriptions = results_descriptions
        self.url = result.get('url')
        self.league_name = self.result.get('json', {}).get('name', 'Unknown League')
        ctk.set_appearance_mode("system")  # or "dark"/"light"
        ctk.set_default_color_theme("blue")
        # Add an attribute to remember the save directory for this popup
        self.save_dir = None
        self.show_league_popup()

    def show_league_popup(self):
        json_data = self.result.get('json', {})
        popup = ctk.CTkToplevel()
        popup.title(f"{self.league_name} Editor")
        popup.geometry('950x700')
        popup.resizable(False, False)
        # Info section at the top
        url = self.url or 'Unknown URL'
        status = self.result.get('status_code', 'Unknown')
        info = f"League: {self.league_name}\nURL: {url}\nStatus: {status}"
        info_label = ctk.CTkLabel(popup, text=info, anchor='w', justify='left', font=("Consolas", 12))
        info_label.pack(padx=20, pady=10, anchor='w')
        # Review section below
        def flatten_json(y, prefix=''):
            items = []
            if isinstance(y, dict):
                for k, v in y.items():
                    new_key = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
                    items.extend(flatten_json(v, new_key))
            elif isinstance(y, list):
                for i, v in enumerate(y):
                    new_key = f"{prefix}[{i}]"
                    items.extend(flatten_json(v, new_key))
            else:
                items.append((prefix, y))
            return items
        items = flatten_json(json_data)
        idx = {'value': 0}
        key_var = ctk.StringVar()
        value_var = ctk.StringVar()
        roster_frame = None
        roster_count_vars = {}
        # Define navigation and jump functions BEFORE creating any buttons that reference them
        def next_item():
            key, _ = items[idx['value']]
            if key.startswith('roster_positions'):
                next_idx = idx['value'] + 1
                while next_idx < len(items):
                    k, _ = items[next_idx]
                    if not k.startswith('roster_positions'):
                        break
                    next_idx += 1
                if next_idx < len(items):
                    idx['value'] = next_idx
                    show_item()
            else:
                if idx['value'] < len(items) - 1:
                    idx['value'] += 1
                    show_item()

        def back_item():
            curr_idx = idx['value']
            first_rp_idx = next((i for i, (k, _) in enumerate(items) if k.startswith('roster_positions')), None)
            if first_rp_idx is not None and curr_idx > first_rp_idx:
                prev_idx = curr_idx - 1
                if items[prev_idx][0].startswith('roster_positions'):
                    idx['value'] = first_rp_idx
                    show_item()
                    return
            if idx['value'] > 0:
                idx['value'] -= 1
                show_item()

        def jump_to_section(section):
            for i, (k, v) in enumerate(items):
                if k == section or k.startswith(section + '.') or k.startswith(section + '['):
                    idx['value'] = i
                    show_item()
                    break
        # Now create jump_frame (top), nav_frame (below editor), btn_frame (right of editor)
        jump_frame = ctk.CTkFrame(popup)
        # Center the jump_frame with pack(anchor='center')
        ctk.CTkButton(jump_frame, text="Jump to Settings", command=lambda: jump_to_section('settings')).pack(side="left", padx=5)
        ctk.CTkButton(jump_frame, text="Jump to Scoring Settings", command=lambda: jump_to_section('scoring_settings')).pack(side="left", padx=5)
        ctk.CTkButton(jump_frame, text="Jump to Roster Positions", command=lambda: jump_to_section('roster_positions')).pack(side="left", padx=5)
        jump_frame.pack(padx=20, pady=(0, 10), anchor='center')  # Centered

        nav_frame = ctk.CTkFrame(popup)
        nav_frame.pack(padx=20, pady=(0, 10), anchor='center')
        back_btn = ctk.CTkButton(nav_frame, text="Back", command=back_item)
        back_btn.pack(side="left", padx=5)
        next_btn = ctk.CTkButton(nav_frame, text="Next", command=next_item)
        next_btn.pack(side="left", padx=5)
        # btn_frame = ctk.CTkFrame(popup)
        save_btn = ctk.CTkButton(nav_frame, text="Save")  # Command will be set after save_changes is defined
        save_btn.pack(side="left", padx=5)
        close_btn = ctk.CTkButton(nav_frame, text="Close", command=popup.destroy)
        close_btn.pack(side="left", padx=5)
        # Review section below
        def flatten_json(y, prefix=''):
            items = []
            if isinstance(y, dict):
                for k, v in y.items():
                    new_key = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
                    items.extend(flatten_json(v, new_key))
            elif isinstance(y, list):
                for i, v in enumerate(y):
                    new_key = f"{prefix}[{i}]"
                    items.extend(flatten_json(v, new_key))
            else:
                items.append((prefix, y))
            return items
        items = flatten_json(json_data)
        idx = {'value': 0}
        key_var = ctk.StringVar()
        value_var = ctk.StringVar()
        roster_frame = None
        roster_count_vars = {}
        # Create a single center_frame for all content, pack once
        center_frame = ctk.CTkFrame(popup)
        center_frame.pack(pady=20)
        # Remove the extra button_frame and its buttons here
        # ...existing code...
        def show_item():
            nonlocal roster_frame
            if roster_frame:
                roster_frame.destroy()
                roster_frame = None
            if not items:
                if hasattr(show_item, 'desc_label') and show_item.desc_label.winfo_exists():
                    show_item.desc_label.pack_forget()
                if hasattr(show_item, 'key_label') and show_item.key_label.winfo_exists():
                    show_item.key_label.pack_forget()
                if hasattr(show_item, 'sublabel') and show_item.sublabel.winfo_exists():
                    show_item.sublabel.pack_forget()
                key_var.set('No data')
                value_var.set('')
                if value_entry.winfo_ismapped():
                    value_entry.pack_forget()
                if nav_frame.winfo_ismapped():
                    nav_frame.pack_forget()
                return

            key, value = items[idx['value']]
            # Remove previous labels if present
            if hasattr(show_item, 'desc_label') and show_item.desc_label.winfo_exists():
                show_item.desc_label.pack_forget()
            if hasattr(show_item, 'key_label') and show_item.key_label.winfo_exists():
                show_item.key_label.pack_forget()
            if hasattr(show_item, 'sublabel') and show_item.sublabel.winfo_exists():
                show_item.sublabel.pack_forget()
            # Find description and full name for the key
            desc = None
            full_name = None
            key_base = key.split('.')[-1].split('[')[0]
            if key_base in self.descriptions:
                desc_info = self.descriptions[key_base]
                if isinstance(desc_info, dict):
                    full_name = desc_info.get('full_name')
                    desc = desc_info.get('description')
                else:
                    full_name = desc_info
            # Place nav_frame above the full name label
            show_item.key_label = ctk.CTkLabel(center_frame, text=full_name or key_base, font=("Consolas", 13, "bold"), anchor='center', justify='center')
            show_item.key_label.pack(padx=20, pady=(10,0))
            show_item.sublabel = ctk.CTkLabel(center_frame, text=f"{key}", font=("Consolas", 10, "italic"), anchor='center', justify='center')
            show_item.sublabel.pack(padx=20, pady=(0,5))
            if desc:
                show_item.desc_label = ctk.CTkLabel(center_frame, text=desc, font=("Consolas", 11), anchor='center', justify='center', wraplength=800)
                show_item.desc_label.pack(padx=20, pady=(0,10))

            if key.startswith('roster_positions'):
                if value_entry.winfo_ismapped():
                    value_entry.pack_forget()
                # Show unique roster positions in a table, centered
                roster_positions = json_data.get('roster_positions', [])
                counts = {}
                unique_positions = []
                for pos in roster_positions:
                    pos_str = str(pos)
                    if pos_str not in counts:
                        unique_positions.append(pos_str)
                    counts[pos_str] = counts.get(pos_str, 0) + 1
                roster_frame = ctk.CTkFrame(center_frame)
                roster_frame.pack(pady=(0,10))
                table_inner = ctk.CTkFrame(roster_frame)
                table_inner.pack(anchor='center')
                ctk.CTkLabel(table_inner, text="Position", font=("Consolas", 12, "bold")).grid(row=0, column=0, sticky='nsew')
                ctk.CTkLabel(table_inner, text="Count", font=("Consolas", 12, "bold")).grid(row=0, column=1, sticky='nsew')
                for i, pos in enumerate(unique_positions, start=1):
                    ctk.CTkLabel(table_inner, text=pos, font=("Consolas", 12)).grid(row=i, column=0, sticky='nsew')
                    var = ctk.StringVar(value=str(counts[pos]))
                    roster_count_vars[pos] = var
                    entry = ctk.CTkEntry(table_inner, textvariable=var, width=80, font=("Consolas", 12), justify='center')
                    entry.grid(row=i, column=1, sticky='nsew', padx=2, pady=2)
            else:
                if value_entry.winfo_ismapped():
                    value_entry.pack_forget()
                value_entry.pack(in_=center_frame, padx=20, pady=(0,10))
                # Pack button frame below value entry
                # btn_frame.pack(pady=(10,0))
                value_var.set(str(value))

            back_btn.configure(state="normal" if idx['value'] > 0 else "disabled")
            next_btn.configure(state="normal" if idx['value'] < len(items) - 1 else "disabled")
        key_label = ctk.CTkLabel(popup, textvariable=key_var, font=("Consolas", 12, "bold"), anchor='w', justify='left')
        key_label.pack(padx=20, pady=(30,5), anchor='w')
        value_entry = ctk.CTkEntry(popup, textvariable=value_var, width=600, font=("Consolas", 12))
        # Do not pack value_entry here; let show_item handle it in the correct order
        # Create nav_frame (Back/Next) and btn_frame (Save/Close) but do not pack yet
        # nav_frame = ctk.CTkFrame(popup)
        # back_btn = ctk.CTkButton(nav_frame, text="Back", command=back_item)
        # back_btn.pack(side="left", padx=5)
        # next_btn = ctk.CTkButton(nav_frame, text="Next", command=next_item)
        # next_btn.pack(side="left", padx=5)

        # save_btn = ctk.CTkButton(nav_frame, text="Save")  # Command will be set after save_changes is defined
        # save_btn.pack(side="left", padx=5)
        # close_btn = ctk.CTkButton(nav_frame, text="Close", command=popup.destroy)
        # close_btn.pack(side="left", padx=5)
        def save_changes():
            import tkinter.filedialog as fd
            key, _ = items[idx['value']]
            def set_in_json(data, key_path, value):
                parts = []
                for part in key_path.replace(']', '').split('.'):
                    if '[' in part:
                        k, idx = part.split('[')
                        parts.append(k)
                        parts.append(int(idx))
                    else:
                        parts.append(part)
                d = data
                for p in parts[:-1]:
                    if isinstance(p, int):
                        d = d[p]
                    else:
                        d = d[p]
                last = parts[-1]
                if isinstance(last, int):
                    d[last] = value
                else:
                    d[last] = value
            # Only update if not roster_positions
            if not key.startswith('roster_positions'):
                try:
                    # If editing the name, do NOT update the 'name' key, only set new_name
                    if key == 'name':
                        old_name = json_data['name']
                        items_list = list(json_data.items())
                        name_index = next((i for i, (k, _) in enumerate(items_list) if k == 'name'), None)
                        if name_index is not None:
                            items_list = [item for item in items_list if item[0] != 'new_name']
                            items_list.insert(name_index + 1, ('new_name', value_var.get()))
                            items_list[name_index] = ('name', old_name)
                            json_data.clear()
                            json_data.update(items_list)
                        else:
                            json_data['new_name'] = value_var.get()
                        print(f"Saved: new_name = {value_var.get()} (name remains {old_name})")
                    else:
                        set_in_json(json_data, key, value_var.get())
                        print(f"Saved: {key} = {value_var.get()}")
                except Exception as e:
                    print(f"Error saving {key}: {e}")
            # Determine file name
            league_name = json_data.get('name', 'league')
            if 'new_name' in json_data:
                file_name_base = json_data['new_name']
            else:
                file_name_base = league_name
            safe_name = ''.join(c for c in file_name_base if c.isalnum() or c in (' ', '_', '-')).rstrip()
            # Ask for save location on first save
            if self.save_dir is None:
                file_path = fd.asksaveasfilename(
                    title='Save League File',
                    defaultextension='.json',
                    initialfile=f"{safe_name}.json",
                    filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')]
                )
                if not file_path:
                    print("Save cancelled.")
                    return
                self.save_dir = os.path.dirname(file_path)
                filename = file_path
            else:
                filename = os.path.join(self.save_dir, f"{safe_name}.json")
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2)
                print(f"League data saved to {filename}")
            except Exception as e:
                print(f"Error writing file {filename}: {e}")

        save_btn.configure(command=save_changes)
        show_item()

def main():
    config = load_config()
    leagues = config.leagues
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
            league_name = result.get('json', {}).get('name')
            btn = ctk.CTkButton(main_frame, text=league_name, width=300, height=40, font=("Consolas", 14), command=partial(lambda r=result: LeagueEditorPopup(r, config)))
            btn.pack(pady=8)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    root.mainloop()

if __name__ == '__main__':
    main()