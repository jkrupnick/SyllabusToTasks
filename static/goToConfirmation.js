async function goToConfirmation() {
    const syllabus = document.getElementById('syllabus').value;
    const apikey = document.getElementById('apikey').value;

    try {
        const response = await fetch('/parse-syllabus', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ syllabus, apikey })
        });

        if (!response.ok) {
            throw new Error('Failed to parse syllabus');
        }

        const data = await response.json();
        // Store the parsed tasks in sessionStorage to access them on the confirmation page
        sessionStorage.setItem('parsedTasks', JSON.stringify(data.tasks || []));
        window.location.href = '/confirmation';
    } catch (error) {
        console.error(error);
        alert('Could not process the syllabus. Check your API key and try again.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const nextButton = document.getElementById('next-button');
    if (nextButton) {
        nextButton.addEventListener('click', goToConfirmation);
    }
});