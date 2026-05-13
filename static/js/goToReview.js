async function goToReview() {
    const syllabus = document.getElementById('syllabus').value;
    const apikey = document.getElementById('apikey').value;
    const fileInput = document.getElementById('syllabus-file');
    const file = fileInput && fileInput.files && fileInput.files[0];

    if (!apikey) {
        alert('Please enter an API key');
        return;
    }

    try {
        let response;

        if (file) {
            // upload PDF via multipart/form-data
            const formData = new FormData();
            formData.append('apikey', apikey);
            formData.append('file', file, file.name);

            response = await fetch('/parse-syllabus-file', {
                method: 'POST',
                body: formData
            });
        } else {
            if (!syllabus) {
                alert('Please enter a syllabus or upload a PDF.');
                return;
            }
            response = await fetch('/parse-syllabus', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ syllabus, apikey })
            });
        }

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        // Store the parsed tasks in sessionStorage to access them on the review page
        sessionStorage.setItem('parsedTasks', JSON.stringify(data.tasks || []));
        window.location.href = '/review';
    } catch (error) {
        console.error(error);
        alert('Could not process the syllabus. Check your API key and try again.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const nextButton = document.getElementById('next-button');
    if (nextButton) {
        nextButton.addEventListener('click', goToReview);
    }
});