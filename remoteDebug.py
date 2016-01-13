LOG = logging.getLogger('nova.api')
LOG.debug(('GOT The logs'))
import pydevd;
pydevd.settrace('192.168.1.4',port=5678, stdoutToServer=True, stderrToServer=True, suspend=True)