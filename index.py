import OBD

# 38400, 9600 are the possible boot bauds (unless reprogrammed via
# PP 0C).  19200, 38400, 57600, 115200, 230400, 500000 are listed on
# p.46 of the ELM327 datasheet.
#
# Once pyserial supports non-standard baud rates on platforms other
# than Linux, we'll add 500K to this list.
#
# We check the two default baud rates first, then go fastest to
# slowest, on the theory that anyone who's using a slow baud rate is
# going to be less picky about the time required to detect it.



# obd.logger.setLevel(obd.logging.DEBUG)

OBD.OBD('/dev/rfcomm1')

