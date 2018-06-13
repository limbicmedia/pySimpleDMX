import serial, sys
import logging

START_VAL   = 0x7E
END_VAL     = 0xE7

COM_BAUD    = 57600
COM_TIMEOUT = 1
COM_PORT    = 7
DMX_SIZE    = 512

LABELS = {
         'GET_WIDGET_PARAMETERS' :3,  #unused
         'SET_WIDGET_PARAMETERS' :4,  #unused
         'RX_DMX_PACKET'         :5,  #unused
         'TX_DMX_PACKET'         :6,
         'TX_RDM_PACKET_REQUEST' :7,  #unused
         'RX_DMX_ON_CHANGE'      :8,  #unused
      }

class DMXChannelOutOfRange(Exception):
  """
  Exception raised for DMX Channel Out of Range
  """

  # Constructor or Initializer
  def __init__(self, value):
      self.value = value

  # __str__ is to print() the value
  def __str__(self):
      return(repr(self.value))

class DMXConnection(object):
  def __init__(self, comport = None, softfail = False):
    '''
    On Windows, the only argument is the port number. On *nix, it's the path to the serial device.
    For example:
        DMXConnection(4)              # Windows
        DMXConnection('/dev/tty2')    # Linux
        DMXConnection("/dev/ttyUSB0") # Linux
    '''
    self.logger = logging.getLogger('pySimpleDMX.DMXConnection')
    self.dmx_frame = [0] * DMX_SIZE
    try:
      self.com = serial.Serial(comport, baudrate = COM_BAUD, timeout = COM_TIMEOUT)
    except serial.SerialException as e:
      self.logger.error("SerialException: {}".format(e))
      if softfail:
        raise
      else:
        sys.exit(0)

    self.logger.info("Opened {}.".format(self.com.portstr))


  def setChannel(self, chan, val, autorender = False):
    '''
    Takes channel and value arguments to set a channel level in the local
    DMX frame, to be rendered the next time the render() method is called.
    '''
    if not 1 <= chan <= DMX_SIZE:
      raise DMXChannelOutOfRange("Invalid channel specified: {}".format(chan))

    # clamp value
    val = max(0, min(val, 255))
    self.dmx_frame[chan] = val
    if autorender: self.render()

  def clear(self, chan = 0):
    '''
    Clears all channels to zero. blackout.
    With optional channel argument, clears only one channel.
    '''
    if chan == 0:
      self.dmx_frame = [0] * DMX_SIZE
    else:
      self.dmx_frame[chan] = 0


  def render(self):
    ''''
    Updates the DMX output from the USB DMX Pro with the values from self.dmx_frame.
    '''

    packet = [
              START_VAL,
              LABELS['TX_DMX_PACKET'],
              len(self.dmx_frame) & 0xFF,
              (len(self.dmx_frame) >> 8) & 0xFF,
    ]
    packet += self.dmx_frame
    packet.append(END_VAL)

    chars = bytes(packet)
    self.com.write(chars)

  def close(self):
    self.com.close()
