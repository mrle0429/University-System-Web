document.addEventListener("DOMContentLoaded", () => {
    const leftBackground = document.querySelector('.login-left');
    
    function createParticle() {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // 随机起始位置
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.opacity = Math.random() * 0.5 + 0.3;
        
        // 随机动画延迟和持续时间
        particle.style.animationDelay = `-${Math.random() * 15}s`;
        particle.style.animationDuration = `${Math.random() * 5 + 15}s`;
        
        leftBackground.appendChild(particle);
    }
    
    // 初始创建更多粒子
    for (let i = 0; i < 50; i++) {
        createParticle();
    }

    // 鼠标交互效果
    leftBackground.addEventListener('mousemove', (event) => {
        const rect = leftBackground.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;
        
        const particles = leftBackground.querySelectorAll('.particle');
        particles.forEach(particle => {
            const particleRect = particle.getBoundingClientRect();
            const particleX = particleRect.left - rect.left + particleRect.width / 2;
            const particleY = particleRect.top - rect.top + particleRect.height / 2;
            
            const distanceX = mouseX - particleX;
            const distanceY = mouseY - particleY;
            const distance = Math.sqrt(distanceX * distanceX + distanceY * distanceY);
            
            if (distance < 120) {
                const angle = Math.atan2(distanceY, distanceX);
                const force = (120 - distance) / 120;
                const moveX = Math.cos(angle) * force * 40;
                const moveY = Math.sin(angle) * force * 40;
                
                // 添加额外的变换，但保持原有的动画
                const currentTransform = getComputedStyle(particle).transform;
                particle.style.transform = `${currentTransform} translate(${-moveX}px, ${-moveY}px)`;
            }
        });
    });

    // 鼠标离开时重置粒子
    leftBackground.addEventListener('mouseleave', () => {
        const particles = leftBackground.querySelectorAll('.particle');
        particles.forEach(particle => {
            particle.style.transform = '';
        });
    });
}); 