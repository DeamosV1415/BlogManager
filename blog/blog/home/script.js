document.addEventListener('DOMContentLoaded', function() {
    console.log('Inko Blog Manager - Home Page Loaded');
    
    // Add entrance animations
    const cards = document.querySelectorAll('.action-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
        }, index * 100);
    });
});