import customtkinter as ctk
import json
import os

def show_league_reviewer(result, parent=None):
    # Load key descriptions from conf/results_keys_descriptions.json
    conf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf', 'results_keys_descriptions.json')
    try:
        with open(conf_path, encoding='utf-8') as f:
            descriptions = json.load(f)
    except Exception:
        descriptions = {}
    # result is a dict with 'data', 'status_code', 'url'
    data = result.get('data', {}) or {}
    status = result.get('status_code', 'Unknown')
    url = result.get('url', 'Unknown URL')
    league_name = data.get('name', 'Unknown League')
    league_id = data.get('league_id', '')
    if league_id:
        url = f"https://api.sleeper.app/v1/league/{league_id}"
    popup = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    popup.title(f"{league_name} Editor")
    popup.geometry('950x700')
    popup.resizable(False, False)
    info = f"League: {league_name}\nURL: {url}\nStatus: {status}"
    info_label = ctk.CTkLabel(popup, text=info, anchor='w', justify='left', font=("Consolas", 12))
    info_label.pack(padx=20, pady=10, anchor='w')
    json_data = data
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
    jump_frame = ctk.CTkFrame(popup)
    ctk.CTkButton(jump_frame, text="Jump to Settings", command=lambda: jump_to_section('settings')).pack(side="left", padx=5)
    ctk.CTkButton(jump_frame, text="Jump to Scoring Settings", command=lambda: jump_to_section('scoring_settings')).pack(side="left", padx=5)
    ctk.CTkButton(jump_frame, text="Jump to Roster Positions", command=lambda: jump_to_section('roster_positions')).pack(side="left", padx=5)
    jump_frame.pack(padx=20, pady=(0, 10), anchor='center')
    nav_frame = ctk.CTkFrame(popup)
    nav_frame.pack(padx=20, pady=(0, 10), anchor='center')
    back_btn = ctk.CTkButton(nav_frame, text="Back", command=back_item)
    back_btn.pack(side="left", padx=5)
    next_btn = ctk.CTkButton(nav_frame, text="Next", command=next_item)
    next_btn.pack(side="left", padx=5)
    save_btn = ctk.CTkButton(nav_frame, text="Save")
    save_btn.pack(side="left", padx=5)
    close_btn = ctk.CTkButton(nav_frame, text="Close", command=popup.destroy)
    close_btn.pack(side="left", padx=5)
    center_frame = ctk.CTkFrame(popup)
    center_frame.pack(pady=20)
    def show_item():
        nonlocal roster_frame
        if roster_frame:
            roster_frame.destroy()
            roster_frame = None
        if not items:
            key_var.set('No data')
            value_var.set('')
            return
        key, value = items[idx['value']]
        # Remove previous labels if present
        if hasattr(show_item, 'desc_label') and show_item.desc_label.winfo_exists():
            show_item.desc_label.pack_forget()
        if hasattr(show_item, 'key_label') and show_item.key_label.winfo_exists():
            show_item.key_label.pack_forget()
        if hasattr(show_item, 'sublabel') and show_item.sublabel.winfo_exists():
            show_item.sublabel.pack_forget()
        desc = None
        full_name = None
        key_base = key.split('.')[-1].split('[')[0]
        if key_base in descriptions:
            desc_info = descriptions[key_base]
            if isinstance(desc_info, dict):
                full_name = desc_info.get('full_name')
                desc = desc_info.get('description')
            else:
                full_name = desc_info
        show_item.key_label = ctk.CTkLabel(center_frame, text=full_name or key_base, font=("Consolas", 13, "bold"), anchor='center', justify='center')
        show_item.key_label.pack(padx=20, pady=(10,0))
        show_item.sublabel = ctk.CTkLabel(center_frame, text=f"{key}", font=("Consolas", 10, "italic"), anchor='center', justify='center')
        show_item.sublabel.pack(padx=20, pady=(0,5))
        if desc:
            show_item.desc_label = ctk.CTkLabel(center_frame, text=desc, font=("Consolas", 11), anchor='center', justify='center', wraplength=800)
            show_item.desc_label.pack(padx=20, pady=(0,10))
        if key.startswith('roster_positions'):
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
            value_entry.pack(in_=center_frame, padx=20, pady=(0,10))
            value_var.set(str(value))
        back_btn.configure(state="normal" if idx['value'] > 0 else "disabled")
        next_btn.configure(state="normal" if idx['value'] < len(items) - 1 else "disabled")
    key_label = ctk.CTkLabel(popup, textvariable=key_var, font=("Consolas", 12, "bold"), anchor='w', justify='left')
    key_label.pack(padx=20, pady=(30,5), anchor='w')
    value_entry = ctk.CTkEntry(popup, textvariable=value_var, width=600, font=("Consolas", 12))
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
        if not key.startswith('roster_positions'):
            try:
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
                else:
                    set_in_json(json_data, key, value_var.get())
            except Exception as e:
                pass
        league_name = json_data.get('name', 'league')
        if 'new_name' in json_data:
            file_name_base = json_data['new_name']
        else:
            file_name_base = league_name
        safe_name = ''.join(c for c in file_name_base if c.isalnum() or c in (' ', '_', '-')).rstrip()
        file_path = fd.asksaveasfilename(
            title='Save League File',
            defaultextension='.json',
            initialfile=f"{safe_name}.json",
            filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
        except Exception as e:
            pass
    save_btn.configure(command=save_changes)
    show_item()
