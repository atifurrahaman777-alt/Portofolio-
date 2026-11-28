(function(){
  if (typeof auth === 'undefined') return;
  var LOCK = { 'tab-sosial': 1, 'tab-feed': 1, 'tab-alat': 1 };
  var known = false, user = null;
  auth.onAuthStateChanged(function(u){ known = true; user = u; });

  function ask(msg){
    setTimeout(function(){
      if (typeof closeSidebar === 'function') closeSidebar();
      var panel = document.getElementById('authPanel'), tog = document.getElementById('auth-toggle');
      if (panel && panel.style.display === 'none' && tog) tog.click();
      var er = document.getElementById('authError');
      if (er) { er.textContent = msg; er.style.display = 'block'; }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 0);
  }
  window.mzNeedLogin = ask;

  var orig = window.showTab;
  if (typeof orig !== 'function') return;
  window.showTab = function(id){
    if (LOCK[id] && !user) {
      ask(known ? 'Masuk dulu untuk memakai fitur ini. Tamu hanya bisa Game dan Musik.' : 'Memeriksa login... coba lagi sebentar.');
      return;
    }
    return orig.apply(this, arguments);
  };
  auth.onAuthStateChanged(function(u){
    if (!u) {
      var act = document.querySelector('.tab.active');
      if (act && LOCK[act.id]) orig('tab-beranda');
    }
  });
})();
