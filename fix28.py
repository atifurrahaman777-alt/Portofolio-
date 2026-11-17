import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-autosave' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

SAVE_FN = '''
  /*mz-autosave*/
  async function saveBorder(){
    var user = auth.currentUser;
    if (!user) return;
    var b = find(cur);
    if (b.owner && !admin) return;
    applyAll();
    try {
      await db.collection('users').doc(user.uid).set({avatarBorder: cur}, {merge:true});
      hint('Bingkai disimpan.');
      setTimeout(function(){ hint(''); }, 1600);
    } catch (e) {
      hint('Gagal menyimpan bingkai, coba lagi.');
    }
  }
'''
CLICK = "var sv = document.getElementById('profileSaveBtn'); if (sv) sv.click();"

s, n1 = re.subn(r'(function applyAll\(\)\{[^\n]*\n)', lambda m: m.group(1) + SAVE_FN, s, count=1)
s, n2 = re.subn(r"(cur = b\.id;\s*setCls\(document\.getElementById\('profileAvatarPreview'\), cur\);)",
                lambda m: m.group(1) + '\n        saveBorder();', s, count=1)
s, n3 = re.subn(r"say\('Foto dipilih\. Tekan Simpan Profil\.'\);",
                lambda m: "say('Foto disimpan.'); " + CLICK, s, count=1)
s, n4 = re.subn(r"say\('Foto dihapus\. Tekan Simpan Profil\.'\);",
                lambda m: "say('Foto dihapus.'); " + CLICK, s, count=1)

print('Simpan bingkai otomatis :', 'OK' if n1 and n2 else 'GAGAL')
print('Simpan foto otomatis    :', 'OK' if n3 else 'GAGAL')
print('Hapus foto otomatis     :', 'OK' if n4 else 'GAGAL')

if not (n1 and n2 and n3 and n4):
    print('Dibatalkan, tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak28')
open(f, 'w', encoding='utf-8').write(s)
print('Selesai.')
