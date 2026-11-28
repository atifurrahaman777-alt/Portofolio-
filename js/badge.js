(function(){
  var PERSON = '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/></svg>';
  ['badgeAvatar','upAvatar'].forEach(function(id){
    var el = document.getElementById(id);
    if (!el) return;
    function fix(){ if (el.textContent.trim() === '?') el.innerHTML = PERSON; }
    fix();
    new MutationObserver(fix).observe(el, {childList:true, characterData:true, subtree:true});
  });
})();
