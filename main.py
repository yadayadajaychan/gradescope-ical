import datetime
import pytz
from src.common import utils
from src.modules import *

offset = pytz.timezone('America/New_York').localize(datetime.datetime.now()).utcoffset()
# Compile assignments into a list
assignments = {}
modules = [
    Gradescope()
]
for module in modules:
    module.run(assignments)

# Save the list to a json file to import later
utils.save_data('assignments', assignments)

# cleans out anything older that 180 days to prevent huge files
utils.old_cleaner()

# converts the json to an ical file and saves it
utils.json_to_ics(time_offset=offset)

