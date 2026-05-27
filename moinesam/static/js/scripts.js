
document.addEventListener('DOMContentLoaded', function() {
    
    const animateElements = document.querySelectorAll('.request-card, .benefit, .photo-card, .stat-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });
    
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
    });
    
    const currentPath = window.location.pathname;
    document.querySelectorAll('nav a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.classList.add('active-nav');
        }
    });
    
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#ff4757';
                    input.classList.add('shake');
                    
                    setTimeout(() => {
                        input.style.borderColor = '';
                        input.classList.remove('shake');
                    }, 300);
                } else {
                    input.style.borderColor = '';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showNotification('⚠️ Пожалуйста, заполните все обязательные поля', 'error');
            }
        });
    });
    
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `flash ${type}`;
        notification.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i> ${message}`;
        
        const main = document.querySelector('main');
        const firstChild = main.firstChild;
        main.insertBefore(notification, firstChild);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
    
    document.querySelectorAll('.btn, button[type="submit"]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            for (let i = 0; i < 8; i++) {
                const particle = document.createElement('div');
                particle.style.position = 'fixed';
                particle.style.left = (e.clientX - 3) + 'px';
                particle.style.top = (e.clientY - 3) + 'px';
                particle.style.width = '6px';
                particle.style.height = '6px';
                particle.style.background = '#ffd700';
                particle.style.borderRadius = '50%';
                particle.style.pointerEvents = 'none';
                particle.style.zIndex = '9999';
                particle.style.animation = `particleFly ${Math.random() * 0.5 + 0.5}s ease-out forwards`;
                document.body.appendChild(particle);
                
                setTimeout(() => particle.remove(), 500);
            }
        });
    });
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes particleFly {
            0% {
                transform: translate(0, 0) scale(1);
                opacity: 1;
            }
            100% {
                transform: translate(${Math.random() * 60 - 30}px, ${Math.random() * -50 - 20}px) scale(0);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    const cancelReason = document.querySelector('textarea[name="cancel_reason"]');
    if (cancelReason) {
        const counter = document.createElement('div');
        counter.style.cssText = 'font-size: 10px; color: #a0a8c0; margin-top: 5px; text-align: right;';
        counter.innerHTML = '0 / 300';
        cancelReason.parentNode.appendChild(counter);
        
        cancelReason.addEventListener('input', function() {
            const length = this.value.length;
            counter.innerHTML = `${length} / 300`;
            if (length > 280) counter.style.color = '#ffd700';
            else counter.style.color = '#a0a8c0';
        });
    }
    
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(flash => {
            setTimeout(() => {
                flash.style.opacity = '0';
                flash.style.transform = 'translateY(-20px)';
                setTimeout(() => flash.remove(), 300);
            }, 5000);
        });
    }, 100);
    
    console.log('%cМОЙ НЕ САМ — ПРЕМИУМ КЛИНИНГ', 'color: #ffd700; font-size: 14px; font-weight: bold;');
    console.log('%cЧистота, которой доверяют с 500 года', 'color: #00ff9d; font-size: 12px;');
});