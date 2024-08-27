import tkinter as tk
from tkinter import ttk
import subprocess

def run_command_bat():
    # Hàm này chạy lệnh từ file run.bat và hiển thị kết quả trên terminal
    loading_label.config(text="Running run.bat...", foreground="blue")
    progress_bar.start()

    # Mở terminal và chạy run.bat ẩn
    process = subprocess.Popen(['cmd.exe', '/c', 'run.bat'], 
                               creationflags=subprocess.CREATE_NO_WINDOW)

    # Đợi cho quá trình hoàn tất
    window.after(100, check_process, process)

def check_process(process):
    # Kiểm tra nếu quá trình đã hoàn thành
    retcode = process.poll()
    if retcode is None:
        # Nếu quá trình vẫn đang chạy, kiểm tra lại sau 100ms
        window.after(100, check_process, process)
    else:
        # Khi quá trình đã hoàn thành, cập nhật giao diện người dùng
        loading_label.config(text="run.bat execution completed.", foreground="green")
        progress_bar.stop()
        progress_bar['value'] = 100  # Thiết lập tiến trình là 100%
        # Đọc nội dung từ file triple.txt và hiển thị
        display_file_content("triples.txt")

def display_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        content_text.config(state=tk.NORMAL)  # Cho phép chỉnh sửa tạm thời
        content_text.delete('1.0', tk.END)  # Xóa nội dung cũ (nếu có)
        content_text.insert(tk.END, content)  # Hiển thị nội dung mới
        content_text.config(state=tk.DISABLED)  # Đặt lại trạng thái chỉ đọc
    except FileNotFoundError:
        content_text.config(state=tk.NORMAL)  # Cho phép chỉnh sửa tạm thời
        content_text.delete('1.0', tk.END)
        content_text.insert(tk.END, "File not found: " + file_path)
        content_text.config(state=tk.DISABLED)  # Đặt lại trạng thái chỉ đọc

# Tạo cửa sổ giao diện
window = tk.Tk()
window.title("Run run.bat in Terminal")
window.geometry("800x600")
window.configure(bg="#f0f0f0")

# Khung chứa các widget
frame = tk.Frame(window, bg="#f0f0f0")
frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

# Label cho thông báo loading
loading_label = tk.Label(frame, text="", font=("Arial", 12), bg="#f0f0f0")
loading_label.pack(pady=10)

# Button chạy lệnh từ run.bat
run_button = tk.Button(frame, text="Run run.bat", command=run_command_bat, font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
run_button.pack(pady=10)

# Progressbar để hiển thị tiến trình
progress_bar = ttk.Progressbar(frame, mode='determinate')
progress_bar.pack(pady=10, fill=tk.X)

# Text widget để hiển thị nội dung file
content_text_frame = tk.Frame(frame, bg="#f0f0f0")
content_text_frame.pack(fill=tk.BOTH, expand=True, pady=20)

content_text = tk.Text(content_text_frame, wrap='word', font=("Arial", 12), state=tk.DISABLED)
content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Hiển thị cửa sổ giao diện
window.mainloop()