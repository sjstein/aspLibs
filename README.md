# aspLibs

## A collection of general use functions and utilities for ASP python programs.

### Common "global" variables

DATA_DIR = './Data'     # Subdirectory into which data is stored

### Classes
class IntRange:
    """
    Class used to validate that a CL argument (int type) is within
    [min,max] range. Utilized with 'type' parameter of add_argument.
    e.g.    argparse.add_argument('...',type=IntRange,...)
    """
    
class AspLogger:
    """
    Class which handles logging messages to console and log file.
    Utilizes severity levels 0,1,2,3 of type:
        'ERRO': 0,
        'WARN': 1,
        'INFO': 2,
        'DISP': 3
        
### Functions
def retry_connect(logobj, sock, saddr=None, sport=None):

def valid_ip(ip_nbr):

def get_interface_devices():

