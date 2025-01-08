document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
  
    flashes.forEach(flash => {
      setTimeout(() => {
        flash.style.opacity = '0';
          flash.style.transition = 'opacity 0.5s ease'
        setTimeout(() => {
          flash.remove()
        }, 500)
      }, 2000)
    });
  });