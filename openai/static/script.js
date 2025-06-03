document.addEventListener('DOMContentLoaded', function() {
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
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        console.log('Form submitted');
        e.preventDefault();
        handleImageGeneration();
    });
    
    // Additional direct click handler for the button
    generateBtn.addEventListener('click', function(e) {
        console.log('Generate button clicked');
        e.preventDefault();
        handleImageGeneration();
    });
    
    async function handleImageGeneration() {
        // Get form values
        const prompt = document.getElementById('prompt').value;
        const n = parseInt(document.getElementById('n').value);
        const size = document.getElementById('size').value;
        const responseFormat = document.getElementById('response_format').value;
        const style = document.getElementById('style').value;
        const quality = document.getElementById('quality').value;
        
        console.log('Form values:', { prompt, n, size, responseFormat, style, quality });
        
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
        
        // Show loading spinner
        loadingSpinner.classList.remove('d-none');
        resultsDiv.innerHTML = '';
        generateBtn.disabled = true;
        
        try {
            console.log('Sending API request with data:', requestData);
            // Make API request - use only '/api/images/generate' as the router is already configured
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
            
            // Display the results
            displayResults(data, prompt);
        } catch (error) {
            console.error('Error:', error);
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h4>Error</h4>
                    <p>${error.message}</p>
                </div>
            `;
        } finally {
            // Hide loading spinner
            loadingSpinner.classList.add('d-none');
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
});
