function dropdown(){
    const text = document.getElementById('explanation')
    text.style.display = 'block'
}

document.addEventListener('DOMContentLoaded', () => {
    const helpButton = document.getElementById('api-help-button')
    if (helpButton) {
        helpButton.addEventListener('click', dropdown)
    }
})