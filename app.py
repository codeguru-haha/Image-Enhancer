from flask import Flask, render_template, request
import cv2
import numpy as np
from PIL import Image, ImageEnhance

app = Flask(__name__)

def reduce_red_color(input_image, reduction_factor=0.5):
    # Split the image into its color channels
    b, g, r = cv2.split(input_image)
    
    # Reduce the red channel intensity
    r = cv2.multiply(r, reduction_factor)
    
    # Merge the modified channels back together
    modified_image = cv2.merge((b, g, r))
    
    return modified_image

def enhance_photo(input_path, output_path, brightness_factor=1.2, contrast_factor=1.2):
    # Open the input image
    image = Image.open(input_path)
    
    # Enhance brightness and contrast
    enhancer = ImageEnhance.Brightness(image)
    enhanced_image = enhancer.enhance(brightness_factor)
    

    enhancer = ImageEnhance.Contrast(enhanced_image)
    final_image = enhancer.enhance(contrast_factor)
    
    # Convert PIL image to OpenCV format
    cv_image = cv2.cvtColor(np.array(final_image), cv2.COLOR_RGB2BGR)
    
    # Apply Gaussian blur for noise reduction
    denoised_image = cv2.GaussianBlur(cv_image, (5, 5), 0)
    
    # Convert OpenCV image back to PIL format
    denoised_pil_image = Image.fromarray(cv2.cvtColor(denoised_image, cv2.COLOR_BGR2RGB))

    # Convert PIL image to NumPy array
    denoised_np_image = np.array(denoised_pil_image)

    # Reduce red color
    denoised_reduced_red_image = reduce_red_color(denoised_np_image, reduction_factor=1)

    # Convert the modified NumPy array back to PIL format
    denoised_pil_image_with_reduced_red = Image.fromarray(denoised_reduced_red_image)

    # Save the enhanced and denoised image
    denoised_pil_image_with_reduced_red.save(output_path)
    print("Enhanced, denoised, and reduced red image saved as:", output_path)

    return image, denoised_pil_image_with_reduced_red  # Return the original and modified images
    
    return image, denoised_pil_image  # Return the original and denoised images

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        brightness_factor = float(request.form['brightness'])
        contrast_factor = float(request.form['contrast'])

        input_file_path = "static/myphoto.jpg"
        output_file_path = "static/enhanced_denoised_photo.jpg"
        
        original_image, enhanced_image = enhance_photo(input_file_path, output_file_path, brightness_factor, contrast_factor)
        
        return render_template('index.html', original_image=input_file_path, enhanced_image=output_file_path)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)





