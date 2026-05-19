window.addEventListener("scroll", function() {
    let navbar = document.querySelector(".navbar");
    if (navbar) {
        navbar.classList.toggle("scrolled", window.scrollY > 50);
    }
});

setTimeout(() => {
    const imageContainer = document.querySelector('.image-container');
    const videoContainer = document.querySelector('.video-container');
    
    if (imageContainer && videoContainer) {
        imageContainer.style.display = 'none';
        videoContainer.style.display = 'block';
        setTimeout(() => {
            videoContainer.style.opacity = '1';
            const content = document.querySelector('.video-container .content');
            if (content) {
                content.style.top = 'auto';
                content.style.bottom = '10%';
                content.style.transform = 'none';
            }
        }, 50);
    }
}, 2000);
