import logging
from . import logger
from .args import parser
from . import integration
from .logger import log, stream_handler

# Parse the arguments
args = parser.parse_args()

if args.verbose:
    stream_handler.setLevel(logging.DEBUG)
    log.debug("Using verbose logging")
    
log.debug("Module fully initialized")

