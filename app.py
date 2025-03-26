from flask import Flask, jsonify, render_template, send_file
import os
import threading

app = Flask(__name__)

# Flash drives to scan
DRIVES = ["E:\\", "F:\\"]
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.mp4', '.ogg'}
cached_media_files = []  # Store scanned media files

# Function to scan media files
def scan_media_files():
    global cached_media_files
    cached_media_files.clear()  # Reset list before scanning
    for drive in DRIVES:
        if os.path.exists(drive):
            for root, _, filenames in os.walk(drive):
                for file in filenames:
                    if os.path.splitext(file)[1].lower() in ALLOWED_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        cached_media_files.append({
                            "filename": file,
                            "path": full_path.replace("\\", "/")  # Fix Windows slashes
                        })
    print(f"Scanned {len(cached_media_files)} media files.")  # Debugging

# Start scanning in a background thread (non-blocking)
scan_thread = threading.Thread(target=scan_media_files, daemon=True)
scan_thread.start()

# API endpoint to get paginated media files
@app.route('/get_media/<int:page>')
def get_media(page):
    per_page = 50  # Load 50 files at a time
    start = (page - 1) * per_page
    end = start + per_page
    return jsonify({
        "files": cached_media_files[start:end],
        "total_files": len(cached_media_files),
        "page": page
    })

# Serve media files dynamically
@app.route('/media/<path:filename>')
def serve_media(filename):
    filename = filename.replace("/", "\\")  # Convert back to Windows path
    if os.path.exists(filename):
        return send_file(filename, as_attachment=False)
    return jsonify({"error": "File not found"}), 404

# Load the main HTML page
@app.route('/')
def index():
    return render_template('player.html')

if __name__ == '__main__':
    app.run(debug=True)
