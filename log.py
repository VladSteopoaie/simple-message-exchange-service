from loguru import logger # library to print logs in the terminal
import sys

# initializing colors and logging format
logger.remove()
logger.add(sys.stdout, colorize=True, format="<level>{level.icon}</level> <level>{message}</level>", level="DEBUG")
logger.level(name='INFO', icon='[-]', color='<cyan><bold>')
logger.level(name='WARNING', icon='[!]', color='<yellow><bold>')
logger.level(name='DEBUG', icon='[*]', color='<blue><bold>')
logger.level(name='ERROR', icon='[X]', color='<red><bold>')
logger.level(name='SUCCESS', icon='[#]', color='<green><bold>')