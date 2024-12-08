import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel
import PIL.Image
import PIL.ImageTk
import requests
import os
import qrcode
import pyperclip
import threading

# DISCLAIMER: Some syntax was made with assistance of ClaudeAI & ChatGPT. This project is influence of Filebin on web browser and I wanted to make and run my own filebin locally for security purpose(avoiding malwares).
class FilebinGUI: 
    def __init__(self, master):
        self.master = master
        master.title("Filebin - Easy Cloud File Sharing")
        master.geometry("600x600") # Size of UI
        
        # UI Components (similar to previous version)
        self.file_path_label = tk.Label(master, text="Selected File: None")
        self.file_path_label.pack(pady=10)
        
        self.select_file_button = tk.Button(
            master, 
            text="Select File", 
            command=self.select_file
        )
        self.select_file_button.pack(pady=5)
        
        self.share_file_button = tk.Button(
            master, 
            text="Share File", 
            command=self.share_file,
            state=tk.DISABLED
        )
        self.share_file_button.pack(pady=5)
        
        self.log_area = scrolledtext.ScrolledText(
            master, 
            wrap=tk.WORD, 
            width=70, 
            height=15
        )
        self.log_area.pack(pady=10)
        
        # Buttons for link and QR
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)
        
        self.copy_link_button = tk.Button(
            button_frame, 
            text="Copy Link", 
            command=self.copy_link,
            state=tk.DISABLED
        )
        self.copy_link_button.pack(side=tk.LEFT, padx=5)
        
        self.qr_button = tk.Button(
            button_frame, 
            text="Show QR Code", 
            command=self.show_qr_code,
            state=tk.DISABLED
        )
        self.qr_button.pack(side=tk.LEFT, padx=5)
        
        # Instance variables
        self.selected_file_path = None
        self.share_link = None
        self.qr_image = None
    
    def select_file(self):
        """Open a file dialog to select a file."""
        self.selected_file_path = filedialog.askopenfilename(
            title="Select a file to share",
            filetypes=(("All files", "*.*"),)
        )
        
        if self.selected_file_path:
            short_path = os.path.basename(self.selected_file_path)
            self.file_path_label.config(text=f"Selected File: {short_path}")
            self.share_file_button.config(state=tk.NORMAL)
            self.log("File selected: " + short_path)
    
    def upload_file(self):
        """Upload file to a temporary file hosting service."""
        try:
            # Using file.io for temporary file hosting
            with open(self.selected_file_path, 'rb') as f:
                response = requests.post('https://file.io/', files={'file': f})
            
            if response.status_code == 200:
                # Parse the response for the download link
                self.share_link = response.json().get('link')
                
                if self.share_link:
                    self.log("File uploaded successfully!")
                    return True
                else:
                    self.log("Failed to get upload link")
                    return False
            else:
                self.log(f"Upload failed: {response.text}")
                return False
        except Exception as e:
            self.log(f"Upload error: {str(e)}")
            return False
    
    def generate_qr_code(self, link):
        """Generate a QR code for the link."""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(link)
            qr.make(fit=True)
            
            # Create an image from the QR Code
            self.qr_image = qr.make_image(fill_color="black", back_color="white")
            
            self.log("QR Code generated")
            self.qr_button.config(state=tk.NORMAL)
            self.copy_link_button.config(state=tk.NORMAL)
        except Exception as e:
            self.log(f"QR Code error: {str(e)}")
            messagebox.showerror("QR Code Error", str(e))
    
    def share_file(self):
        """Orchestrate the file sharing process."""
        if not self.selected_file_path:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        # Reset buttons
        self.copy_link_button.config(state=tk.DISABLED)
        self.qr_button.config(state=tk.DISABLED)
        
        # Upload in a separate thread to keep UI responsive
        def upload_thread():
            if self.upload_file():
                # Generate QR Code on the main thread
                self.master.after(0, self.generate_qr_code, self.share_link)
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def show_qr_code(self):
        """Display the QR code in a new window."""
        if self.qr_image:
            # Create a new window
            qr_window = Toplevel(self.master)
            qr_window.title("QR Code")
            
            # Convert PIL Image to PhotoImage
            tk_image = PIL.ImageTk.PhotoImage(self.qr_image)
            
            # Create a label to display the image
            label = tk.Label(qr_window, image=tk_image)
            label.image = tk_image  # Keep a reference!
            label.pack(padx=20, pady=20)
    
    def copy_link(self):
        """Copy share link to clipboard."""
        if self.share_link:
            pyperclip.copy(self.share_link)
            messagebox.showinfo("Link Copied", "Share link copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No share link available")
    
    def log(self, message):
        """Log messages to the scrolled text area."""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)