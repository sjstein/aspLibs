from datetime import datetime
import argparse
import re
import subprocess
import sys
import time

time_shortform = '%Y%m%d %H:%M:%S'
time_longform = '%Y%m%d %H:%M:%S.%f'

V_NONE = 0  # Verbosity levels (0 = lowest)
V_LOW = 1
V_MED = 2
V_HIGH = 3

DATA_DIR = './Data'     # Subdirectory into which data is stored

class IntRange:
    """
    Class used to validate that a CL argument (int type) is within
    [min,max] range. Utilized with 'type' parameter of add_argument.
    e.g.    argparse.add_argument('...',type=IntRange,...)
    """

    def __init__(self, imin=None, imax=None):
        self.imin = imin
        self.imax = imax

    def __call__(self, arg):
        try:
            value = int(arg)
        except ValueError:
            raise self.exception()
        if (self.imin is not None and value < self.imin) or (self.imax is not None and value > self.imax):
            raise self.exception()
        return value

    def exception(self):
        if self.imin is not None and self.imax is not None:
            return argparse.ArgumentTypeError(f'Must be an integer in the range [{self.imin}, {self.imax}]')
        elif self.imin is not None:
            return argparse.ArgumentTypeError(f'Must be an integer >= {self.imin}')
        elif self.imax is not None:
            return argparse.ArgumentTypeError(f'Must be an integer <= {self.imax}')
        else:
            return argparse.ArgumentTypeError('Must be an integer')


def retry_connect(logobj, sock, saddr=None, sport=None):
    e = sock.connect_ex((saddr, sport))
    while e != 0:
        try:
            logobj.warn(f'Unable to connect to server (err: {e}). Delaying before retry.')
            time.sleep(10)
            e = sock.connect_ex((saddr, sport))

        except KeyboardInterrupt:
            logobj.warn('Program termination via user interrupt.')
            exit(-1)


class AspLogger:

    severities_dict = {
        'ERRO': 0,
        'WARN': 1,
        'INFO': 2,
        'DISP': 3,
    }

    def __init__(self, verbosity=V_HIGH):

        self.verbosity = verbosity

        """
        _logging_method_template is the skeleton code that will be expanded into a number of methods based on the
        _severities dict (above). For each severity entry in that dict, the __init__ function will create a new method 
        with name = <entry>. From the instantiated object, user will call <objname>.<methodname>('msg','fname'). msg
        is the text to be sent to the console and (optionally) the file <fname>.
        """
        def _logging_method_template(severity_str, msg=None, fname=None):
            if verbosity >= self.severities_dict[severity_str]:
                if msg:
                    print(f'{self.timestamp()} [{severity_str}] {msg} {{{sys.argv[0]}}}')
                else:
                    print('')
            if fname:
                self.file_message(msg, fname)

        def _create_logging_method(severity_str):
            def _templated_logging_method(msg, fname=None):
                _logging_method_template(severity_str, msg, fname=fname)
            return _templated_logging_method

        """
        Upon instantiation, the for loop below will create a class method for each member within the _severities list.
        These new class methods will have severity embedded in the method name, so will only require passing of the 
        message and filename strings; obj.method('msg','fname').
        """
        for severity in self.severities_dict.keys():
            lm = _create_logging_method(severity)
            setattr(self, severity.lower(), lm)

    # Write message to file <fname> with long form timestamp
    def file_message(self, msg='', fname=None):
        with open(fname, 'a') as f:
            f.write(f'{self.timestamp("long")} {msg} \n')

    # Return timestamp string in short (HH:MM:SS) or long (HH:MM:SS.ff) format
    @staticmethod
    def timestamp(fmt='short'):
        if fmt == 'short':
            return datetime.now().strftime(time_shortform)
        else:
            return datetime.now().strftime(time_longform)


# Function to validate IPv4 address
def valid_ip(ip_nbr):
    # Create regular expression used to evaluate ipv4 address
    regex_ip = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$'''

    if re.search(regex_ip, ip_nbr):
        return True  # IP address is properly formed
    else:
        return False  # IP address is malformed


def get_interface_devices():
    """
    For operating systems that respond in a predictable way to the 
    command
        
        ip -4 addr show

    this utility will parse the result and produce a dictionary keyed by
    interface device name strings, and valued with their IP addresses as
    strings.  

    If the OS does not support the subprocess call, presumably the call
    will raise *some* kind of exception, which we report and then return
    an empty dictionary.  

    The expected format for results from the "ip" command is:

        id: name: ...
            inet addr/ ...

    This method identifies each hardware device by finding output lines
    that start with an integer device id.  From there it extracts the 
    device name and addr.  
    """

    # Execute the command:
    ip_command = ['ip', '-4', 'addr', 'show']
    try:
        output_bytes = subprocess.check_output(ip_command)
    except Exception as e:
        print(e)
        return dict()

    # Convert the output:
    output_string = output_bytes.decode()
    output_lines = output_string.split('\n')

    # Parse the output for lines containing device IDs:
    device_line_indices = list()
    for idx, line in enumerate(output_lines):
        try:
            # If the first segment of the ':'-split line will cast to 
            # int it's an id, and this line defines an interface device:
            int(line.split(':')[0])
            device_line_indices.append(idx)
        except ValueError:
            pass

    # Parse the output to extract device name/addr:
    interface_devices = dict()
    for idx in device_line_indices:
        # The name is the second segment of the ':'-split line:
        device = output_lines[idx].split(':')[1].strip()
        # The following line has the address after 'inet'; in other 
        # words, the second segment after stripping leading whitespace
        # and splitting on ' ':
        address = output_lines[idx+1].strip().replace('/', ' ').split()[1]
        interface_devices.update({device: address})

    return interface_devices
