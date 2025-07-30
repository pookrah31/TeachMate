import os
from openai import OpenAI  
from dotenv import load_dotenv
import tkinter as tk
import threading
from tkinter import scrolledtext
from datetime import datetime

# Load environment variables from .env file  
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in .env file.")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain(concept, mode='simple', level='Beginner'):
    prompt = {
        "simple":  f"Explain {concept} in simple terms to a 10-year-old to comprehend. Use examples and analogies where helpful. Keep it to about 3-4 sentences.",
        "Story": f"Explain {concept} to a 10-year-old using a fun, short story or cartoon adventure (3-5 sentences).",
        "Analogy": f"Explain {concept} using a strong analogy, like comparing it to something familiar.",
        "level": f"Explain the concept of {concept} in a {level.lower()} level tone."
    }

    default_prompt = prompt.get(mode, prompt["simple"])

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 'You are a helpful mate that explains concepts in simple and engaging terms to a 10 year-old child. Use creative, simple language based on the chosen mode.'},
                {"role": "user", "content": default_prompt}],
            max_tokens=250,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't explain that. Error: {str(e)}"

def save_to_history(concept, mode, explanation):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"📅 Time: {now}\n🎛️ Mode: {mode}\n🔍 Concept: {concept}\n💬 Explanation: {explanation}\n{'-'*60}\n"

    try:
        with open("teachmate_history.txt", "a", encoding="utf-8") as file:
            file.write(entry)
    except Exception as e:
        print(f"⚠️ Could not save history: {e}")

def explain_gui():
    root = tk.Tk()
    root.configure(bg="#FFFFFF")
    root.title(" 🧠 TeachMate - Simple Concept Explainer Just like Your Peer! 👩‍🏫") 
    
    concept_level = tk.StringVar(value="Beginner")

    level_label = tk.Label(root, text="🎓 Select Concept Level:", font=("Comic Sans MS", 12), fg="black", bg="#FDF6EC")
    level_label.grid(row=2, column=1, sticky="w", padx=5) 

    level_dropdown = tk.OptionMenu(root, concept_level, "Beginner", "Intermediate", "Advanced")
    level_dropdown.config(font=("Comic San MS", 12), bg="#F0E68C", fg="black")
    level_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    welcome = tk.Label(
        root, 
        text=" 👋 Welcome to TeachMate - Your Simple Concept Explainer! 🤓\n",
        font=("Segoe UI", 20, "bold"), 
        fg="#2C3E50",
        bg="#F5F5F5",
    )
    welcome.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

    entry = tk.Entry(root, width=50)
    entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    root.columnconfigure(0, weight=1)

    mode_var = tk.StringVar(root)
    mode_var.set("Simple")

    mode_label = tk.Label(root, text="🎛️ Choose Explanation Mode:", font=("Comic Sans MS", 12), fg="black", bg="#FDF6EC")
    mode_label.grid(row=1, column=1, sticky="w", padx=5)

    mode_menu = tk.OptionMenu(root, mode_var, "Simple", "Story", "Analogy")
    mode_menu.config(font=("Comic Sans MS", 12), bg="#F0E68C", fg="black")
    mode_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    output = scrolledtext.ScrolledText(
        root,
        width=60,
        height=20,
        font=("Comic Sans MS", 11),
        fg="#1A1A1A",
        bg="#E8F0FE",
        wrap=tk.WORD,
        state='disabled'


    )
    output.grid(row=3, column=0, padx=20, pady=10, sticky="nsew") 

    loading_label = tk.Label(root, text="", font=("Comic Sans MS", 10), fg="blue", bg="#FFFFFF")
    loading_label.grid(row=5, column=0, columnspan=2, pady=5)

    def clear_output():
        output.config(state='normal')
        output.delete("1.0", tk.END)
        output.config(state='disabled')

    clear_output_button = tk.Button(
        root,
        text="🧼 Clear Output",
        command=clear_output,
        font=("Comic Sans MS", 10, "bold"),
        bg="#ADD8E6",
        fg="black",
        relief="raised",
        bd=2
    )
    clear_output_button.grid(row=4, column=1, padx=20, pady=5, sticky="ew")

    import threading

    def on_click():
        concept = entry.get().strip()
        mode = mode_var.get().lower()
        level = concept_level.get()
        if concept:
            loading_label.config(text="⏳ Loading, please wait...")
            button.config(state="disabled")
            entry.config(state="disabled")

            def run_explanation():
                result = explain(concept, mode, level)

                # Update the GUI back on the main thread
                output.after(0, lambda: display_result(concept, mode, level, result))

            threading.Thread(target=run_explanation).start()

    def display_result(concept, mode, level, result):
        output.config(state='normal')
        output.insert(tk.END, f"📚 Concept: {concept}\n 🧭 Mode:{mode.title()}\n 🎓 Level: {level}\n 💡 Explanation: {result}\n\n")
        output.config(state='disabled')
        output.yview(tk.END)
    
        save_to_history(concept, mode, result)
        entry.delete(0, tk.END)
        entry.focus()
        loading_label.config(text="")  # Clear the loading text
        button.config(state="normal")
        entry.config(state="normal")

    button = tk.Button(
        root,
        text="🪄Explain ", 
        command=on_click,
        font=("Segoe UI", 12, "bold"),
        bg='#1D3557',
        fg='white',
        activebackground='#457B9D',
        relief="raised",
        bd=3
    )
    button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

    history_button = tk.Button(
        root,
        text="📜 View History",
        command=lambda: show_history(root),
        font=("Comic Sans MS", 10, "bold"),
        bg="#FFDEAD",
        fg="black",
        relief="raised",
        bd=2
    )
    history_button.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

    root.bind("<Return>", lambda event: on_click())
    root.bind("<Escape>", lambda event: root.quit())
    root.mainloop()

def show_history(root):
    history_window = tk.Toplevel(root)
    history_window.title("📜 TeachMate - History")
    history_window.configure(bg="#FAF3E0")

    tk.Label(history_window, text="📚 Explanation History", font=("Comic Sans MS", 16, "bold"), fg="purple", bg="#FAF3E0").pack(pady=10)

    history_text = scrolledtext.ScrolledText(history_window,
                                             width=70,
                                             height=25,
                                             font=("Comic Sans MS", 11),
                                             fg="#333333",
                                             bg="#F5FFFA",
                                             wrap=tk.WORD)
    history_text.pack(padx=15, pady=10)

    def clear_history_file():
        try:
            with open("teachmate_history.txt", "w", encoding="utf-8") as file:
                file.write("")
            history_text.config(state='normal')
            history_text.delete("1.0", tk.END)
            history_text.insert(tk.END, "🧹 History cleared successfully.")
            history_text.config(state='disabled')
        except Exception as e:
            history_text.config(state='normal')
            history_text.insert(tk.END, f"\n⚠️ Error clearing history: {str(e)}")
            history_text.config(state='disabled')

    clear_btn = tk.Button(
        history_window,
        text="🧹 Clear History",
        command=clear_history_file,
        font=("Comic Sans MS", 10, "bold"),
        bg="#FF6F61",
        fg="white",
        relief="raised",
        bd=2
    )
    clear_btn.pack(pady=(0, 10))

    try:
        with open("teachmate_history.txt", "r", encoding="utf-8") as file:
            history = file.read()
        history_text.insert(tk.END, history)
    except FileNotFoundError:
        history_text.insert(tk.END, "📭 No history found yet.")

    history_text.config(state='disabled')

# Interactive loop
def main():
    while True:
        print("Welcome to TeachMate your Simple Concept Explainer! (Type 'quit' to exit at any time.) ")
        user_input = input("\nWhat concept do you need explanation for? ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            print("Please enter a valid concept to be explained.")
            continue
        print(explain(user_input, 'simple'))

if __name__ == "__main__":
    explain_gui()




