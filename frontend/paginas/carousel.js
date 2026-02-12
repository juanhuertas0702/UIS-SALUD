// Carrusel
class Carousel {
    constructor() {
        this.slides = document.querySelectorAll('.carousel-slide');
        this.indicators = document.querySelectorAll('.carousel-indicator');
        this.prevBtn = document.getElementById('prev');
        this.nextBtn = document.getElementById('next');
        this.carousel = document.getElementById('carousel');
        this.currentSlide = 0;
        this.totalSlides = this.slides.length;
        this.autoplayInterval = null;
        
        this.init();
    }
    
    init() {
        if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.handlePrev());
        if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.handleNext());
        
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => this.handleIndicatorClick(index));
        });
        
        if (this.carousel) {
            this.carousel.addEventListener('mouseenter', () => this.stopAutoplay());
            this.carousel.addEventListener('mouseleave', () => this.startAutoplay());
        }
        
        this.startAutoplay();
    }
    
    showSlide(n) {
        this.slides.forEach(slide => {
            slide.classList.remove('opacity-100');
            slide.classList.add('opacity-0');
        });
        this.indicators.forEach(indicator => indicator.classList.remove('active'));
        
        this.currentSlide = (n + this.totalSlides) % this.totalSlides;
        this.slides[this.currentSlide].classList.remove('opacity-0');
        this.slides[this.currentSlide].classList.add('opacity-100');
        this.indicators[this.currentSlide].classList.add('active');
    }
    
    nextSlide() {
        this.showSlide(this.currentSlide + 1);
    }
    
    prevSlide() {
        this.showSlide(this.currentSlide - 1);
    }
    
    handleNext() {
        this.nextSlide();
        this.stopAutoplay();
        this.startAutoplay();
    }
    
    handlePrev() {
        this.prevSlide();
        this.stopAutoplay();
        this.startAutoplay();
    }
    
    handleIndicatorClick(index) {
        this.showSlide(index);
        this.stopAutoplay();
        this.startAutoplay();
    }
    
    startAutoplay() {
        this.autoplayInterval = setInterval(() => this.nextSlide(), 5000);
    }
    
    stopAutoplay() {
        clearInterval(this.autoplayInterval);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new Carousel();
});
