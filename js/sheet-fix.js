(function(){
  var root = document.documentElement;
  function sync(){
    var open = !!document.querySelector('.pf-sheet:not([hidden])');
    root.classList.toggle('mz-sheetlock', open);
  }
  new MutationObserver(sync).observe(document.body, {childList:true, subtree:true, attributes:true, attributeFilter:['hidden']});
  document.addEventListener('touchmove', function(e){
    var t = e.target;
    if (t && t.classList && t.classList.contains('pf-sheet')) e.preventDefault();
  }, {passive:false});
  sync();
})();
