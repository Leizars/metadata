from flask import Flask, render_template, request, redirect, send_file, url_for
from PIL import Image
import os
import piexif

app = Flask(__name__)
UPLOAD_FOLDER = 'static/cleaned'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cleaned')
def cleaned():
    return render_template('cleaned.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    image = request.files['image']
    if not image:
        return redirect('/cleaned')

    original_filename = image.filename
    filepath = os.path.join(UPLOAD_FOLDER, original_filename)
    image.save(filepath)

    # Load metadata
    img = Image.open(filepath)
    exif_data = img.info.get('exif')

    metadata = {}
    has_metadata = False

    if exif_data:
        try:
            exif_dict = piexif.load(exif_data)
            for ifd in exif_dict:
                if exif_dict[ifd] is None:
                    continue
                for tag in exif_dict[ifd]:
                    try:
                        metadata[str(tag)] = str(exif_dict[ifd][tag])
                        has_metadata = True
                    except Exception:
                        pass
        except Exception:
            pass

    # Clean image and save without metadata
    clean_name = f"cleaned_{original_filename}"
    clean_path = os.path.join(UPLOAD_FOLDER, clean_name)
    img.save(clean_path, "jpeg")

    return render_template('result.html',
                           original_filename=original_filename,
                           clean_filename=clean_name,
                           metadata=metadata,
                           has_metadata=has_metadata)

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.abspath(os.path.join(UPLOAD_FOLDER, filename))
    if not os.path.exists(filepath):
        return f"❌ File not found: {filename}", 404
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
