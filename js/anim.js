(function(){
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var sel = '.home-hero,.intro-row,.community-card,.about-block,.title,.project,.skill,.contact-block,.tool-card';
  var els = document.querySelectorAll(sel);
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) { e.target.classList.add('mz-in'); io.unobserve(e.target); }
      });
    }, {threshold:.12, rootMargin:'0px 0px -6% 0px'});
    els.forEach(function(el){
      var idx = Array.prototype.indexOf.call(el.parentNode.children, el);
      el.style.transitionDelay = ((idx % 4) * 70) + 'ms';
      el.classList.add('mz-rv');
      io.observe(el);
    });
  }
  var ticking = false;
  window.addEventListener('scroll', function(){
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function(){
      document.body.classList.toggle('mz-scrolled', window.scrollY > 8);
      ticking = false;
    });
  }, {passive:true});
})();
