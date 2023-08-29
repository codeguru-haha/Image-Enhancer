from flask import Flask, render_template, request, send_from_directory, jsonify
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/upload'
ENHANCED_FOLDER = 'static/enhancer'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENHANCED_FOLDER'] = ENHANCED_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_image(image, brightness_factor=1.2, contrast_factor=1.2, sharpen_factor=1.3):
    # Enhance brightness and contrast
    enhancer = ImageEnhance.Brightness(image)
    enhanced_image = enhancer.enhance(brightness_factor)

    enhancer = ImageEnhance.Contrast(enhanced_image)
    contrast_enhanced_image = enhancer.enhance(contrast_factor)

    # Convert to numpy array
    cv_image = np.array(contrast_enhanced_image)

    # Convert to BGR color space (OpenCV format)
    cv_image_bgr = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

    # Apply non-local means denoising
    denoised_image_bgr = cv2.fastNlMeansDenoisingColored(cv_image_bgr, None, 10, 10, 7, 21)

    # Apply sharpening
    kernel = np.array([[-1, -1, -1], [-1, sharpen_factor + 9, -1], [-1, -1, -1]])
    sharpened_image_bgr = cv2.filter2D(denoised_image_bgr, -1, kernel)

    # Convert back to RGB color space (PIL format)
    sharpened_image_rgb = cv2.cvtColor(sharpened_image_bgr, cv2.COLOR_BGR2RGB)
    sharpened_pil_image = Image.fromarray(sharpened_image_rgb)

    return sharpened_pil_image


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({'error': 'No selected file'})

        if uploaded_file and allowed_file(uploaded_file.filename):
            # Save uploaded file
            filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(filename)

            # Read the uploaded image
            image = Image.open(filename)

            # Get user-defined enhancement properties
            brightness = float(request.form['brightness'])
            contrast = float(request.form['contrast'])
            sharpen = float(request.form['sharpen'])

            # Enhance the image
            enhanced_image = enhance_image(image, brightness, contrast, sharpen)

            # Create a unique filename for the enhanced image
            enhanced_filename = os.path.join(app.config['ENHANCED_FOLDER'], uploaded_file.filename)
            
            # Save enhanced image
            enhanced_image.save(enhanced_filename)

            # Return the relative URL of the enhanced image
            enhanced_image_url = '/' + enhanced_filename
            return jsonify({'enhanced_image': enhanced_image_url})

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/enhanced/<filename>')
def enhanced_file(filename):
    return send_from_directory(app.config['ENHANCED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=False)
