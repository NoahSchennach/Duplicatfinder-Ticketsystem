const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('show');
    } else {
      entry.target.classList.remove('show'); // wieder ausblenden
    }
  });
}, {
  threshold: 0.1
});





const hiddenElements = document.querySelectorAll('.hidden');
hiddenElements.forEach((el) => observer.observe(el));

hiddenElements.forEach((el, index) => {
  setTimeout(() => observer.observe(el), index * 150); // 150ms Abstand
});
