import redbot.core.utils.chat_formatting as chat    # Chat Formatting
from redbot.core.commands.context import Context    # Message Context
import redbot.core.utils.menus as menus             # Redbot menus
from redbot import MIN_PYTHON_VERSION               # Python Version
from difflib import get_close_matches
from redbot.core import commands                    # Redbot commands
from .data.consts import CONSTS                     # Consts used in Azure-Chan
from unidecode import unidecode                     # Unicode to ASCII encoder
from random import choice
from typing import *                                # Python Types
import contextlib
import requests                                     # API Handler
import discord
import sys
import re                                           # Regex
