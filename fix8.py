import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-photo' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
shutil.copy(f, f + '.bak8')

new_ui = '''<input type="text" id="profilePhotoInput" style="display:none">
<input type="file" id="profilePhotoFile" accept="image/*" style="display:none">
<button class="btn" id="profilePhotoBtn" type="button">Pilih Foto dari Galeri</button>
<button class="btn" id="profilePhotoRemove" type="button">Hapus Foto</button>
<p class="muted" id="profilePhotoHint" style="display:none;font-size:.8rem;margin:0"></p>'''

s, n = re.subn(r'<input[^>]*id="profilePhotoInput"[^>]*>', lambda m: new_ui, s, count=1)

js = r'''
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
      say('Foto dipilih. Tekan Simpan Profil.');
    });
  });

  rm.addEventListener('click', function() {
    input.value = '';
    renderAvatar(preview, nameInput.value, '');
    say('Foto dihapus. Tekan Simpan Profil.');
  });
})();
'''

i = s.rfind('</body>')
ok_body = i != -1
if ok_body:
    s = s[:i] + '<script id="mz-photo">' + js + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('Tombol galeri :', 'OK' if n else 'GAGAL (kolom foto tidak ketemu)')
print('Script        :', 'OK' if ok_body else 'GAGAL')
