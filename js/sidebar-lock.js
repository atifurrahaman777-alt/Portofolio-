(function(){
  var sb = document.getElementById('sidebar');
  var ov = document.getElementById('sidebarOverlay');
  if (!sb) return;
  function sync(){
    document.documentElement.classList.toggle('mz-lock', sb.classList.contains('active'));
  }
  new MutationObserver(sync).observe(sb, {attributes:true, attributeFilter:['class']});
  if (ov) ov.addEventListener('touchmove', function(e){ e.preventDefault(); }, {passive:false});
  sync();
})();
