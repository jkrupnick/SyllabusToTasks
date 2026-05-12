document.addEventListener('DOMContentLoaded', () => {
    const saveButton = document.getElementById('save-button');
    if (saveButton) {
        saveButton.addEventListener('click', handleSave);
    }
});

// Handle user updated tasks and save to Google tasks after clicking save button
async function handleSave() {
    console.log('Save button clicked');
    const originalTasks = JSON.parse(sessionStorage.getItem('parsedTasks') || '[]');
    console.log('Original tasks:', originalTasks);
    const updatedTasks = []

    //loop through original tasks and get updated values from input fields
    for (let i = 0; i < originalTasks.length; i++) {
        try{
            const title = document.getElementById(`title-${i}`).value;

            //get due date and convert to ISO format
            const dueLocal = document.getElementById(`due-${i}`).value;
            let due = null;
            if (dueLocal) {
                const d = new Date(dueLocal + ':00Z');
                due = d.toISOString();
            }
            //add updated task to array
            updatedTasks.push({ title, due });
        } catch (error) {
            console.error(`Error processing task ${i}:`, error);
        }
    }
    console.log('Updated tasks to send:', updatedTasks);
    const response = await fetch('/save-tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tasks: updatedTasks })
    });
    const results = await response.json();
    console.log('Response from server:', results);
}