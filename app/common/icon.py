from enum import Enum

from libs.qfluentwidgets_pro import FluentIconBase, Theme

# class Icon(FluentIconBase, Enum):
#     def path(self, theme=Theme.AUTO):
#         return f":/app/images/icons/{self.value}_{getIconColor(theme)}.svg"


class Logo(FluentIconBase, Enum):
    FFMPEG = "FFmpeg"
    FACE01 = "Face01"
    FACE02 = "Face02"
    FACE03 = "Face03"
    FACE04 = "Face04"
    FACE05 = "Face05"
    FACE06 = "Face06"
    FACE07 = "Face07"
    FACE08 = "Face08"
    FACE09 = "Face09"
    FACE10 = "Face10"

    # 高级设置卡片图标
    ENCODER = "Gear"
    HARDWARE = "High-voltage"
    PLATFORM = "Factory"
    GPU = "Rocket"
    QUALITY_MODE = "Control-knobs"
    CRF = "Star"
    BITRATE = "Bar-chart"
    TWO_PASS = "Repeat-button"
    PRESET = "Stopwatch"
    RESOLUTION = "Television"
    CUSTOM_WIDTH = "Input-numbers"
    FRAME_RATE = "Film-frames"
    AUDIO_CODEC = "Musical-note"
    AUDIO_BITRATE = "Loudspeaker"
    REMOVE_AUDIO = "Muted-speaker"
    TUNE = "Magic-wand"
    START_TIME = "Alarm-clock"
    DURATION = "Timer-clock"
    DEINTERLACE = "Wavy-dash"
    ROTATION = "Curly-loop"

    def path(self, theme=Theme.AUTO) -> str:
        return f":/app/images/logo/{self.value}.svg"
