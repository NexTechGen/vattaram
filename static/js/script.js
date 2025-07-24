let cropper;
const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');

imageInput.addEventListener('change', function (event) {
    const files = event.target.files;
    const done = (url) => {
        imageInput.value = '';
        preview.innerHTML = `<img id="image" src="${url}" />`;
        const image = document.getElementById('image');
        document.getElementById('cropBtn').classList.remove('hidden');
        cropper = new Cropper(image, {
            aspectRatio: 1,
            viewMode: 1,
            autoCropArea: 1,
            crop(event) {
                // You can get the crop data here if needed
            },
        });

        // Add crop button handler
        document.getElementById('cropBtn').addEventListener('click', function () {
            if (cropper) {
                // Get cropped canvas and convert to blob
                cropper.getCroppedCanvas().toBlob((blob) => {
                    // Create new file from blob
                    const file = new File([blob], 'cropped.jpg', { type: 'image/jpeg' });

                    // Create a new FileList and DataTransfer to update the input
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    imageInput.files = dataTransfer.files;

                    // Update preview with cropped image
                    preview.innerHTML = `<img src="${URL.createObjectURL(blob)}" />`;
                }, 'image/jpeg', 0.9);
            }
        });
    };

    if (files && files.length > 0) {
        const reader = new FileReader();
        reader.onload = (e) => {
            done(e.target.result);
        };
        reader.readAsDataURL(files[0]);
    }
});

function enableRegNo() {
    document.querySelector('input[name="reg_no"]').disabled = false;
}


// Auto-hide flash messages after 3 seconds
setTimeout(() => {
    document.querySelectorAll('.flash-message').forEach(el => {
        el.style.transition = 'opacity 0.5s ease';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
    });
}, 3000);
