# CustomTkinter GUI Patterns

## Sinhala Font Setup
```python
import tkinter.font as tkfont

SINHALA_FONT = ("Iskoola Pota", 16)
SINHALA_FONT_BOLD = ("Iskoola Pota", 16, "bold")
HEADING_FONT = ("Iskoola Pota", 20, "bold")

# Fallback if Iskoola Pota not found:
# ("Noto Sans Sinhala", 16)
```

## Highlighted Text (Error Highlighting)
```python
# Must use tk.Text not CTkTextbox for tag support
import tkinter as tk

text = tk.Text(frame, font=SINHALA_FONT, wrap="word",
               bg="#2b2b2b", fg="white", insertbackground="white")

text.tag_configure("spell_error",
    background="#8B0000", foreground="white",
    font=SINHALA_FONT_BOLD)
text.tag_configure("grammar_error", 
    background="#8B4500", foreground="white")

# Apply highlight:
text.tag_add("spell_error", f"1.{start}", f"1.{end}")
```

## Loading Spinner
```python
import threading

def check_with_spinner():
    btn_check.configure(state="disabled", text="⏳ පරීක්ෂා කරමින්...")
    
    def run():
        result = proofreader.proofread(input_text)
        root.after(0, lambda: display_results(result))
        root.after(0, lambda: btn_check.configure(
            state="normal", text="🔍 පරීක්ෂා කරන්න"))
    
    threading.Thread(target=run, daemon=True).start()
```

## Status Indicator
```python
def update_status(connected: bool, message: str):
    color = "#00AA00" if connected else "#CC0000"
    icon = "✅" if connected else "❌"
    status_label.configure(text=f"{icon} {message}", text_color=color)
```