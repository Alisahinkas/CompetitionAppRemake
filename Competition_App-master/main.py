import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import fitz  

class ChronometerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("QuizShow")
        self.master.configure(bg='#2E2E2E')
        self.master.geometry("800x600")

        image = Image.open("alis.png")  
        image = image.resize((150, 150))  
        self.photo = ImageTk.PhotoImage(image)

        self.image_label = tk.Label(master, image=self.photo, bg='#2E2E2E')
        self.image_label.place(x=40, y=40) 
        
        self.amal_label = tk.Label(master, text="AMAL Dijital Sözlük", font=("Arial", 15), bg='#2E2E2E', fg='#30D5C8')
        self.amal_label.place(x=40, y=210)  # Position

        self.amal_label = tk.Label(master, text="Sözcük Yarışması", font=("Impact", 25), bg='#2E2E2E', fg='white')
        self.amal_label.place(x=20, y=250)

        self.label_time = tk.Label(master, text="Süre girin:", bg='#2E2E2E', fg='white')
        self.label_time.pack()

        self.entry_time = tk.Entry(master, bg='#2E2E2E', fg='white')
        self.entry_time.pack()

        self.countdown_frame = tk.Frame(master, bg='#404040')
        self.countdown_frame.pack(side=tk.TOP, pady=(10, 0))
        self.countdown_var = tk.StringVar()
        self.countdown_label = tk.Label(self.countdown_frame, textvariable=self.countdown_var, font=("Arial", 24), bg='#2E2E2E', fg='white')
        self.countdown_label.pack()

        self.start_button = tk.Button(master, text="Kronometreyi Başlat", command=self.start_chronometer, bg='#404040', fg='white', height=3, width=30)
        self.start_button.pack(side=tk.LEFT, padx=(10, 0), pady=(0, 10))

        self.reset_button = tk.Button(master, text="Sıfırla", command=self.reset_chronometer, bg='red', fg='white', height=3, width=15)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 10), pady=(0, 10))
        self.reset_button.config(state=tk.DISABLED)

        self.score_frame = tk.Frame(master, bg='#2E2E2E')
        self.score_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 10))

        self.label_teams = tk.Label(self.score_frame, text="Puanlar", bg='#2E2E2E', fg='white')
        self.label_teams.pack()
        
        self.label_point_change = tk.Label(self.score_frame, text="Puan Değişim Miktarı:", bg='#2E2E2E', fg='white')
        self.label_point_change.pack()

        self.entry_point_change = tk.Entry(self.score_frame, bg='#2E2E2E', fg='white')
        self.entry_point_change.pack()

        self.team_scores = [0, 0, 0, 0, 0]

        self.team_labels = []
        self.team_buttons_plus = []
        self.team_buttons_minus = []

        for i in range(5):
            frame = tk.Frame(self.score_frame, bg='#2E2E2E')
            frame.pack(pady=10)  

            label = tk.Label(frame, text=f"Takım {i + 1}", bg='#2E2E2E', fg='white') 
            label.pack(side=tk.LEFT)

            button_minus = tk.Button(frame, text="-", command=lambda idx=i: self.update_score(idx, -self.get_point_change()), bg='#404040', fg='white', height=2, width=5)
            button_minus.pack(side=tk.LEFT)
            
            score_label = tk.Label(frame, text=str(self.team_scores[i]), bg='#2E2E2E', fg='white')
            score_label.pack(side=tk.LEFT)

            button_plus = tk.Button(frame, text="+", command=lambda idx=i: self.update_score(idx, self.get_point_change()), bg='#404040', fg='white', height=2, width=5)
            button_plus.pack(side=tk.LEFT)

            self.team_labels.append(score_label)
            self.team_buttons_plus.append(button_plus)
            self.team_buttons_minus.append(button_minus)

        self.running = False


        self.pdf_frame = tk.Frame(master)
        self.pdf_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=20)

        self.canvas = tk.Canvas(self.pdf_frame, bg='#2E2E2E')
        self.scrollbar = tk.Scrollbar(self.pdf_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2E2E2E')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_pdf_button = tk.Button(master, text="PDF Yükle", command=self.load_pdf, bg='#404040', fg='white', height=2, width=15)
        self.load_pdf_button.pack(pady=(10, 0))

        self.zoom_factor = 1.0  

        self.zoom_in_button = tk.Button(master, text="Zoom In", command=self.zoom_in, bg='#404040', fg='white', height=2, width=15)
        self.zoom_in_button.pack(pady=(10, 0))


        self.zoom_out_button = tk.Button(master, text="Zoom Out", command=self.zoom_out, bg='#404040', fg='white', height=2, width=15)
        self.zoom_out_button.pack(pady=(10, 0))

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.current_pdf_path = file_path  
            self.display_pdf(file_path)

    def display_pdf(self, file_path):
        pdf_document = fitz.open(file_path)
        self.pdf_images = []  

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num] 
            pix = page.get_pixmap() 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) 
            img = img.resize((int(400 * self.zoom_factor), int(400 * self.zoom_factor)))  
            pdf_image = ImageTk.PhotoImage(img) 
            self.pdf_images.append(pdf_image)  

            pdf_label = tk.Label(self.scrollable_frame, image=pdf_image, bg='#2E2E2E')
            pdf_label.image = pdf_image 
            pdf_label.pack(pady=5)  

    def zoom_in(self):
        self.zoom_factor *= 1.1  
        self.refresh_pdf_display()

    def zoom_out(self):
        self.zoom_factor /= 1.1 
        self.refresh_pdf_display()

    def refresh_pdf_display(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy() 
        self.display_pdf(self.current_pdf_path) 

    def start_chronometer(self):
        if not self.running:
            try:
                target_time = float(self.entry_time.get())
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli bir süre girin.")
                return

            self.label_time.config(text="Kronometre çalışıyor...")
            self.start_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL)

            self.remaining_time = target_time
            self.running = True  
            self.update_countdown()

    def update_countdown(self):
        if self.running:
            if self.remaining_time <= 0:
                messagebox.showinfo("Süre doldu", "Süre doldu.")
                self.running = False  
                self.reset_chronometer()
            else:
                self.countdown_var.set(f"Kalan süre: {self.remaining_time:.2f} saniye")
                self.remaining_time -= 0.01
                self.master.after(10, self.update_countdown)

    def reset_chronometer(self):
        self.entry_time.delete(0, tk.END)
        self.label_time.config(text="Süre girin:")
        self.start_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)
        self.running = False  
        self.countdown_var.set("") 

    def update_score(self, team_index, delta):
        self.team_scores[team_index] += delta
        self.team_labels[team_index].config(text=str(self.team_scores[team_index]))

    def get_point_change(self):
        try:
            return int(self.entry_point_change.get())
        except ValueError:
            return 10


if __name__ == "__main__":
    root = tk.Tk()
    app = ChronometerApp(root)
    root.mainloop()
