#define MyAppName "ActionVideoRepair"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Oldrey"
#define MyAppExeName "ActionVideoRepair.exe"

[Setup]
AppId={{8B9A7E6D-4D91-4A0C-9F34-ACTIONVIDEOREPAIR}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

SetupIconFile=icono.ico

OutputDir=installer
OutputBaseFilename=ActionVideoRepair_Setup

Compression=lzma
SolidCompression=yes

ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

[Files]
Source: "dist\ActionVideoRepair\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "icono.ico"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{userdocs}\Action Video Repair"

[Icons]
Name: "{autodesktop}\ActionVideoRepair"; Filename: "{app}\ActionVideoRepair.exe"; IconFilename: "{app}\icono.ico"
Name: "{autoprograms}\ActionVideoRepair"; Filename: "{app}\ActionVideoRepair.exe"; IconFilename: "{app}\icono.ico"

[UninstallDelete]
Type: filesandordirs; Name: "{userdocs}\Action Video Repair"

[Run]
Filename: "{app}\ActionVideoRepair.exe"; Description: "Ejecutar ActionVideoRepair"; Flags: nowait postinstall skipifsilent