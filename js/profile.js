(function(){
  var els = {
    avatar: document.getElementById('upAvatar'),
    name: document.getElementById('upName'),
    badge: document.getElementById('upBadge'),
    email: document.getElementById('upEmail'),
    role: document.getElementById('upRole'),
    joined: document.getElementById('upJoined'),
    edit: document.getElementById('upEdit'),
    logout: document.getElementById('upLogout')
  };
  if (!els.avatar || typeof auth === 'undefined') return;

  var BADGE = '<svg viewBox="0 0 24 24" class="badge-icon"><path fill="currentColor" d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/><path fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" d="m9 12 2 2 4-4"/></svg>';

  function render(user, data) {
    if (!user) {
      renderAvatar(els.avatar, '?', '');
      els.name.textContent = 'Tamu';
      els.badge.innerHTML = '';
      els.email.textContent = 'Masuk untuk melihat dan mengatur profilmu.';
      els.role.textContent = 'Tamu';
      els.joined.textContent = '-';
      els.edit.textContent = 'Masuk / Daftar';
      els.logout.style.display = 'none';
      return;
    }
    var name = (data && data.name) || user.displayName || user.email || 'Pengguna';
    var photo = (data && data.photoURL) || '';
    var isAdmin = !!(data && data.isAdmin);
    renderAvatar(els.avatar, name, photo);
    els.name.textContent = name;
    els.badge.innerHTML = '<span class="verified-badge2' + (isAdmin ? ' owner-role' : '') + '">' + BADGE + '</span>';
    els.email.textContent = user.email || '';
    els.role.textContent = isAdmin ? 'Owner' : 'Member';
    var d = null;
    if (data && data.createdAt && data.createdAt.toDate) d = data.createdAt.toDate();
    else if (user.metadata && user.metadata.creationTime) d = new Date(user.metadata.creationTime);
    els.joined.textContent = d ? d.toLocaleDateString('id-ID', {day:'numeric', month:'short', year:'numeric'}) : '-';
    els.edit.textContent = 'Edit Profil';
    els.logout.style.display = 'inline-block';
  }

  async function load(user) {
    if (!user) { render(null, null); return; }
    var data = null;
    try {
      var doc = await db.collection('users').doc(user.uid).get();
      if (doc.exists) data = doc.data();
    } catch (e) {}
    render(user, data);
  }

  auth.onAuthStateChanged(load);

  var saved = document.getElementById('profileSavedMsg');
  if (saved) {
    new MutationObserver(function(){
      if (saved.style.display === 'block') load(auth.currentUser);
    }).observe(saved, {attributes:true, attributeFilter:['style']});
  }

  els.edit.addEventListener('click', function(){
    setTimeout(function(){
      window.scrollTo({top:0});
      var panel = document.getElementById('authPanel');
      if (panel && panel.style.display === 'none') document.getElementById('auth-toggle').click();
    }, 0);
  });
  els.logout.addEventListener('click', function(){ auth.signOut(); });
})();
