// Internationalization messages
const messages = {
  zh: {
    "nav.features": "功能特性",
    "nav.docs": "文档",
    "nav.download": "下载",
    "hero.badge": "开源 · 简单 · 高效",
    "hero.title": '基于 FFmpeg 的<span class="accent underline">批量视频</span>处理工具',
    "hero.description": "可视化任务队列、高级编码参数配置，内置 12 种常用工具。支持 Windows、macOS、Linux 三平台，基于 PySide6 与 QFluentWidgets 打造的现代化桌面应用。",
    "hero.downloadButton": "立即下载",
    "hero.githubButton": "查看源码",
    "features.title": "核心功能",
    "features.subtitle": "覆盖视频处理全流程的强大工具集",
    "features.queue.title": "任务队列与批量处理",
    "features.queue.description": "可视化任务卡片实时显示进度、速度、码率与预估大小。SQLite 持久化存储，支持批量添加、重试、取消、删除，拖放文件即可添加任务。",
    "features.encode.title": "高级编码参数",
    "features.encode.description": "编码器选择（软件 / 硬件加速）、CRF / 码率质量控制、分辨率与帧率调整、音频编码、自定义 FFmpeg 命令模板，参数块按需勾选。",
    "features.tools.title": "12 种常用工具",
    "features.tools.description": "音频提取、视频截图、GIF 制作、视频剪切、格式转换、图片压缩、视频拼接、媒体信息、MS Store 徽标、字幕处理、音量归一化、速度调整。",
    "features.crossplatform.title": "跨平台支持",
    "features.crossplatform.description": "原生支持 Windows 10/11、macOS 10.15+ 与 Linux 三大平台，FFmpeg 路径自动检测，开箱即用。",
    "features.hardware.title": "硬件加速",
    "features.hardware.description": "支持 NVIDIA NVENC、Intel QSV、AMD AMF、Apple VideoToolbox 等硬件编码器，大幅缩短编码时间。",
    "features.ui.title": "现代化界面",
    "features.ui.description": "Fluent 设计语言，Windows 11 Mica 效果，深色 / 浅色主题快捷切换，系统托盘集成，内置更新检查与多语言支持。",
    "download.title": "开始你的视频处理之旅",
    "download.desc": "完全本地化运行，不收集任何隐私数据。",
    "download.win.detail": "完整支持硬件加速、右键菜单集成与系统托盘",
    "download.mac.detail": "支持全部功能，首次打开需右键 → 打开",
    "download.linux.detail": "自动检测系统 FFmpeg 路径，开箱即用",
    "download.btn": "获取最新安装包",
    "download.mirror.text": "无法访问 GitHub？请转用迅雷网盘下载",
    "download.mirror.btn": "前往迅雷网盘",
    "docs.nav.tools": "工具一览",
    "docs.nav.requirements": "系统要求",
    "docs.nav.source": "源码运行",
    "docs.kicker": "Documentation",
    "docs.title": "使用文档",
    "docs.description": "这里整理了 12 种工具说明、系统要求与源码运行方式。",
    "docs.tools.title": "12 种常用工具",
    "docs.tools.intro": "从「更多」页面入口网格选择所需工具，进入功能页填写参数后执行。工具任务复用主任务队列，统一显示进度与状态。",
    "docs.tools.audio_extract.name": "音频提取",
    "docs.tools.audio_extract.desc": "从视频提取音轨，转为 MP3 / AAC / WAV / Opus / Vorbis / FLAC",
    "docs.tools.snapshot.name": "视频截图",
    "docs.tools.snapshot.desc": "按时间点截取单帧画面，支持 PNG / JPG / WEBP",
    "docs.tools.gif.name": "GIF 制作",
    "docs.tools.gif.desc": "视频片段转 GIF 动图",
    "docs.tools.cut.name": "视频剪切",
    "docs.tools.cut.desc": "按时间段裁剪视频",
    "docs.tools.convert.name": "音视频格式转换",
    "docs.tools.convert.desc": "容器与编码互转",
    "docs.tools.image_convert.name": "图片格式转换",
    "docs.tools.image_convert.desc": "图片格式互转与质量压缩",
    "docs.tools.concat.name": "视频拼接",
    "docs.tools.concat.desc": "合并多个视频，自动用 scale2ref + setsar 统一分辨率与 SAR",
    "docs.tools.media_info.name": "媒体信息",
    "docs.tools.media_info.desc": "异步探测编码 / 码率 / 时长等详情，结构化中文展示",
    "docs.tools.ms_logo.name": "MS Store 徽标",
    "docs.tools.ms_logo.desc": "一键生成 5 个微软商店徽标（720×1080、1080×1080、300×300、150×150、71×71）",
    "docs.tools.subtitle.name": "字幕处理",
    "docs.tools.subtitle.desc": "提取 / 嵌入硬字幕 / 嵌入软字幕 / 格式转换（SRT / ASS / VTT）",
    "docs.tools.loudnorm.name": "音量归一化",
    "docs.tools.loudnorm.desc": "基于 EBU R128 标准的响度与动态范围归一化",
    "docs.tools.speed.name": "速度调整",
    "docs.tools.speed.desc": "音视频同步变速 / 仅视频 / 仅音频，支持 0.25×–8×+",
    "docs.requirements.title": "系统要求",
    "docs.source.title": "源码运行",
    "guide.sys.os": "<strong>操作系统：</strong>支持 Windows 10/11（推荐）、macOS 10.15+ 与 Linux，三大平台原生运行。",
    "guide.sys.python": "<strong>运行环境：</strong>Python 3.9 及以上版本，推荐使用 uv 进行极速依赖管理。",
    "guide.sys.ffmpeg": "<strong>FFmpeg：</strong>需单独安装并加入系统 PATH，应用启动时自动检测路径，也可在「设置」页面手动指定。",
    "guide.sys.gpu": "<strong>硬件加速：</strong>可选配备 GPU（NVIDIA / Intel / AMD / Apple），用于编码加速；建议内存 4GB 以上。",
    "guide.run.intro": "源码运行与部署流程（开发者 / 高级用户）：",
    "guide.run.code": "# 1. 克隆仓库\ngit clone --recursive https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg.git\ncd Easy-FFmpeg\n\n# 2. 创建并激活虚拟环境\nuv venv\n.venv\\Scripts\\activate        # Windows\nsource .venv/bin/activate     # Unix/macOS\n\n# 3. 安装依赖\nuv pip install -r requirements.txt\nuv pip install -r requirements-win.txt   # Windows 额外依赖\nuv pip install -r requirements-mac.txt   # macOS 额外依赖\n\n# 4. 确保 ffmpeg 已安装并加入 PATH\n#    或在应用「设置」页面手动指定路径\n\n# 5. 运行应用\npython Easy-FFmpeg.py",
    "footer.quote": "“让视频处理变得简单，让创意自由流动。”",
    "footer.github": "GitHub",
    "footer.copyright": "🄯 {year} 天机阁 Fairy Oracle Sanctuary"
  },
  en: {
    "nav.features": "Features",
    "nav.docs": "Docs",
    "nav.download": "Download",
    "hero.badge": "Open Source · Simple · Efficient",
    "hero.title": 'FFmpeg-Powered <span class="accent underline">Batch Video</span> Processing',
    "hero.description": "A visual task queue, advanced encoding parameters, and 12 built-in tools. Supports Windows, macOS, and Linux. A modern desktop app built with PySide6 and QFluentWidgets.",
    "hero.downloadButton": "Download Now",
    "hero.githubButton": "View Source",
    "features.title": "Core Features",
    "features.subtitle": "A powerful toolkit covering the entire video processing workflow",
    "features.queue.title": "Task Queue & Batch Processing",
    "features.queue.description": "Visual task cards with real-time progress, speed, bitrate, and estimated size. SQLite persistent storage, batch add / retry / cancel / delete, drag-and-drop file support.",
    "features.encode.title": "Advanced Encoding",
    "features.encode.description": "Encoder selection (software / hardware acceleration), CRF / bitrate quality control, resolution & frame rate, audio encoding, custom FFmpeg command templates with toggleable parameter blocks.",
    "features.tools.title": "12 Built-in Tools",
    "features.tools.description": "Audio extract, video snapshot, GIF maker, video cut, format convert, image convert, video concat, media info, MS Store logo, subtitle handling, loudness normalization, speed adjustment.",
    "features.crossplatform.title": "Cross-Platform",
    "features.crossplatform.description": "Native support for Windows 10/11, macOS 10.15+, and Linux. FFmpeg path auto-detection, ready to use out of the box.",
    "features.hardware.title": "Hardware Acceleration",
    "features.hardware.description": "Supports NVIDIA NVENC, Intel QSV, AMD AMF, and Apple VideoToolbox hardware encoders to dramatically reduce encoding time.",
    "features.ui.title": "Modern Interface",
    "features.ui.description": "Fluent design language, Windows 11 Mica effect, dark / light theme toggle, system tray integration, built-in update checker, and multi-language support.",
    "download.title": "Start Your Video Processing Journey",
    "download.desc": "Fully local execution, collecting no privacy data.",
    "download.win.detail": "Full support for hardware acceleration, right-click menu, and system tray",
    "download.mac.detail": "Full feature support, right-click → Open on first launch",
    "download.linux.detail": "Auto-detects system FFmpeg path, ready to use",
    "download.btn": "Get Latest Installer",
    "download.mirror.text": "Can't access GitHub? Download via Thunder Drive",
    "download.mirror.btn": "Go to Thunder Drive",
    "docs.nav.tools": "Tools",
    "docs.nav.requirements": "Requirements",
    "docs.nav.source": "Run from Source",
    "docs.kicker": "Documentation",
    "docs.title": "Documentation",
    "docs.description": "Find the 12 tools overview, system requirements, and source code run guide here.",
    "docs.tools.title": "12 Built-in Tools",
    "docs.tools.intro": "Pick a tool from the \"More\" page entry grid, fill in the parameters on the function page, then execute. Tool tasks reuse the main task queue with unified progress and status display.",
    "docs.tools.audio_extract.name": "Audio Extract",
    "docs.tools.audio_extract.desc": "Extract audio tracks from video, convert to MP3 / AAC / WAV / Opus / Vorbis / FLAC",
    "docs.tools.snapshot.name": "Video Snapshot",
    "docs.tools.snapshot.desc": "Capture a single frame at a given time point, PNG / JPG / WEBP",
    "docs.tools.gif.name": "GIF Maker",
    "docs.tools.gif.desc": "Turn a video clip into a GIF animation",
    "docs.tools.cut.name": "Video Cut",
    "docs.tools.cut.desc": "Trim a video by time range",
    "docs.tools.convert.name": "Media Convert",
    "docs.tools.convert.desc": "Container and codec conversion",
    "docs.tools.image_convert.name": "Image Convert",
    "docs.tools.image_convert.desc": "Image format conversion and quality compression",
    "docs.tools.concat.name": "Video Concat",
    "docs.tools.concat.desc": "Merge multiple videos, auto-unify resolution and SAR with scale2ref + setsar",
    "docs.tools.media_info.name": "Media Info",
    "docs.tools.media_info.desc": "Async probe of codec / bitrate / duration, shown in structured format",
    "docs.tools.ms_logo.name": "MS Store Logo",
    "docs.tools.ms_logo.desc": "Generate 5 Microsoft Store logos (720×1080, 1080×1080, 300×300, 150×150, 71×71)",
    "docs.tools.subtitle.name": "Subtitle",
    "docs.tools.subtitle.desc": "Extract / burn-in hard subtitles / embed soft subtitles / convert (SRT / ASS / VTT)",
    "docs.tools.loudnorm.name": "Loudnorm",
    "docs.tools.loudnorm.desc": "Loudness and dynamic range normalization based on EBU R128",
    "docs.tools.speed.name": "Speed",
    "docs.tools.speed.desc": "Audio+video / video-only / audio-only speed change, supports 0.25×–8×+",
    "docs.requirements.title": "Requirements",
    "docs.source.title": "Run from Source",
    "guide.sys.os": "<strong>OS:</strong> Supports Windows 10/11 (recommended), macOS 10.15+, and Linux. Native cross-platform execution.",
    "guide.sys.python": "<strong>Runtime:</strong> Python 3.9 or higher, with uv recommended for fast dependency management.",
    "guide.sys.ffmpeg": "<strong>FFmpeg:</strong> Must be installed separately and added to system PATH. The app auto-detects the path on startup, or you can specify it manually in \"Settings\".",
    "guide.sys.gpu": "<strong>Acceleration:</strong> Optional GPU (NVIDIA / Intel / AMD / Apple) for encoding acceleration; 4GB+ memory advised.",
    "guide.run.intro": "Source code run and deployment flow (for developers / advanced users):",
    "guide.run.code": "# 1. Clone the repository\ngit clone --recursive https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg.git\ncd Easy-FFmpeg\n\n# 2. Create and activate virtual environment\nuv venv\n.venv\\Scripts\\activate        # Windows\nsource .venv/bin/activate     # Unix/macOS\n\n# 3. Install dependencies\nuv pip install -r requirements.txt\nuv pip install -r requirements-win.txt   # Windows extras\nuv pip install -r requirements-mac.txt   # macOS extras\n\n# 4. Ensure ffmpeg is installed and in PATH\n#    or specify the path manually in the app's \"Settings\" page\n\n# 5. Run the application\npython Easy-FFmpeg.py",
    "footer.quote": "\"Making video processing simple, letting creativity flow freely.\"",
    "footer.github": "GitHub",
    "footer.copyright": "🄯 {year} Fairy Oracle Sanctuary"
  }
};

// Language names for display
const languageNames = {
  zh: "简体中文",
  en: "English"
};

// Showcase images per locale (light / dark)
const showcaseImages = {
  zh: {
    light: 'images/zh/thumbnail_full.png',
    dark: 'images/zh/thumbnail_full_black.png'
  },
  en: {
    light: 'images/en/thumbnail_full.png',
    dark: 'images/en/thumbnail_full_black.png'
  }
};

// Current locale
let currentLocale = 'zh';

// Keys whose values contain HTML markup and must be set via innerHTML
const htmlKeys = new Set([
  'hero.title',
  'guide.sys.os', 'guide.sys.python', 'guide.sys.ffmpeg', 'guide.sys.gpu'
]);

// Update all translations
function updateTranslations() {
  localStorage.setItem('locale', currentLocale);

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (messages[currentLocale] && messages[currentLocale][key] !== undefined) {
      if (htmlKeys.has(key)) {
        el.innerHTML = messages[currentLocale][key];
      } else {
        el.textContent = messages[currentLocale][key];
      }
    }
  });

  // Update copyright with year
  const copyrightEl = document.getElementById('copyright');
  if (copyrightEl && messages[currentLocale]["footer.copyright"]) {
    const year = new Date().getFullYear();
    copyrightEl.textContent = messages[currentLocale]["footer.copyright"].replace('{year}', year);
  }

  // Update html lang attribute
  document.documentElement.lang = currentLocale;

  // Update showcase images based on locale
  updateShowcaseImages();
}

// Update showcase images based on current locale
function updateShowcaseImages() {
  const lightImg = document.getElementById('showcase-light');
  const darkImg = document.getElementById('showcase-dark');
  const images = showcaseImages[currentLocale] || showcaseImages.zh;
  if (lightImg) lightImg.src = images.light;
  if (darkImg) darkImg.src = images.dark;
}

// Particle background
function initParticles() {
  const container = document.getElementById('hero-particles');
  if (!container) return;

  const particleCount = 20;

  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';

    const size = Math.random() * 4 + 2;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    particle.style.left = `${Math.random() * 100}%`;

    const duration = Math.random() * 10 + 15;
    particle.style.setProperty('--duration', `${duration}s`);

    const drift = (Math.random() - 0.5) * 200;
    particle.style.setProperty('--drift', `${drift}px`);

    particle.style.animationDelay = `${Math.random() * 20}s`;

    container.appendChild(particle);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  const navEntry = performance.getEntriesByType?.('navigation')?.[0];
  const isReload = navEntry?.type === 'reload';
  if (isReload && window.location.hash) {
    history.replaceState(null, '', window.location.pathname + window.location.search);
  }

  // Element refs
  const langBtn = document.getElementById('langBtn');
  const langDropdown = document.getElementById('langDropdown');
  const currentLangSpan = document.getElementById('currentLang');
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');
  const navbar = document.querySelector('.navbar');

  const closeNavMenu = () => {
    if (!navbar || !navToggle) return;
    navbar.classList.remove('nav-open');
    navToggle.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  };

  if (navMenu) {
    navMenu.addEventListener('click', (event) => {
      event.stopPropagation();
    });
  }

  if (navToggle && navMenu && navbar) {
    navToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      const willOpen = !navbar.classList.contains('nav-open');
      navbar.classList.toggle('nav-open', willOpen);
      navToggle.classList.toggle('open', willOpen);
      navToggle.setAttribute('aria-expanded', String(willOpen));
      if (!willOpen && langDropdown) {
        langDropdown.classList.remove('show');
      }
    });

    navMenu.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        closeNavMenu();
      });
    });
  }

  if (langBtn && langDropdown) {
    langBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      langDropdown.classList.toggle('show');
    });

    document.addEventListener('click', () => {
      langDropdown.classList.remove('show');
      closeNavMenu();
    });

    const langOptions = langDropdown.querySelectorAll('.lang-option');
    langOptions.forEach(option => {
      option.addEventListener('click', () => {
        const newLocale = option.dataset.lang;
        if (newLocale !== currentLocale) {
          langOptions.forEach(opt => opt.classList.remove('active'));
          option.classList.add('active');
          currentLocale = newLocale;
          localStorage.setItem('locale', newLocale);
          if (currentLangSpan) currentLangSpan.textContent = languageNames[newLocale];
          updateTranslations();
        }
      });
    });
  }

  window.addEventListener('resize', () => {
    if (window.innerWidth >= 768) {
      closeNavMenu();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      langDropdown?.classList.remove('show');
      closeNavMenu();
    }
  });

  // Detect browser language on first visit (default zh)
  const savedLocale = localStorage.getItem('locale');
  let detectedLocale = 'zh';

  if (savedLocale && messages[savedLocale]) {
    detectedLocale = savedLocale;
  } else {
    const browserLang = navigator.language.split('-')[0];
    if (messages[browserLang]) {
      detectedLocale = browserLang;
    }
  }

  currentLocale = detectedLocale;
  if (currentLangSpan) {
    currentLangSpan.textContent = languageNames[currentLocale];
  }
  if (langDropdown) {
    langDropdown.querySelectorAll('.lang-option').forEach(opt => {
      opt.classList.toggle('active', opt.dataset.lang === currentLocale);
    });
  }
  updateTranslations();

  // Theme toggle
  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('theme');

  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
    });
  }

  // Particle background
  initParticles();

  // Back to top button
  const backToTop = document.getElementById('backToTop');
  if (backToTop) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) {
        backToTop.classList.add('show');
      } else {
        backToTop.classList.remove('show');
      }
    });

    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
});
