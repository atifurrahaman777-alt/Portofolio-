const authToggle=document.getElementById('auth-toggle');
const authPanel=document.getElementById('authPanel');
const authPanelClose=document.getElementById('authPanel-close');
if(authPanelClose) authPanelClose.addEventListener('click',()=>{authPanel.style.display='none';});
if(authPanel) authPanel.addEventListener('click',(e)=>{ if(e.target===authPanel) authPanel.style.display='none'; });
document.addEventListener('click',(e)=>{
if(authPanel.style.display!=='none' && !authPanel.contains(e.target) && !authToggle.contains(e.target)){
authPanel.style.display='none';
}
});
const authTabs=document.querySelectorAll('.auth-tab');
const authLoginForm=document.getElementById('authLoginForm');
const authRegisterForm=document.getElementById('authRegisterForm');
const loginEmail=document.getElementById('loginEmail');
const loginPass=document.getElementById('loginPass');
const loginSubmit=document.getElementById('loginSubmit');
const regName=document.getElementById('regName');
const regEmail=document.getElementById('regEmail');
const regPass=document.getElementById('regPass');
const registerSubmit=document.getElementById('registerSubmit');
const authError=document.getElementById('authError');
const logoutBtn=document.getElementById('logoutBtn');
const ownerBadge=document.getElementById('ownerBadge');
const verifiedBadge=document.getElementById('verifiedBadge');
const EYE_ICON='<svg viewBox="0 0 24 24" class="icon"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/></svg>';
const EYEOFF_ICON='<svg viewBox="0 0 24 24" class="icon"><path d="M3 3l18 18"/><path d="M9.9 4.2A11 11 0 0112 4c7 0 11 7 11 7a13.6 13.6 0 01-3.4 4.1M6.1 6.1A13.6 13.6 0 001 11s4 7 11 7a10.8 10.8 0 004.9-1.1"/><path d="M9.5 9.9a3 3 0 004.1 4.2"/></svg>';
const CROWN_ICON='<svg viewBox="0 0 24 24" class="icon"><path d="M3 18h18l-1.5-9-4.5 4-3-6-3 6-4.5-4L3 18z"/></svg>';

function showAuthError(msg){ authError.textContent=msg; authError.style.display='block'; }
function clearAuthError(){ authError.style.display='none'; }

authTabs.forEach(tab=>{
tab.addEventListener('click',()=>{
authTabs.forEach(t=>t.classList.toggle('active',t===tab));
const which=tab.dataset.authTab;
authLoginForm.style.display=which==='login'?'flex':'none';
authRegisterForm.style.display=which==='register'?'flex':'none';
clearAuthError();
});
});

authToggle.addEventListener('click',()=>{
if(typeof closeSidebar==='function') closeSidebar();
authPanel.style.display = authPanel.style.display==='none' ? 'flex' : 'none';
});

registerSubmit.addEventListener('click', async ()=>{
clearAuthError();
const name=regName.value.trim();
const email=regEmail.value.trim();
const pass=regPass.value;
if(!name||!email||pass.length<6){ showAuthError('Isi nama, email, dan password minimal 6 karakter.'); return; }
registerSubmit.disabled=true;
try{
const cred=await auth.createUserWithEmailAndPassword(email,pass);
await db.collection('users').doc(cred.user.uid).set({
name:name, email:email, isAdmin:false, createdAt:firebase.firestore.FieldValue.serverTimestamp()
});
try{ await cred.user.sendEmailVerification(); }catch(e){}
}catch(e){ showAuthError(e.message||'Daftar gagal.'); }
finally{ registerSubmit.disabled=false; }
});

loginSubmit.addEventListener('click', async ()=>{
clearAuthError();
const email=loginEmail.value.trim();
const pass=loginPass.value;
if(!email||!pass){ showAuthError('Isi email dan password.'); return; }
loginSubmit.disabled=true;
try{ await auth.signInWithEmailAndPassword(email,pass); }
catch(e){ showAuthError(e.message||'Masuk gagal.'); }
finally{ loginSubmit.disabled=false; }
});

logoutBtn.addEventListener('click',()=>{ auth.signOut(); });

document.querySelectorAll('.pass-eye[data-eye-for]').forEach(btn=>{
btn.addEventListener('click',()=>{
const input=document.getElementById(btn.dataset.eyeFor);
const isPass=input.type==='password';
input.type=isPass?'text':'password';
btn.innerHTML=isPass?EYEOFF_ICON:EYE_ICON;
});
});

const badgeAvatar=document.getElementById('badgeAvatar');
const badgeText=document.getElementById('badgeText');
const profileEditor=document.getElementById('profileEditor');
const profileAvatarPreview=document.getElementById('profileAvatarPreview');
const profileNameInput=document.getElementById('profileNameInput');
const profilePhotoInput=document.getElementById('profilePhotoInput');
const profileSaveBtn=document.getElementById('profileSaveBtn');
const profileSavedMsg=document.getElementById('profileSavedMsg');

function renderAvatar(container, name, photoURL){
container.innerHTML='';
if(photoURL){
const img=document.createElement('img');
img.src=photoURL;
img.alt='avatar';
img.onerror=function(){ renderAvatar(container, name, ''); };
container.appendChild(img);
}else{
container.textContent=(name||'?').trim().charAt(0).toUpperCase()||'?';
}
}

auth.onAuthStateChanged(async (user)=>{
if(user){
authPanel.style.display='none';
logoutBtn.style.display='block';
profileEditor.style.display='flex';
authTabs.forEach(t=>t.style.display='none');
authLoginForm.style.display='none';
authRegisterForm.style.display='none';
let isAdmin=false, name=user.email, photoURL='';
try{
const doc=await db.collection('users').doc(user.uid).get();
if(doc.exists){ const data=doc.data(); isAdmin=!!data.isAdmin; name=data.name||name; photoURL=data.photoURL||''; }
}catch(e){}
if(isAdmin){
badgeText.innerHTML=CROWN_ICON+' OWNER';
ownerBadge.classList.add('owner-role');
if (verifiedBadge) verifiedBadge.classList.add('owner-role');
}else{
badgeText.textContent=name;
ownerBadge.classList.remove('owner-role');
if (verifiedBadge) verifiedBadge.classList.remove('owner-role');
}
renderAvatar(badgeAvatar, name, photoURL);
renderAvatar(profileAvatarPreview, name, photoURL);
profileNameInput.value=name;
profilePhotoInput.value=photoURL;
window.currentUserProfile={uid:user.uid, isAdmin:isAdmin, name:name, photoURL:photoURL};
}else{
badgeText.textContent='Tamu';
badgeAvatar.textContent='?';
ownerBadge.classList.remove('owner-role');
if (verifiedBadge) verifiedBadge.classList.remove('owner-role');
logoutBtn.style.display='none';
profileEditor.style.display='none';
authTabs.forEach(t=>t.style.display='block');
authLoginForm.style.display='flex';
authRegisterForm.style.display='none';
window.currentUserProfile=null;
}
});

profileSaveBtn.addEventListener('click', async ()=>{
const user=auth.currentUser;
if(!user) return;
const newName=profileNameInput.value.trim();
const newPhoto=profilePhotoInput.value.trim();
if(!newName){ return; }
profileSaveBtn.disabled=true;
try{
await db.collection('users').doc(user.uid).update({name:newName, photoURL:newPhoto});
const isAdmin=window.currentUserProfile?window.currentUserProfile.isAdmin:false;
if(isAdmin){ badgeText.innerHTML=CROWN_ICON+' OWNER'; } else { badgeText.textContent=newName; }
renderAvatar(badgeAvatar, newName, newPhoto);
renderAvatar(profileAvatarPreview, newName, newPhoto);
window.currentUserProfile={uid:user.uid, isAdmin:isAdmin, name:newName, photoURL:newPhoto};
profileSavedMsg.style.display='block';
setTimeout(()=>{ profileSavedMsg.style.display='none'; }, 2000);
}catch(e){
alert('Gagal simpan profil: '+(e.message||'coba lagi'));
}finally{
profileSaveBtn.disabled=false;
}
});

const themeToggle=document.getElementById('theme-toggle');
const SUN_ICON='<svg viewBox="0 0 24 24" class="icon"><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22"/><line x1="4" y1="12" x2="2" y2="12"/><line x1="22" y1="12" x2="20" y2="12"/><line x1="5" y1="5" x2="6.4" y2="6.4"/><line x1="17.6" y1="17.6" x2="19" y2="19"/><line x1="5" y1="19" x2="6.4" y2="17.6"/><line x1="17.6" y1="6.4" x2="19" y2="5"/></svg>';
const MOON_ICON='<svg viewBox="0 0 24 24" class="icon"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg>';
themeToggle.innerHTML=document.body.classList.contains('light-mode')?MOON_ICON:SUN_ICON;
themeToggle.addEventListener('click',()=>{
const light=document.body.classList.toggle('light-mode');
themeToggle.innerHTML=light?MOON_ICON:SUN_ICON;
try{localStorage.setItem('mz-theme',light?'light':'dark');}catch(e){}
});

const navBtns=document.querySelectorAll('.nav-btn[data-tab]');
const tabs=document.querySelectorAll('.tab');
function showTab(id){
tabs.forEach(t=>t.classList.toggle('active',t.id===id));
navBtns.forEach(b=>{b.classList.toggle('active',b.dataset.tab===id);b.classList.toggle('home',b.dataset.tab===id);});
window.scrollTo({top:0});
}

const sidebar=document.getElementById('sidebar');
const sidebarOverlay=document.getElementById('sidebarOverlay');
const menuToggle=document.getElementById('menu-toggle');
const sidebarClose=document.getElementById('sidebar-close');
function openSidebar(){sidebar.classList.add('active');sidebarOverlay.classList.add('active');}
function closeSidebar(){sidebar.classList.remove('active');sidebarOverlay.classList.remove('active');}
if(menuToggle) menuToggle.addEventListener('click',openSidebar);
if(sidebarClose) sidebarClose.addEventListener('click',closeSidebar);
if(sidebarOverlay) sidebarOverlay.addEventListener('click',closeSidebar);

navBtns.forEach(b=>b.addEventListener('click',()=>{showTab(b.dataset.tab);closeSidebar();}));
document.querySelectorAll('[data-goto-tab]').forEach(b=>b.addEventListener('click',()=>{showTab(b.dataset.gotoTab);closeSidebar();}));

const toolCards=document.querySelectorAll('.tool-card[data-tool]');
const toolOverlay=document.getElementById('toolOverlay');
const toolFrame=document.getElementById('toolFrame');
const toolClose=document.getElementById('toolClose');
let toolOpen=false;
function openTool(src){
if(!toolOpen){ try{history.pushState({mzTool:true},'');}catch(e){} }
toolOpen=true;
toolFrame.src=src;
toolOverlay.classList.add('active');
document.body.style.overflow='hidden';
}
function closeTool(toHistory){
if(!toolOpen) return;
toolOpen=false;
toolOverlay.classList.remove('active');
toolFrame.src='';
document.body.style.overflow='';
if(toHistory && history.state && history.state.mzTool) history.back();
}
toolCards.forEach(c=>c.addEventListener('click',()=>openTool(c.dataset.tool)));
if(toolClose) toolClose.addEventListener('click',()=>closeTool(true));
window.addEventListener('popstate',()=>{if(toolOpen) closeTool(false);});
document.addEventListener('keydown',e=>{if(e.key==='Escape' && toolOpen) closeTool(true);});

document.getElementById('year').textContent=new Date().getFullYear();
document.getElementById('form').addEventListener('submit',e=>{
e.preventDefault();
const d=new FormData(e.currentTarget);
const subject=encodeURIComponent('Pesan portofolio dari '+d.get('name'));
const body=encodeURIComponent('Nama: '+d.get('name')+'\nEmail: '+d.get('email')+'\n\n'+d.get('message'));
document.getElementById('status').textContent='Membuka aplikasi email...';
location.href='mailto:mannzz144hz@gmail.com?subject='+subject+'&body='+body;
});
