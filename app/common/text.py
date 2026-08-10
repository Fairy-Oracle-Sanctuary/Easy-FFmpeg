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

        # task interface / task card
        self.NoTasks = self.tr("目前没有任务")
        self.Pressing = self.tr("压制中")
        self.DeleteSelectedConfirm = self.tr("确定删除选中的任务吗？")
        self.TasksAdded = self.tr("已添加 {} 个任务，过滤 {} 个重复任务")
        self.TaskAddedName = self.tr("已添加任务：{}")
        self.FileInQueue = self.tr("该文件已在任务队列中")
        self.Notice = self.tr("提示")
        self.Retry = self.tr("重试")
        self.Delete = self.tr("删除")
        self.SelectAll = self.tr("全选")
        self.TaskFinished = self.tr("任务已完成：{}")
        self.TaskFailedName = self.tr("任务失败：{}")
        self.PassOneAnalyze = self.tr("第一遍分析")
        self.PassTwoEncode = self.tr("第二遍编码")
        self.StatusWaiting = self.tr("等待中")
        self.StatusPending = self.tr("初始化中")
        self.StatusCancelling = self.tr("正在取消")
        self.ShowInFolder = self.tr("在文件夹中显示")
        self.CancelTask = self.tr("取消任务")
        self.RetryTask = self.tr("重试任务")
        self.ViewLog = self.tr("查看日志")
        self.RemoveTask = self.tr("移除任务")
        self.DeleteTask = self.tr("删除任务")
        self.ConfirmDeleteTask = self.tr("确认删除任务吗？")
        self.DeleteFile = self.tr("删除文件")

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

        # setting interface cards
        self.Software = self.tr("软件")
        self.HomeRecursive = self.tr("递归遍历文件夹")
        self.HomeRecursiveDesc = self.tr("添加文件夹时是否递归遍历子文件夹中的媒体文件")
        self.RetryUseCurrentSettings = self.tr("重试任务使用当前设置")
        self.RetryUseCurrentSettingsDesc = self.tr(
            "重试时按当前高级设置重新构建参数，而非使用添加任务时的参数"
        )
        self.AutoCleanLogs = self.tr("自动清理过期日志")
        self.AutoCleanLogsDesc = self.tr("启动时自动删除超过保留期限的日志文件")
        self.LogRetentionDays = self.tr("日志保留天数")
        self.LogRetentionDaysDesc = self.tr("超过该天数的日志文件将在启动时自动清理")
        self.NDays = self.tr("{} 天")
        self.MicaEffect = self.tr("云母效果")
        self.MicaEffectDesc = self.tr("窗口和表面显示半透明")
        self.CheckUpdateAtStartUp = self.tr("在软件启动时检查更新")
        self.CheckUpdateAtStartUpDesc = self.tr("新版本更稳定且具有更多功能(推荐开启)")

        # main window
        self.Home = self.tr("主页")
        self.Task = self.tr("任务")
        self.Advance = self.tr("高级")
        self.More = self.tr("更多")
        self.NewVersionAvailable = self.tr("新版本 v{} 可用")
        self.DownloadInstaller = self.tr("下载安装包")
        self.Downloading = self.tr("下载中...")
        self.OpenFolder = self.tr("打开文件夹")
        self.InstallerDownloadedTo = self.tr("\n安装包已下载到：{}")
        self.DownloadFailed = self.tr("\n下载失败：{}")
        self.NoReleaseNotes = self.tr("暂无更新说明")
        self.OpenFile = self.tr("打开文件")
        self.UnhandledException = self.tr("发生未处理异常")
        self.UnhandledExceptionDesc = self.tr(
            "报错信息已写入系统粘贴板和日志文件，是否立即反馈？"
        )
        self.MinimizedToTray = self.tr("程序已最小化到系统托盘")

        # info card
        self.Update = self.tr("更新")
        self.Version = self.tr("版本")
        self.UpdateTime = self.tr("更新时间")
        self.LogUsage = self.tr("日志占用")
        self.AppDescription = self.tr(
            "Easy FFmpeg 是一个基于 FFmpeg 的视频处理工具，用于批量处理视频文件，操作简单易用。"
        )
        self.Test = self.tr("测试")
        self.ClearLogsToolTip = self.tr("清理日志文件")
        self.ResetSettingsToolTip = self.tr("重置设置并重启")
        self.WebsiteToolTip = self.tr("软件官网")
        self.GitHubToolTip = self.tr("GitHub 仓库")
        self.ClearLogs = self.tr("清理日志")
        self.ClearLogsConfirm = self.tr(
            "确定要清空所有日志文件吗？当前占用 {}，此操作不可撤销。"
        )
        self.LogsCleared = self.tr("已清理 {} 个日志文件")
        self.LogsSkipped = self.tr("，{} 个被占用跳过")
        self.ResetSettings = self.tr("重置设置")
        self.ResetSettingsConfirm = self.tr(
            "确定要重置所有设置并重启应用吗？此操作不可撤销。"
        )

        # more interface - common
        self.Files = self.tr("文件")
        self.VideoFiles = self.tr("视频文件")
        self.AudioVideoFiles = self.tr("音视频文件")
        self.ImageFiles = self.tr("图片文件")
        self.AllFiles = self.tr("所有文件")
        self.SelectInputFileHint = self.tr("选择输入文件...")
        self.Execute = self.tr("执行")
        self.SelectVideoFiles = self.tr("选择视频文件")
        self.FilesSelected = self.tr("已选 {} 个文件")

        # more interface - placeholder
        self.FeatureInDevelopment = self.tr("功能开发中")
        self.FeatureInDevelopmentHint = self.tr("该功能正在开发中，敬请期待。")

        # more interface - format names
        self.FmtWav = self.tr("WAV (无损 PCM)")
        self.FmtFlac = self.tr("FLAC (无损)")
        self.FmtPng = self.tr("PNG (无损)")
        self.FmtBmp = self.tr("BMP (无损)")
        self.OriginResolution = self.tr("原分辨率")

        # more interface - audio extract
        self.AudioExtract = self.tr("音频提取")
        self.AudioExtractDesc = self.tr("从视频提取音轨")
        self.AudioFormat = self.tr("音频格式：")
        self.AudioBitrate = self.tr("码率：")
        self.AudioBitrateHint = self.tr("码率，如 192k（仅对有损格式生效，留空=默认）")

        # more interface - video snapshot
        self.VideoSnapshot = self.tr("视频截图")
        self.VideoSnapshotDesc = self.tr("按时间点截取视频帧")
        self.TimePoint = self.tr("时间点：")
        self.TimePointHint = self.tr("截图时间点，如 90 或 00:01:30（留空=首帧）")
        self.ImageFormat = self.tr("图片格式：")

        # more interface - gif
        self.GifMake = self.tr("GIF 制作")
        self.GifMakeDesc = self.tr("视频转 GIF 动图")
        self.StartTime = self.tr("起始时间：")
        self.StartTimeHint = self.tr("起始时间，如 00:00:05（留空=从头）")
        self.Duration = self.tr("持续时间：")
        self.DurationHint = self.tr("持续时间，如 3（留空=到结尾）")
        self.Width = self.tr("宽度：")
        self.FrameRate = self.tr("帧率：")

        # more interface - video cut
        self.VideoCut = self.tr("视频剪切")
        self.VideoCutDesc = self.tr("按时间段裁剪视频")
        self.CutStartHint = self.tr("起始时间，如 00:00:10")
        self.CutDurationHint = self.tr("持续时间，如 30 或 00:00:30")
        self.CutMode = self.tr("剪切模式：")
        self.ModeFastCopy = self.tr("快速复制（不重编码）")
        self.ModeAccurateCut = self.tr("精确剪切（重编码）")

        # more interface - media convert
        self.MediaConvert = self.tr("音视频格式转换")
        self.MediaConvertDesc = self.tr("MP4/MKV/MP3/WAV 等容器与编码转换")
        self.OutputFormat = self.tr("输出格式：")

        # more interface - image convert
        self.ImageConvert = self.tr("图片格式转换")
        self.ImageConvertDesc = self.tr("PNG/JPG/WebP/BMP 等格式互转")
        self.Quality = self.tr("质量：")
        self.QualityHint = self.tr("质量，如 2（仅 JPG/WebP，范围 2-31，越小越好）")

        # more interface - video concat
        self.VideoConcat = self.tr("视频拼接")
        self.VideoConcatDesc = self.tr("合并多个视频文件")
        self.ConcatContent = self.tr("拼接内容：")
        self.ConcatHint = self.tr(
            "提示：文件需含对应轨道；输出为 MP4。可拖入或选择多个文件。"
        )
        self.ConcatAv = self.tr("音视频")
        self.ConcatVideo = self.tr("仅视频")

        # more interface - media info
        self.MediaInfo = self.tr("媒体信息")
        self.MediaInfoDesc = self.tr("查看编码/码率/时长等详细信息")
        self.MediaInfoPlaceholder = self.tr(
            "选择文件后点击执行，查看编码/码率/时长等详细信息"
        )
        self.Probing = self.tr("正在探测...")
        self.FailToStartFfmpeg = self.tr("无法启动 ffmpeg：{}")
        self.NoInfo = self.tr("未获取到信息")
        self.NoInfoParsed = self.tr("未解析到信息")
        self.FileLabel = self.tr("文件：{}")
        self.FormatLabel = self.tr("格式：{}")
        self.DurationLabel = self.tr("时长：{}")
        self.BitrateLabel = self.tr("总码率：{} kbps")
        self.VideoStreamLabel = self.tr("[视频流] {}")
        self.AudioStreamLabel = self.tr("[音频流] {}")
        self.FpsLabel = self.tr("{} fps")
        self.HzLabel = self.tr("{} Hz")
        self.Mono = self.tr("单声道")
        self.Stereo = self.tr("立体声")

        # more interface - ms store logo
        self.MsStoreLogo = self.tr("MS Store 徽标")
        self.MsStoreLogoDesc = self.tr("一键生成上架微软商店的五个徽标")
        self.MsStoreLogoHint = self.tr("从输入图片生成 5 个徽标到其所在目录：{}")
        self.MsStoreLogoTaskTitle = self.tr("MS Store 徽标 - {}")

        # more interface - subtitle
        self.Subtitle = self.tr("字幕处理")
        self.SubtitleDesc = self.tr("提取/嵌入/转换字幕轨")
        self.SubtitleMode = self.tr("处理模式：")
        self.SubtitleFile = self.tr("字幕文件：")
        self.SubtitleFiles = self.tr("字幕文件")
        self.SelectSubtitleHint = self.tr("选择字幕文件...")
        self.SelectSubtitle = self.tr("选择字幕")
        self.SelectSubtitleFile = self.tr("选择字幕文件")
        self.ModeSubtitleExtract = self.tr("提取字幕（从视频提取字幕轨）")
        self.ModeSubtitleBurn = self.tr("嵌入硬字幕（烧录到画面）")
        self.ModeSubtitleEmbed = self.tr("嵌入软字幕（作为可切换字幕轨）")
        self.ModeSubtitleConvert = self.tr("格式转换（SRT/ASS/VTT 互转）")

        # more interface - loudnorm
        self.Loudnorm = self.tr("音量归一化")
        self.LoudnormDesc = self.tr("统一音量到标准响度")
        self.LoudnormMode = self.tr("归一化模式：")
        self.TargetLoudness = self.tr("目标响度：")
        self.TargetLoudnessHint = self.tr(
            "目标响度（LUFS），如 -16（仅 loudnorm 生效）"
        )
        self.LoudnormHint = self.tr(
            "提示：仅重新编码音频，视频流直接复制（音频文件则全部重编码）。"
        )
        self.ModeLoudnorm = self.tr("EBU R128 标准响度（推荐）")
        self.ModeDynaudnorm = self.tr("动态范围归一化")

        # more interface - speed
        self.Speed = self.tr("速度调整")
        self.SpeedDesc = self.tr("视频/音频变速")
        self.SpeedFactor = self.tr("速度倍率：")
        self.SpeedFactorHint = self.tr("速度倍率，如 2.0（2倍速）或 0.5（半速）")
        self.SpeedMode = self.tr("变速范围：")
        self.SpeedHint = self.tr(
            "提示：倍率 >1 加速，<1 减速。音视频同步变速需输入含音频轨的文件。"
        )
        self.ModeSpeedAv = self.tr("音视频同步变速")
        self.ModeSpeedVideo = self.tr("仅视频变速（静音输出）")
        self.ModeSpeedAudio = self.tr("仅音频变速")

        # more interface - home groups
        self.ImageTools = self.tr("图片工具")
        self.FormatConvert = self.tr("格式转换")
        self.Utilities = self.tr("实用工具")
        self.AdvancedTools = self.tr("高级工具")

        # advance interface cards
        self.EncoderSettings = self.tr("编码器设置")
        self.SoftwareEncoder = self.tr("软件编码器")
        self.SoftwareEncoderDesc = self.tr(
            "libx264兼容性好,libx265同画质更小,VP9流媒体友好,AV1体积最小但极慢"
        )
        self.UseHardwareEncoder = self.tr("是否使用硬件编码器")
        self.UseHardwareEncoderDesc = self.tr(
            "启用后使用显卡进行硬件加速编码,速度远快于软件编码但画质略逊"
        )
        self.HardwarePlatform = self.tr("硬件编码器平台")
        self.HardwarePlatformMac = self.tr("使用Apple VideoToolbox框架进行硬件加速编码")
        self.HardwarePlatformDesc = self.tr(
            "选择显卡厂商对应的编码平台,NVIDIA为NVENC,Intel为QSV,AMD为AMF"
        )
        self.HardwareEncoder = self.tr("硬件编码器")
        self.HardwareEncoderDesc = self.tr(
            "选择具体硬件编码器,可用项取决于平台与显卡型号,不支持时ffmpeg会报错"
        )
        self.QualityControlMode = self.tr("质量控制模式")
        self.QualityControlModeDesc = self.tr(
            "CRF恒定质量画质优先,Bitrate目标码率控制输出体积,二选一"
        )
        self.CrfParam = self.tr("CRF质量参数")
        self.CrfParamDesc = self.tr("数值越低画质越高体积越大,0为无损,常用18-28")
        self.VideoTargetBitrate = self.tr("视频目标码率")
        self.VideoTargetBitrateDesc = self.tr("单位kbps,仅在Bitrate模式下生效")
        self.TwoPass = self.tr("二次编码")
        self.TwoPassDesc = self.tr("码率控制更精准但耗时翻倍,仅Bitrate模式有意义")
        self.EncodeSpeedPreset = self.tr("编码速度预设")
        self.EncodeSpeedPresetDesc = self.tr(
            "越慢压缩体积越小但耗时越长,medium为平衡默认"
        )
        self.ResolutionDesc = self.tr(
            "origin保持原分辨率,1080p/720p/480p常用档,custom自定义宽度"
        )
        self.CustomWidth = self.tr("自定义宽度")
        self.CustomWidthDesc = self.tr(
            "高度按比例自动计算,需为偶数,仅在custom模式下生效"
        )
        self.FrameRateDesc = self.tr("origin保持原帧率,可固定为24/30/60")
        self.AudioEncoder = self.tr("音频编码器")
        self.AudioEncoderDesc = self.tr(
            "aac默认,libmp3lame兼容性好,libopus高质量低码率,copy不重编码"
        )
        self.AudioBitrateCard = self.tr("音频码率")
        self.AudioBitrateCardDesc = self.tr("128k默认,192k/320k音质更高但体积更大")
        self.RemoveAudioTrack = self.tr("删除音轨")
        self.RemoveAudioTrackDesc = self.tr("启用后不编码音频,输出视频无声音")
        self.ImageQualityCard = self.tr("图片质量")
        self.ImageQualityCardDesc = self.tr(
            "-q:v 数值，越小质量越高，仅对 jpeg/webp 等有损格式生效"
        )
        self.Tune = self.tr("调优")
        self.TuneDesc = self.tr("针对内容类型优化编码,仅libx264/libx265生效")
        self.CutStartTime = self.tr("裁剪起始时间")
        self.CutStartTimeDesc = self.tr("单位秒,留空表示从头开始")
        self.CutDuration = self.tr("裁剪持续时间")
        self.CutDurationDesc = self.tr("单位秒,留空表示到结尾")
        self.Deinterlace = self.tr("反交错")
        self.DeinterlaceDesc = self.tr("消除隔行扫描产生的横纹,适合老式DVD源")
        self.Rotation = self.tr("旋转角度")
        self.RotationDesc = self.tr("none不旋转,90/180/270逆时针旋转")
        self.Seconds = self.tr("秒")
        self.VideoArgs = self.tr("视频参数:")
        self.AudioArgs = self.tr("音频参数:")
        self.ImageArgs = self.tr("图片参数:")

        # menu bar
        self.FileMenu = self.tr("文件(&F)")
        self.CloseWindow = self.tr("关闭窗口")
        self.HelpMenu = self.tr("帮助(&H)")
        self.Feedback = self.tr("问题反馈")
        self.FfmpegWebsite = self.tr("FFmpeg 官网")

        # system tray
        self.ToggleWindow = self.tr("显示/隐藏窗口")
        self.Quit = self.tr("退出")

        # advance interface
        self.UseCustomArgs = self.tr("是否使用自定义参数")
        self.UseCustomArgsDesc = self.tr(
            "自定义ffmpeg参数，软件默认使用默认参数里的配置"
        )
        self.FilterConfigHint = self.tr(
            "勾选需要启用的参数块，未勾选的将不会加入 FFmpeg 命令"
        )
        self.FilterEncoder = self.tr("编码器")
        self.FilterQuality = self.tr("质量控制")
        self.FilterPreset = self.tr("编码速度")
        self.FilterResolution = self.tr("分辨率")
        self.FilterFrameRate = self.tr("帧率")
        self.FilterAudio = self.tr("音频")
        self.FilterImage = self.tr("图片")
        self.FilterExtra = self.tr("进阶设置")
