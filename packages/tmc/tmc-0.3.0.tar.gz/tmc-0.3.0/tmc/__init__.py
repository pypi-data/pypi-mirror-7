VERSION = version = "0.3.0"

from tmc.models import DB
from tmc.api import API
from tmc.files import Files

db = DB()
api = API()
files = Files(api)
