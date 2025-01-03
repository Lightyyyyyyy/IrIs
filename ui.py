import tkinter as tk

def start_voice_recognition():
    
    chat_box.insert(tk.END, "Listening...\n")
    chat_box.tag_add("white_text", "1.0", "end")  
    chat_box.after(2000, lambda: chat_box.insert(tk.END, "You said: Hello!\n"))

def round_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Draw a rounded rectangle on the canvas."""
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

root = tk.Tk()
root.title("Voice Assistant")
root.geometry("400x500")  
root.configure(bg="#f4f4f4")  

chat_frame = tk.Frame(root, bg="#f4f4f4")
chat_frame.pack(pady=10, padx=20)

chat_canvas = tk.Canvas(chat_frame, width=360, height=200, bg="#f4f4f4", highlightthickness=0)
chat_canvas.pack()

round_rectangle(chat_canvas, 5, 5, 355, 195, radius=20, fill="black", outline="")
chat_box = tk.Text(chat_canvas, height=10, width=42, bg="black", fg="white", font=("Arial", 12), bd=0, highlightthickness=0)
chat_box.place(x=10, y=10, width=340, height=180)  # Position inside the rounded rectangle
chat_box.insert(tk.END, "Welcome to the Voice Assistant\n")
chat_box.tag_config("white_text", foreground="white")  # Configure white text tag

circle_frame = tk.Frame(root, bg="#f4f4f4")
circle_frame.pack(expand=True)

canvas = tk.Canvas(circle_frame, width=150, height=150, bg="#f4f4f4", highlightthickness=0)
canvas.pack()

circle = canvas.create_oval(10, 10, 140, 140, fill="#003366", outline="")

mic_body = canvas.create_rectangle(65, 40, 85, 90, fill="white", outline="white", width=2)
mic_head = canvas.create_oval(60, 20, 90, 40, fill="white", outline="white", width=2)
mic_base = canvas.create_line(75, 90, 75, 110, width=4, fill="white")
mic_stand = canvas.create_line(65, 110, 85, 110, width=4, fill="white")
canvas.bind("<Button-1>", lambda event: start_voice_recognition())

root.mainloop()
