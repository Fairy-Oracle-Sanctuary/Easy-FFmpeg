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

    def path(self, theme=Theme.AUTO) -> str:
        return f":/app/images/logo/{self.value}.svg"
