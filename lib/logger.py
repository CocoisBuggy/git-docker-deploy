# Create a logger
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Create a file handler
# The file handler can be verbose, since it's not logger.infoed to the console
file_handler = logging.FileHandler("activity.log")
file_handler.setLevel(logging.DEBUG)

# Create a stream handler
# The detail will be controllable via the command line arguments
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Set the formatter for the handlers
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(file_handler)
log.addHandler(stream_handler)
