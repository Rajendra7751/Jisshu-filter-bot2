import math
import time

HELP_TEXT = """
<b>Commands:</b>
/start — Welcome & bot instructions
/mirror [link] — Mirror URL or Telegram file to PixelDrain
/leech [link] [-e] — Download/send (use -e to extract ZIP)
/status — Show your queue
/thumb — Set or update thumbnail
/del_thumb — Remove thumbnail
/cancel — Cancel all uploads/downloads
/help — See this message
"""

def human_readable_size(size):
    if size < 1024: return f"{size}B"
    for unit in ['KiB','MiB','GiB','TiB']:
        size /= 1024.0
        if size < 1024:
            return f"{size:.2f}{unit}"
    return f"{size:.2f}PiB"

def progress_bar_string(progress, width=10):
    filled = int(width * progress)
    empty = width - filled
    return "[" + "█" * filled + "░" * empty + f"] {int(progress*100)}%"

def format_status(filename, total, done, speed, eta):
    bar = progress_bar_string(done / total if total else 0)
    size_str = f"{human_readable_size(done)}/{human_readable_size(total)}"
    speed_str = f"{human_readable_size(speed)}/s" if speed else "?"
    return f"{bar} {size_str}
Speed: {speed_str} | ETA: {eta}s
{filename}"
