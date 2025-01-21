// Function to add the animation class when the section is in the viewport
const animateOnScroll = () => {
    const sections = document.querySelectorAll('.section-animate');
    const cards = document.querySelectorAll('.card-animate');

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            // If the section is in the viewport, add the animation class
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');  // Add class to trigger animation
                observer.unobserve(entry.target); // Stop observing this section after animation
            }
        });
    }, {
        threshold: 0.3  // Trigger animation when 30% of the section is visible
    });

    // Observe all sections for animation
    sections.forEach(section => {
        observer.observe(section);
    });

    // Optionally, if you want to animate cards individually with a delay
    let cardDelay = 0.3;  // Start with a small delay for the first card
    cards.forEach(card => {
        card.style.animationDelay = `${cardDelay}s`;
        cardDelay += 0.2;  // Increment delay for each card
        observer.observe(card);
    });
};

// Wait for the DOM content to load before initializing the animations
document.addEventListener("DOMContentLoaded", () => {
    animateOnScroll();  // Trigger animation on scroll for sections and cards
});
