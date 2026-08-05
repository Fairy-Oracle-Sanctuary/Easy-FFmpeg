from PySide6.QtCore import QObject


class Text(QObject):
    def __init__(self):
        super().__init__()
        # common
        self.Success = self.tr("成功")
        self.Error = self.tr("错误")
        self.Warning = self.tr("警告")
        self.OK = self.tr("确定")
        self.Cancel = self.tr("取消")
        self.Default = self.tr("默认")
        self.Close = self.tr("关闭")
        self.All = self.tr("全部")

        # task
        self.Waiting = self.tr("等待")
        self.Processing = self.tr("处理中")
        self.Done = self.tr("完成")
        self.Failed = self.tr("失败")
        self.Cancelling = self.tr("取消中")
        self.Cancelled = self.tr("已取消")
        self.TaskType = self.tr("任务类型")
        self.TaskCompleted = self.tr("{} {}已完成")
        self.TaskFailed = self.tr("{} {}任务失败：{}")
        self.TaskSuccessTitle = self.tr("{}任务完成")
        self.TaskFailedTitle = self.tr("{}任务失败")

        # home
        self.MediaFiles = self.tr("媒体文件")

        # setting
        self.Settings = self.tr("设置")
        self.Personalization = self.tr("个性化")
        self.ApplicationTheme = self.tr("应用主题")
        self.AAA = self.tr("调整应用的外观")
        self.Light = self.tr("浅色")
        self.Dark = self.tr("深色")
        self.FollowSystem = self.tr("跟随系统设置")
        self.ThemeColor = self.tr("主题色")
        self.AdjustThemeColor = self.tr("调整应用的主题颜色")
        self.SeafoamGreen = self.tr("海沫绿")
        self.InterfaceScaling = self.tr("界面缩放")
        self.ACAFS = self.tr("调整组件和字体的大小")
        self.Language = self.tr("语言")
        self.SetInterfaceLanguage = self.tr("设置界面语言")
        self.CloseDirectly = self.tr("直接关闭")
        self.EODDC = self.tr("启用或禁用直接关闭应用")
        self.DetectPrograms = self.tr("检测程序")
        self.ADAUPP = self.tr("自动检测并更新程序路径")
        self.About = self.tr("关于")
        self.CheckForUpdates = self.tr("检查更新")
        self.Checking = self.tr("检查中...")
        self.Copyleft = self.tr("Copyleft")
        self.CurrentVersion = self.tr("当前版本")
        self.SelectFile = self.tr("选择文件")
        self.Rely = self.tr("依赖")
        self.Detect = self.tr("检测")
        self.UpdateSuccessful = self.tr("更新成功")
        self.STEAR = self.tr("配置在重启软件后生效")
        self.DetectionSuccessful = self.tr("检测成功")
        self.PathSetTo = self.tr("{}路径已设置为{}")
        self.NotFoundDownloadIt = self.tr("未检测到{}程序，是否要下载")
        self.GoToDownload = self.tr("前往下载")
        self.Detecting = self.tr("检测中...")
        self.NewVersionDetected = self.tr("检测到新版本")
        self.NewVersion = self.tr("新版本")
        self.ADYWTDI = self.tr("可用，你是否要下载新版本？")
        self.NoNewVersion = self.tr("没有新版本")
        self.FKWIUTD = self.tr("Easy FFmpeg 已是最新版本")
        self.SelectFfmpegFile = self.tr("选择ffmpeg文件")

        # advance interface
        self.FilterConfigHint = self.tr(
            "勾选需要启用的参数块，未勾选的将不会加入 FFmpeg 命令"
        )
        self.FilterEncoder = self.tr("编码器")
        self.FilterQuality = self.tr("质量控制")
        self.FilterPreset = self.tr("编码速度")
        self.FilterResolution = self.tr("分辨率")
        self.FilterFrameRate = self.tr("帧率")
        self.FilterAudio = self.tr("音频")
        self.FilterExtra = self.tr("进阶设置")
