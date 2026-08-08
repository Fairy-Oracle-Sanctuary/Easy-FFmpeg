; 脚本由 Inno Setup 脚本向导生成。
; 有关创建 Inno Setup 脚本文件的详细信息，请参阅帮助文档！

#define MyAppName "Easy FFmpeg"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppPublisher "Easy FFmpeg"
#define MyAppURL "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg"
#define MyAppExeName "Easy-FFmpeg.exe"
#define MyAppAssocName MyAppName + "文件"
#define MyAppAssocExt ".myp"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; 注意：AppId 的值唯一标识此应用程序。不要在其他应用程序的安装程序中使用相同的 AppId 值。
; (若要生成新的 GUID，请在 IDE 中单击 "工具|生成 GUID"。)
AppId={{82CA8639-031C-4B26-BA52-0E185B4513E3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
; "ArchitecturesAllowed=x64compatible" 指定安装程序无法运行
; 除 Arm 上的 x64 和 Windows 11 之外的任何平台上。
ArchitecturesAllowed=x64compatible
; "ArchitecturesInstallIn64BitMode=x64compatible" 要求
; 安装可以在 x64 或 Arm 上的 Windows 11 上以“64 位模式”完成，
; 这意味着它应该使用本机 64 位 Program Files 目录和
; 注册表的 64 位视图。
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=LICENSE
; 取消注释以下行以在非管理员安装模式下运行 (仅为当前用户安装)。
PrivilegesRequired=admin
OutputBaseFilename=Easy-FFmpeg-v{#MyAppVersion}-Windows-x86_64-Setup
OutputDir=Output
SolidCompression=yes
; 根据系统语言自动选择安装界面语言，不弹语言选择框
ShowLanguageDialog=no
WizardStyle=modern
SetupIconFile=app\resource\images\logo.ico

[Languages]
#expr EmitLanguagesSection

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "addrightclick"; Description: "{cm:AddRightClick}"; GroupDescription: "{cm:AdditionalIcons}"

[CustomMessages]
; 默认（英文）
AddRightClick=Add "Compress with Easy FFmpeg" to the right-click menu

; 官方支持语言翻译
arabic.AddRightClick=إضافة "ضغط باستخدام Easy FFmpeg" إلى قائمة النقر بزر الماوس الأيمن
armenian.AddRightClick=Ավելացնել «Սեղմել Easy FFmpeg-ով» աջ կտտոցի ընտրացանկում
brazilianportuguese.AddRightClick=Adicionar "Comprimir com Easy FFmpeg" ao menu de contexto
bulgarian.AddRightClick=Добавяне на „Компресирай с Easy FFmpeg“ в контекстното меню
catalan.AddRightClick=Afegeix "Comprimeix amb Easy FFmpeg" al menú contextual
chinesesimplified.AddRightClick=添加右键菜单“用 Easy FFmpeg 压制”
chinesetraditional.AddRightClick=新增右鍵選單「用 Easy FFmpeg 轉檔」
corsican.AddRightClick=Aghjunghje "Cumpressà cù Easy FFmpeg" à u menù di u cliccà dirittu
czech.AddRightClick=Přidat „Komprimovat pomocí Easy FFmpeg“ do místní nabídky
danish.AddRightClick=Tilføj "Komprimer med Easy FFmpeg" til højreklikmenuen
dutch.AddRightClick=Voeg "Comprimeren met Easy FFmpeg" toe aan het contextmenu
finnish.AddRightClick=Lisää "Pakkaa Easy FFmpegillä" hiiren kakkospainikkeen valikkoon
french.AddRightClick=Ajouter « Compresser avec Easy FFmpeg » au menu contextuel
german.AddRightClick="Mit Easy FFmpeg komprimieren" zum Rechtsklickmenü hinzufügen
hebrew.AddRightClick=הוסף "דחוס עם Easy FFmpeg" לתפריט לחיצה ימנית
hungarian.AddRightClick=„Tömörítés Easy FFmpeg-gel” hozzáadása a jobb gombos menühöz
italian.AddRightClick=Aggiungi "Comprimi con Easy FFmpeg" al menu contestuale
japanese.AddRightClick=右クリックメニューに「Easy FFmpeg で圧縮」を追加
korean.AddRightClick=마우스 오른쪽 버튼 메뉴에 "Easy FFmpeg로 압축" 추가
lithuanian.AddRightClick=Pridėti „Suspausti su Easy FFmpeg“ į dešiniojo pelės mygtuko meniu
norwegian.AddRightClick=Legg til «Komprimer med Easy FFmpeg» i høyreklikkmenyen
polish.AddRightClick=Dodaj „Kompresuj za pomocą Easy FFmpeg” do menu kontekstowego
portuguese.AddRightClick=Adicionar "Comprimir com Easy FFmpeg" ao menu de contexto
russian.AddRightClick=Добавить «Сжать с помощью Easy FFmpeg» в контекстное меню
slovak.AddRightClick=Pridať „Komprimovať pomocou Easy FFmpeg“ do kontextovej ponuky
slovenian.AddRightClick=Dodaj »Stisni z Easy FFmpeg« v kontekstni meni
spanish.AddRightClick=Añadir "Comprimir con Easy FFmpeg" al menú contextual
swedish.AddRightClick=Lägg till "Komprimera med Easy FFmpeg" i högerklicksmenyn
tamil.AddRightClick=வலது கிளிக் மெனுவில் "Easy FFmpeg மூலம் சுருக்கு" சேர்
thai.AddRightClick=เพิ่ม "บีบอัดด้วย Easy FFmpeg" ไปยังเมนูคลิกขวา
turkish.AddRightClick=Sağ tıklama menüsüne "Easy FFmpeg ile Sıkıştır" ekle
ukrainian.AddRightClick=Додати «Стиснути за допомогою Easy FFmpeg» до контекстного меню

[InstallDelete]
; 安装前删除旧版本的所有文件和子目录
Type: filesandordirs; Name: "{app}\*"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; tools 显式单独声明：确保 ffmpeg 一定进入 {app}\tools（缺失会直接编译报错）
Source: "dist\Easy-FFmpeg.dist\tools\*"; DestDir: "{app}\tools"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Easy-FFmpeg.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 注意：不要在任何共享系统文件上使用 "Flags: ignoreversion" 

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKCR; Subkey: "*\shell\EasyFFmpeg"; ValueType: string; ValueName: ""; ValueData: "{cm:AddRightClick}"; Tasks: addrightclick; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\shell\EasyFFmpeg"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName},0"; Tasks: addrightclick; Flags: uninsdeletevalue
Root: HKCR; Subkey: "*\shell\EasyFFmpeg\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: addrightclick

; 文件夹右键菜单
Root: HKCR; Subkey: "Directory\shell\EasyFFmpeg"; ValueType: string; ValueName: ""; ValueData: "{cm:AddRightClick}"; Tasks: addrightclick; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\EasyFFmpeg"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName},0"; Tasks: addrightclick; Flags: uninsdeletevalue
Root: HKCR; Subkey: "Directory\shell\EasyFFmpeg\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: addrightclick

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\EasyFFmpeg"

; [Run]
; Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
