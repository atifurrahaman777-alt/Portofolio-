(function(){
  var btn = document.getElementById('profilePhotoBtn');
  var rm = document.getElementById('profilePhotoRemove');
  var file = document.getElementById('profilePhotoFile');
  var input = document.getElementById('profilePhotoInput');
  var hint = document.getElementById('profilePhotoHint');
  var preview = document.getElementById('profileAvatarPreview');
  var nameInput = document.getElementById('profileNameInput');
  if (!btn || !file || !input) return;

  function say(msg) {
    hint.textContent = msg;
    hint.style.display = msg ? 'block' : 'none';
  }

  function toSquare(f, size, cb) {
    var reader = new FileReader();
    reader.onload = function() {
      var img = new Image();
      img.onload = function() {
        var c = document.createElement('canvas');
        c.width = c.height = size;
        var side = Math.min(img.width, img.height);
        c.getContext('2d').drawImage(img, (img.width - side) / 2, (img.height - side) / 2, side, side, 0, 0, size, size);
        cb(c.toDataURL('image/jpeg', 0.85));
      };
      img.onerror = function() { cb(null); };
      img.src = reader.result;
    };
    reader.onerror = function() { cb(null); };
    reader.readAsDataURL(f);
  }

  btn.addEventListener('click', function() { file.click(); });

  file.addEventListener('change', function() {
    var f = file.files && file.files[0];
    if (!f) return;
    if (f.type && f.type.indexOf('image/') !== 0) { say('File harus berupa gambar.'); return; }
    say('Memproses foto...');
    toSquare(f, 256, function(data) {
      file.value = '';
      if (!data) { say('Foto tidak bisa dibaca. Coba foto lain (JPG atau PNG).'); return; }
      input.value = data;
      renderAvatar(preview, nameInput.value, data);
      say('Foto disimpan.'); var sv = document.getElementById('profileSaveBtn'); if (sv) sv.click();
    });
  });

  rm.addEventListener('click', function() {
    input.value = '';
    renderAvatar(preview, nameInput.value, '');
    say('Foto dihapus.'); var sv = document.getElementById('profileSaveBtn'); if (sv) sv.click();
  });
})();
