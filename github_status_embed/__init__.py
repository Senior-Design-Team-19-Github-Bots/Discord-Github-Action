"""
Github Status Embed for Discord.

This applications sends an enhanced GitHub Actions Status Embed to a
Discord webhook. The default embeds sent by GitHub don't contain a lot
of information and are send for every workflow run. This application,
part of a Docker-based action, allows you to send more meaningful embeds
when you want to send them.
"""

# 阅读顺序（根据__main__.py)
# 1. log.py
# 2. types.py
# 3. webhook.py