(function(){
  var KEY = "mz_lang";
  var LANGS = [
    { c: "id", n: "🇮🇩 Indonesia" },
    { c: "en", n: "🇬🇧 English" },
    { c: "zh", n: "🇨🇳 中文" },
    { c: "ja", n: "🇯🇵 日本語" },
    { c: "ko", n: "🇰🇷 한국어" },
    { c: "es", n: "🇪🇸 Español" },
    { c: "fr", n: "🇫🇷 Français" },
    { c: "de", n: "🇩🇪 Deutsch" }
  ];
  var IX = { id: 0, en: 1, zh: 2, ja: 3, ko: 4, es: 5, fr: 6, de: 7 };

  /* Urutan: Indonesia, English, 中文, 日本語, 한국어, Español, Français, Deutsch. */
  var W = {
    "Bahasa": ["Bahasa", "Language", "语言", "言語", "언어", "Idioma", "Langue", "Sprache"],
    "Multifungsi": ["Multifungsi", "Multipurpose", "多功能", "マルチ機能", "다기능", "Multifunción", "Multifonction", "Multifunktional"],
    "Tamu": ["Tamu", "Guest", "访客", "ゲスト", "게스트", "Invitado", "Invité", "Gast"],
    "Beranda": ["Beranda", "Home", "首页", "ホーム", "홈", "Inicio", "Accueil", "Start"],
    "Profil": ["Profil", "Profile", "个人资料", "プロフィール", "프로필", "Perfil", "Profil", "Profil"],
    "Sosial": ["Sosial", "Social", "社交", "ソーシャル", "소셜", "Social", "Social", "Sozial"],
    "Feed": ["Feed", "Feed", "动态", "フィード", "피드", "Feed", "Fil", "Feed"],
    "Game": ["Game", "Games", "游戏", "ゲーム", "게임", "Juegos", "Jeux", "Spiele"],
    "Alat": ["Alat", "Tools", "工具", "ツール", "도구", "Herramientas", "Outils", "Werkzeuge"],
    "Pengaturan": ["Pengaturan", "Settings", "设置", "設定", "설정", "Ajustes", "Paramètres", "Einstellungen"],
    "Musik": ["Musik", "Music", "音乐", "音楽", "음악", "Música", "Musique", "Musik"],
    "Telegram": ["Telegram", "Telegram", "Telegram", "Telegram", "텔레그램", "Telegram", "Telegram", "Telegram"],
    "WhatsApp": ["WhatsApp", "WhatsApp", "WhatsApp", "WhatsApp", "왓츠앱", "WhatsApp", "WhatsApp", "WhatsApp"],
    "Saluran WA": ["Saluran WA", "WA Channel", "WhatsApp频道", "WAチャンネル", "WA 채널", "Canal de WA", "Canal WA", "WA-Kanal"],
    "Saluran Tele": ["Saluran Tele", "Telegram Channel", "Telegram频道", "Telegramチャンネル", "텔레그램 채널", "Canal de Telegram", "Canal Telegram", "Telegram-Kanal"],
    "Masuk": ["Masuk", "Sign in", "登录", "ログイン", "로그인", "Iniciar sesión", "Connexion", "Anmelden"],
    "Daftar": ["Daftar", "Sign up", "注册", "登録", "회원가입", "Registrarse", "Inscription", "Registrieren"],
    "Keluar": ["Keluar", "Sign out", "退出", "ログアウト", "로그아웃", "Cerrar sesión", "Déconnexion", "Abmelden"],
    "Dev": ["Dev", "Dev", "开发者", "開発者", "개발자", "Dev", "Dev", "Entwickler"],
    "Ganti tema": ["Ganti tema", "Switch theme", "切换主题", "テーマを切り替える", "테마 전환", "Cambiar tema", "Changer de thème", "Design wechseln"],
    "Tutup menu": ["Tutup menu", "Close menu", "关闭菜单", "メニューを閉じる", "메뉴 닫기", "Cerrar menú", "Fermer le menu", "Menü schließen"],
    "Pilih akun untuk masuk": ["Pilih akun untuk masuk", "Choose an account to sign in", "选择要登录的账号", "ログインするアカウントを選択", "로그인할 계정 선택", "Elige una cuenta para entrar", "Choisissez un compte", "Konto zum Anmelden wählen"],
    "Lanjutkan dengan Google": ["Lanjutkan dengan Google", "Continue with Google", "使用 Google 继续", "Google で続ける", "Google로 계속", "Continuar con Google", "Continuer avec Google", "Mit Google fortfahren"],
    "Lanjutkan dengan GitHub": ["Lanjutkan dengan GitHub", "Continue with GitHub", "使用 GitHub 继续", "GitHub で続ける", "GitHub로 계속", "Continuar con GitHub", "Continuer avec GitHub", "Mit GitHub fortfahren"],
    "Tentang Saya": ["Tentang Saya", "About Me", "关于我", "私について", "나에 대해", "Sobre mí", "À propos de moi", "Über mich"],
    "Projects": ["Projects", "Projects", "项目", "プロジェクト", "프로젝트", "Proyectos", "Projets", "Projekte"],
    "Skills": ["Skills", "Skills", "技能", "スキル", "기술", "Habilidades", "Compétences", "Fähigkeiten"],
    "Contact": ["Contact", "Contact", "联系方式", "お問い合わせ", "연락처", "Contacto", "Contact", "Kontakt"],
    "KOMUNITAS": ["KOMUNITAS", "COMMUNITY", "社区", "コミュニティ", "커뮤니티", "COMUNIDAD", "COMMUNAUTÉ", "COMMUNITY"],
    "Komunitas Nexcode": ["Komunitas Nexcode", "Nexcode Community", "Nexcode 社区", "Nexcode コミュニティ", "Nexcode 커뮤니티", "Comunidad Nexcode", "Communauté Nexcode", "Nexcode-Community"],
    "ilmu · Tools · Komunitas": ["ilmu · Tools · Komunitas", "knowledge · Tools · Community", "知识 · 工具 · 社区", "知識 · ツール · コミュニティ", "지식 · 도구 · 커뮤니티", "conocimiento · Herramientas · Comunidad", "savoir · Outils · Communauté", "Wissen · Werkzeuge · Community"],
    "Punya ide proyek atau ingin bekerja sama?": ["Punya ide proyek atau ingin bekerja sama?", "Have a project idea or want to collaborate?", "有项目想法或想合作吗？", "プロジェクトのアイデアや協力のご希望は？", "프로젝트 아이디어나 협업을 원하시나요?", "¿Tienes una idea o quieres colaborar?", "Une idée de projet ou une collaboration ?", "Projektidee oder Zusammenarbeit?"],
    "Kirim Pesan": ["Kirim Pesan", "Send Message", "发送消息", "メッセージを送る", "메시지 보내기", "Enviar mensaje", "Envoyer un message", "Nachricht senden"],
    "Nama Anda": ["Nama Anda", "Your Name", "您的名字", "お名前", "이름", "Tu nombre", "Votre nom", "Ihr Name"],
    "Email Anda": ["Email Anda", "Your Email", "您的邮箱", "メールアドレス", "이메일", "Tu correo", "Votre e-mail", "Ihre E-Mail"],
    "Pesan Anda...": ["Pesan Anda...", "Your Message...", "您的消息...", "メッセージ...", "메시지...", "Tu mensaje...", "Votre message...", "Ihre Nachricht..."],
    "Nama": ["Nama", "Name", "姓名", "名前", "이름", "Nombre", "Nom", "Name"],
    "Nama tampilan": ["Nama tampilan", "Display name", "显示名称", "表示名", "표시 이름", "Nombre visible", "Nom affiché", "Anzeigename"],
    "Fitur feed lagi dibangun, bentar lagi nyusul.": ["Fitur feed lagi dibangun, bentar lagi nyusul.", "The feed is under construction, coming soon.", "动态功能正在建设中，敬请期待。", "フィード機能は準備中です。お楽しみに。", "피드 기능을 준비 중입니다. 곧 만나요.", "La función de feed está en construcción.", "Le fil est en construction, bientôt disponible.", "Der Feed wird gerade aufgebaut."],
    "Chat Global": ["Chat Global", "Global Chat", "全球聊天", "グローバルチャット", "글로벌 채팅", "Chat global", "Chat global", "Globaler Chat"],
    "Buka Chat Global": ["Buka Chat Global", "Open Global Chat", "打开全球聊天", "グローバルチャットを開く", "글로벌 채팅 열기", "Abrir chat global", "Ouvrir le chat global", "Globalen Chat öffnen"],
    "Ngobrol, story, dan catatan bareng.": ["Ngobrol, story, dan catatan bareng.", "Chat, stories, and notes together.", "一起聊天、看动态、做笔记。", "チャットやストーリー、ノートを一緒に。", "채팅, 스토리, 메모를 함께.", "Chatea, comparte historias y notas.", "Discutez, partagez des stories et des notes.", "Chatten, Stories und Notizen teilen."],
    "Lawan bot, pilih tingkat kesulitan.": ["Lawan bot, pilih tingkat kesulitan.", "Play the bot, pick a difficulty.", "与机器人对战，选择难度。", "ボットと対戦、難易度を選べる。", "봇과 대결, 난이도 선택.", "Juega contra el bot, elige la dificultad.", "Jouez contre le bot, choisissez la difficulté.", "Gegen den Bot spielen, Schwierigkeit wählen."],
    "Pukul tikus secepat mungkin dalam 30 detik.": ["Pukul tikus secepat mungkin dalam 30 detik.", "Hit the moles as fast as you can in 30 seconds.", "30 秒内尽快打地鼠。", "30秒以内にモグラをたたこう。", "30초 안에 두더지를 최대한 빨리 잡기.", "Golpea los topos lo antes posible en 30 segundos.", "Frappez les taupes en 30 secondes.", "Schlage die Maulwürfe in 30 Sekunden."],
    "Ukur kecepatan reaksimu.": ["Ukur kecepatan reaksimu.", "Measure your reaction speed.", "测试你的反应速度。", "反応速度を測ろう。", "반응 속도를 측정하세요.", "Mide tu velocidad de reacción.", "Mesurez votre temps de réaction.", "Reaktionszeit messen."],
    "Cek kecepatan dan akurasi mengetikmu.": ["Cek kecepatan dan akurasi mengetikmu.", "Check your typing speed and accuracy.", "检查你的打字速度和准确率。", "タイピング速度と正確さをチェック。", "타자 속도와 정확도를 확인하세요.", "Comprueba tu velocidad y precisión al escribir.", "Vérifiez votre vitesse et précision de frappe.", "Tippgeschwindigkeit und Genauigkeit prüfen."],
    "Putar roda dengan pilihanmu sendiri.": ["Putar roda dengan pilihanmu sendiri.", "Spin a wheel with your own choices.", "用你自己的选项转动轮盘。", "自分で決めた選択肢でルーレット。", "내 선택으로 룰렛을 돌려보세요.", "Gira la ruleta con tus propias opciones.", "Faites tourner la roue avec vos choix.", "Drehe das Rad mit eigenen Optionen."],
    "Cari pasangan kartu yang sama.": ["Cari pasangan kartu yang sama.", "Find matching card pairs.", "找出相同的卡片配对。", "同じカードのペアを見つけよう。", "같은 카드 짝을 찾으세요.", "Encuentra las parejas de cartas.", "Trouvez les paires de cartes.", "Finde die passenden Kartenpaare."],
    "Gabungkan angka sampai 2048.": ["Gabungkan angka sampai 2048.", "Combine tiles to reach 2048.", "合并数字，达到 2048。", "数字を合わせて 2048 を目指そう。", "숫자를 합쳐 2048을 만드세요.", "Combina números hasta llegar a 2048.", "Fusionnez les chiffres jusqu'à 2048.", "Zahlen kombinieren bis 2048."],
    "Makan titik, jangan sampai nabrak.": ["Makan titik, jangan sampai nabrak.", "Eat the dots, avoid collisions.", "吃掉圆点，别撞到障碍。", "ドットを食べ、衝突を避けよう。", "점을 먹고 충돌을 피하세요.", "Come los puntos, evita chocar.", "Mangez les points, évitez les collisions.", "Punkte essen, Kollisionen vermeiden."],
    "Tebak Angka": ["Tebak Angka", "Guess the Number", "猜数字", "数字当て", "숫자 맞히기", "Adivina el número", "Devinez le nombre", "Zahl raten"],
    "Tebak angka rahasia 1 sampai 100.": ["Tebak angka rahasia 1 sampai 100.", "Guess the secret number from 1 to 100.", "猜 1 到 100 之间的秘密数字。", "1から100の秘密の数字を当てよう。", "1부터 100까지의 비밀 숫자를 맞히세요.", "Adivina el número secreto del 1 al 100.", "Devinez le nombre secret entre 1 et 100.", "Rate die geheime Zahl von 1 bis 100."],
    "Batu, gunting, kertas lawan bot.": ["Batu, gunting, kertas lawan bot.", "Rock, paper, scissors against the bot.", "与机器人玩石头剪刀布。", "ボットとグー・チョキ・パー。", "봇과 가위바위보 하기.", "Piedra, papel o tijera contra el bot.", "Pierre-papier-ciseaux contre le bot.", "Schere-Stein-Papier gegen den Bot."],
    "Cari": ["Cari", "Search", "搜索", "検索", "검색", "Buscar", "Rechercher", "Suchen"],
    "Putar": ["Putar", "Play", "播放", "再生", "재생", "Reproducir", "Lire", "Abspielen"],
    "Tutup": ["Tutup", "Close", "关闭", "閉じる", "닫기", "Cerrar", "Fermer", "Schließen"],
    "Menu": ["Menu", "Menu", "菜单", "メニュー", "메뉴", "Menú", "Menu", "Menü"],
    "Cari lagu atau artis...": ["Cari lagu atau artis...", "Search songs or artists...", "搜索歌曲或歌手...", "曲やアーティストを検索...", "노래나 아티스트 검색...", "Busca canciones o artistas...", "Rechercher des chansons...", "Lieder oder Künstler suchen..."],
    "Tempel link YouTube...": ["Tempel link YouTube...", "Paste a YouTube link...", "粘贴 YouTube 链接...", "YouTube のリンクを貼り付け...", "YouTube 링크 붙여넣기...", "Pega un enlace de YouTube...", "Collez un lien YouTube...", "YouTube-Link einfügen..."],
    "Masuk / Daftar": ["Masuk / Daftar", "Sign in / Sign up", "登录 / 注册", "ログイン / 登録", "로그인 / 회원가입", "Entrar / Registrarse", "Connexion / Inscription", "Anmelden / Registrieren"],
    "Hari": ["Hari", "Days", "天", "日", "일", "Días", "Jours", "Tage"],
    "Lencana": ["Lencana", "Badges", "徽章", "バッジ", "배지", "Insignias", "Badges", "Abzeichen"],
    "Status": ["Status", "Status", "状态", "ステータス", "상태", "Estado", "Statut", "Status"],
    "Bergabung": ["Bergabung", "Joined", "加入时间", "参加日", "가입일", "Se unió", "Inscrit", "Dabei seit"],
    "Edit Bio & Link": ["Edit Bio & Link", "Edit Bio & Links", "编辑简介和链接", "自己紹介とリンクを編集", "소개 및 링크 수정", "Editar biografía y enlaces", "Modifier la bio et les liens", "Bio und Links bearbeiten"],
    "Tema Warna": ["Tema Warna", "Color Theme", "颜色主题", "カラーテーマ", "색상 테마", "Tema de color", "Thème de couleur", "Farben"],
    "Kembalikan ke Bawaan": ["Kembalikan ke Bawaan", "Restore Defaults", "恢复默认", "初期設定に戻す", "기본값으로 복원", "Restablecer valores", "Réinitialiser", "Zurücksetzen"],
    "Hitam/Putih": ["Hitam/Putih", "Black & White", "黑白", "白黒", "흑백", "Blanco y negro", "Noir et blanc", "Schwarz/Weiß"],
    "Bawaan": ["Bawaan", "Default", "默认", "既定", "기본", "Predeterminado", "Par défaut", "Standard"]
  };

  var MAP = {};
  LANGS.forEach(function(l){
    MAP[l.c] = {};
    Object.keys(W).forEach(function(k){ MAP[l.c][k] = W[k][IX[l.c]]; });
  });

  var SKIP = { SCRIPT: 1, STYLE: 1, SVG: 1, TITLE: 1, NOSCRIPT: 1, OPTION: 1, SELECT: 1 };
  var DYN = { badgeText: 1, upName: 1, pfHint: 1, pfFavNote: 1, authError: 1, status: 1, feed: 1 };
  var rawText = new WeakMap(), rawAttr = new WeakMap(), cur = "id";

  function trText(node, lang){
    var raw = rawText.get(node);
    if (raw === undefined) { raw = node.nodeValue; rawText.set(node, raw); }
    var key = raw.trim();
    if (!key) return;
    var val = MAP[lang][key];
    if (val === undefined) val = key;
    var m = raw.match(/^(\s*)([\s\S]*?)(\s*)$/);
    node.nodeValue = (m ? m[1] : "") + val + (m ? m[3] : "");
  }

  function trAttrs(el, lang){
    var orig = rawAttr.get(el);
    if (!orig) { orig = {}; rawAttr.set(el, orig); }
    ["placeholder", "aria-label", "title", "alt"].forEach(function(a){
      if (!(a in orig)) { var v = el.getAttribute(a); if (v !== null) orig[a] = v; }
      if (!(a in orig)) return;
      var val = MAP[lang][orig[a]];
      if (val !== undefined && el.getAttribute(a) !== val) el.setAttribute(a, val);
    });
  }

  function walk(node, lang){
    if (node.nodeType === 3) { trText(node, lang); return; }
    if (node.nodeType !== 1 || SKIP[node.tagName] || node.hasAttribute("data-no-i18n")) return;
    if (DYN[node.id]) return;
    trAttrs(node, lang);
    for (var c = node.firstChild; c; c = c.nextSibling) walk(c, lang);
  }

  function applyTo(doc, lang){
    if (!doc || !doc.body) return;
    walk(doc.body, lang);
    if (doc.documentElement) doc.documentElement.lang = lang;
  }

  function refresh(){
    applyTo(document, cur);
    var fr = document.getElementById("toolFrame");
    if (fr) { try { applyTo(fr.contentDocument, cur); } catch (e) {} }
  }

  function set(lang, save){
    cur = MAP[lang] ? lang : "id";
    var sel = document.getElementById("mzLangSelect");
    if (sel) sel.value = cur;
    refresh();
    if (save) { try { localStorage.setItem(KEY, cur); } catch (e) {} }
  }

  var sel = document.getElementById("mzLangSelect");
  if (sel) {
    LANGS.forEach(function(l){
      var o = document.createElement("option");
      o.value = l.c;
      o.textContent = l.n;
      sel.appendChild(o);
    });
    sel.addEventListener("change", function(){ set(sel.value, true); });
  }

  var saved = "id";
  try { saved = localStorage.getItem(KEY) || "id"; } catch (e) {}
  set(saved, false);

  var fr = document.getElementById("toolFrame");
  if (fr) fr.addEventListener("load", function(){ try { applyTo(fr.contentDocument, cur); } catch (e) {} });
  document.querySelectorAll(".nav-btn[data-tab]").forEach(function(b){
    b.addEventListener("click", function(){ setTimeout(refresh, 0); });
  });
  var mb = document.getElementById("mzMusicBtn");
  if (mb) mb.addEventListener("click", function(){ setTimeout(refresh, 0); });

  window.mzLang = { get: function(){ return cur; }, set: set, refresh: refresh };
})();
