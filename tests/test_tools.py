from tools.browser import BrowserTool
from tools.youtube import YoutubeTool
from tools.filesystem import FileSystemTool
from tools.whatsapp import WhatsAppTool

print(FileSystemTool.current_directory())

print(YoutubeTool.open())

print(WhatsAppTool.open())