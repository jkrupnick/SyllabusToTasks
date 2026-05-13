function dropdown(){
    const text = document.getElementById('explanation')
    text.style.display = text.style.display === 'none' ? 'block' : 'none'
}

document.addEventListener('DOMContentLoaded', () => {
    const helpButton = document.getElementById('api-help-button')
    if (helpButton) {
        helpButton.addEventListener('click', dropdown)
    }
})