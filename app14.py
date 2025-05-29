from flask import Flask, request, render_template, send_file, jsonify
import os
import datetime
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
STATIC_FOLDER = "static"
os.makedirs(STATIC_FOLDER, exist_ok=True)

FONT_PATH = os.path.join("fonts", "Arial.ttf")  # ضع هنا مسار خط إنجليزي موجود (مثل Arial أو أي TTF)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    pdf_file = request.files.get('pdf_file')
    if not pdf_file:
        return "Please upload a PDF file", 400

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = f"input_{timestamp}.pdf"
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
    pdf_file.save(pdf_path)

    
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap()
    preview_img_name = f"preview_{timestamp}.png"
    preview_img_path = os.path.join(STATIC_FOLDER, preview_img_name)
    pix.save(preview_img_path)
    doc.close()

    return jsonify({
        "pdf_filename": pdf_filename,
        "preview_img": preview_img_name
    })

@app.route('/add_text', methods=['POST'])
def add_text():
    data = request.json
    pdf_filename = data.get('pdf_filename')
    text = data.get('text')
    page_number = int(data.get('page_number', 0))
    x = float(data.get('x'))
    y = float(data.get('y'))

    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
    if not os.path.exists(pdf_path):
        return jsonify({"error": "PDF file not found"}), 404

    doc = fitz.open(pdf_path)
    if page_number < 0 or page_number >= len(doc):
        doc.close()
        return jsonify({"error": "Invalid page number"}), 400

    page = doc[page_number]
    rect = fitz.Rect(x, y, x + 300, y + 500)

   
    page.insert_textbox(rect, text, fontsize=14, fontname="helv", align=0)  # 'helv' = Helvetica built-in font

    output_filename = f"خبيبي{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    doc.save(output_path)
    doc.close()

    return jsonify({"output_pdf": output_filename})

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
