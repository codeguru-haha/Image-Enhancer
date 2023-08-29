$(document).ready(function() {
    $('#enhance-button').click(function() {
        var fileInput = $('#file')[0];
        var formData = new FormData();
        var file = fileInput.files[0];
        
        formData.append('file', file);

        formData.append('brightness', $('#brightness').val());
        formData.append('contrast', $('#contrast').val());
        formData.append('sharpen', $('#sharpen').val());

        $.ajax({
            url: '/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                // Clear the current image
                $('#enhanced-preview').attr('src', '').show();

                // Set the new image URL with a cache-busting parameter
                var enhancedImageUrl = data.enhanced_image + '?' + new Date().getTime();
                $('#enhanced-preview').attr('src', enhancedImageUrl).show();
                console.log("Enhanced image updated");
                // Set the new image URL and show it
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });
    });
});