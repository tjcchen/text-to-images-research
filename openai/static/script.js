document.addEventListener('DOMContentLoaded', function () {
    console.log('Document loaded');
    const form = document.getElementById('imageForm');
    const generateBtn = document.getElementById('generateBtn');
    const resultsDiv = document.getElementById('results');
    const loadingSpinner = document.getElementById('loadingSpinner');

    if (!form) {
        console.error('Form element not found!');
        return;
    }

    if (!generateBtn) {
        console.error('Generate button not found!');
        return;
    }

    console.log('Form and button found');

    // Additional direct click handler for the button
    generateBtn.addEventListener('click', function (e) {
        console.log('Generate button clicked');
        e.preventDefault();
        handleImageGeneration();
    });

    // Text overlay form elements
    const textOverlayForm = document.getElementById('textOverlayForm');
    const overlayForm = document.getElementById('overlayForm');
    const opacityInput = document.getElementById('opacity');
    const opacityValue = document.getElementById('opacityValue');
    const bgOpacityInput = document.getElementById('bgOpacity');
    const bgOpacityValue = document.getElementById('bgOpacityValue');
    let currentImageSource = null;

    // Update opacity value display
    opacityInput.addEventListener('input', function () {
        opacityValue.textContent = `${this.value}%`;
    });

    bgOpacityInput.addEventListener('input', function () {
        bgOpacityValue.textContent = `${this.value}%`;
    });

    async function handleImageGeneration() {
        // Get form values
        const prompt = document.getElementById('prompt').value;
        const n = parseInt(document.getElementById('n').value);
        const size = document.getElementById('size').value;
        const responseFormat = document.getElementById('response_format').value;
        const style = document.getElementById('style').value;
        const quality = document.getElementById('quality').value;
        const chineseText = document.getElementById('chineseText').value;
        const fontSize = parseInt(document.getElementById('fontSize').value);
        const textColor = document.getElementById('textColor').value;
        const opacity = parseInt(document.getElementById('opacity').value) / 100;
        const align = document.getElementById('textAlign').value;
        const positionX = parseInt(document.getElementById('positionX').value);
        const positionY = parseInt(document.getElementById('positionY').value);
        const bgColor = document.getElementById('bgColor').value;
        const bgOpacity = parseInt(document.getElementById('bgOpacity').value) / 100;
        const padding = parseInt(document.getElementById('padding').value);
        const borderRadius = parseInt(document.getElementById('borderRadius').value);

        // Convert hex color to RGB
        const r = parseInt(textColor.slice(1, 3), 16);
        const g = parseInt(textColor.slice(3, 5), 16);
        const b = parseInt(textColor.slice(5, 7), 16);
        const bgr = parseInt(bgColor.slice(1, 3), 16);
        const bgg = parseInt(bgColor.slice(3, 5), 16);
        const bgb = parseInt(bgColor.slice(5, 7), 16);

        console.log('Form values:', { prompt, n, size, responseFormat, style, quality, chineseText, fontSize, textColor, opacity, align, positionX, positionY, bgColor, bgOpacity, padding, borderRadius });

        // If prompt is empty, use static/image.jpg as background and call overlay API directly
        if (!prompt.trim()) {
            // Fetch the default image as base64
            const resp = await fetch('/static/image.jpg');
            const blob = await resp.blob();
            const base64Image = await blobToBase64(blob);
            const imageSource = base64Image.replace(/^data:image\/[^;]+;base64,/, '');
            // Call overlay API
            try {
                if (loadingSpinner) loadingSpinner.classList.remove('d-none');
                if (resultsDiv) resultsDiv.innerHTML = '';
                generateBtn.disabled = true;
                const overlayResp = await fetch('/api/images/add-text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image_source: imageSource,
                        text: chineseText,
                        font_size: fontSize,
                        position: [positionX, positionY],
                        color: [r, g, b],
                        opacity: opacity,
                        align: align,
                        bg_color: [bgr, bgg, bgb],
                        bg_opacity: bgOpacity,
                        padding: padding,
                        border_radius: borderRadius
                    })
                });
                if (!overlayResp.ok) {
                    throw new Error(`Overlay error ${overlayResp.status}: ${await overlayResp.text()}`);
                }
                const overlayData = await overlayResp.json();
                // Display the result
                displayResults({ images: [overlayData.image], prompt: prompt }, prompt);
            } catch (error) {
                console.error('Error:', error);
                if (resultsDiv) {
                    resultsDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <h4>Error</h4>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
            } finally {
                if (loadingSpinner) loadingSpinner.classList.add('d-none');
                generateBtn.disabled = false;
            }
            return;
        }

        // Validate form
        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }

        if (n < 1 || n > 10) {
            alert('Number of images must be between 1 and 10');
            return;
        }

        // Prepare request data
        const requestData = {
            prompt: prompt,
            n: n,
            size: size,
            response_format: responseFormat,
            style: style,
            quality: quality
        };

        // Force b64_json if Chinese text is present
        if (chineseText) {
            requestData.response_format = 'b64_json';
        }

        // Show loading spinner
        if (loadingSpinner) loadingSpinner.classList.remove('d-none');
        if (resultsDiv) resultsDiv.innerHTML = '';
        generateBtn.disabled = true;

        try {
            console.log('Sending API request with data:', requestData);
            const apiUrl = '/api/images/generate';
            console.log('API URL:', apiUrl);

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
            }

            const data = await response.json();

            // Debug logging
            console.log('API Response:', data);

            // If Chinese text is provided, overlay it automatically
            if (chineseText && data.images && data.images.length > 0) {
                console.log('Chinese text detected, preparing to overlay:', chineseText);
                let imageSource = data.images[0];
                // Always base64 now
                imageSource = imageSource.replace(/^data:image\/[^;]+;base64,/, '');
                console.log('Calling overlay API with image source (first 100 chars):', imageSource.slice(0, 100));
                const overlayResp = await fetch('/api/images/add-text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image_source: imageSource,
                        text: chineseText,
                        font_size: fontSize,
                        position: [positionX, positionY],
                        color: [r, g, b],
                        opacity: opacity,
                        align: align,
                        bg_color: [bgr, bgg, bgb],
                        bg_opacity: bgOpacity,
                        padding: padding,
                        border_radius: borderRadius
                    })
                });
                if (!overlayResp.ok) {
                    throw new Error(`Overlay error ${overlayResp.status}: ${await overlayResp.text()}`);
                }
                const overlayData = await overlayResp.json();
                console.log('Overlay API response:', overlayData);
                data.images[0] = overlayData.image;
            }

            // Now display the results
            displayResults(data, prompt);
        } catch (error) {
            console.error('Error:', error);
            if (resultsDiv) {
                resultsDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <h4>Error</h4>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        } finally {
            // Hide loading spinner
            if (loadingSpinner) loadingSpinner.classList.add('d-none');
            generateBtn.disabled = false;
        }
    }

    function displayResults(data, prompt) {
        console.log('Displaying results:', data);
        
        if (!data || !data.images || !Array.isArray(data.images) || data.images.length === 0) {
            resultsDiv.innerHTML = `
                <div class="alert alert-warning">
                    <h4>No images returned</h4>
                    <p>The API didn't return any images for prompt: "${prompt}"</p>
                    <p>Response data: ${JSON.stringify(data)}</p>
                </div>
            `;
            return;
        }
        
        resultsDiv.innerHTML = `
            <p class="prompt-text">"${prompt}"</p>
        `;
        
        // Display each image
        data.images.forEach((image, index) => {
            const imgElement = document.createElement('img');
            imgElement.className = 'result-image mb-3';
            imgElement.alt = `Generated image ${index + 1} for: ${prompt}`;
            
            // Handle both URL and base64 formats
            if (image.startsWith('http')) {
                imgElement.src = image;
            } else {
                imgElement.src = `data:image/png;base64,${image}`;
            }
            
            resultsDiv.appendChild(imgElement);
            
            // Add download button for each image
            const downloadBtn = document.createElement('a');
            downloadBtn.className = 'btn btn-sm btn-outline-primary mb-4 d-block';
            downloadBtn.innerHTML = 'Download Image';
            downloadBtn.setAttribute('download', `dalle-image-${Date.now()}-${index}.png`);
            
            if (image.startsWith('http')) {
                downloadBtn.href = image;
            } else {
                downloadBtn.href = `data:image/png;base64,${image}`;
            }
            
            resultsDiv.appendChild(downloadBtn);
        });
    }

    // Helper to convert blob to base64
    async function blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }
});
