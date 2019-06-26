import serial, sys, os
from time import sleep, time
from threading import Thread, Event
import logging


START_VAL   = 0x7E
END_VAL     = 0xE7

COM_BAUD    = 57600
COM_TIMEOUT = 1
WRITE_TIMEOUT = 10
COM_PORT    = 7
DMX_SIZE    = 512
DMX_MAX     = 256

LABELS = {
         'GET_WIDGET_PARAMETERS' :3,  #unused
         'SET_WIDGET_PARAMETERS' :4,  #unused
         'RX_DMX_PACKET'         :5,  #unused
         'TX_DMX_PACKET'         :6,
         'TX_RDM_PACKET_REQUEST' :7,  #unused
         'RX_DMX_ON_CHANGE'      :8,  #unused
      }

class DMXChannelOutOfRange(Exception):
  '''
  Exception raised for DMX Channel Out of Range
  '''
  # Constructor or Initializer
  def __init__(self, value):
      self.value = value

  # __str__ is to print() the value
  def __str__(self):
      return(repr(self.value))

class DMXConnection(object):
  def __init__(self, comport = None, numChannels = DMX_SIZE ):
    '''
    On Windows, the only argument is the port number. On *nix, it's the path to the serial device.
    For example:
        DMXConnection(4)              # Windows
        DMXConnection('/dev/tty2')    # Linux
        DMXConnection("/dev/ttyUSB0") # Linux
    '''
    self.logger = logging.getLogger('pySimpleDMX.DMXConnection')
    self.stoprequest = Event()
    self.thread = Thread()
    self.numChannels = numChannels
    self.dmx_frame = [0] * self.numChannels
    try:
      self.com = serial.Serial(comport, baudrate = COM_BAUD, timeout = COM_TIMEOUT, write_timeout = WRITE_TIMEOUT)
    except serial.SerialException as e:
      self.logger.error("SerialException: {}".format(e))
      raise
    
    self.logger.info("Opened {}.".format(self.com.portstr))


  def setChannel(self, chan, val, autorender = False):
    '''
    Takes channel and value arguments to set a channel level in the local
    DMX frame, to be rendered the next time the render() method is called.
    '''
    if not 1 <= chan <= self.numChannels:
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
      self.dmx_frame = [0] * self.numChannels
    else:
      self.dmx_frame[chan] = 0

  def ramp(self, channels, vals, transitionTime):
    '''
    Linearly ramp list of channels to corresponding values
    over the specific transition time.
    '''
    self.logger.debug("Starting DMX ramp")
    if type(channels) is not list:
      channels = [channels]
    if type(vals) is not list:
      vals = [vals]

    channel_vals = list(zip(channels, vals))    
    steps = []
    for channel, endval in channel_vals:
        startval = self.dmx_frame[channel]
        step = (endval -  startval) / float(DMX_MAX)
        steps.append({"startval": startval, "step": step})

    self.logger.debug("Starting DMX ramp THREAD")
    if(self.thread.is_alive()):
      self.logger.debug("THREAD is alive! Joining")
      self.stoprequest.set()
      self.thread.join()
    else:
      self.stoprequest.clear()
    del(self.thread)
    self.thread = Thread(target=self._transitionThread, name="transition", args=(channels, steps, transitionTime,))
    self.thread.start()

  def _transitionThread(self, channels, steps, transitionTime):
    '''
    A thread for ramping DMX values without blocking
    '''
    self.logger.debug("Entering DMX ramp THREAD")
    
    sleeptime = transitionTime / float(DMX_MAX)
    for n in range(DMX_MAX):
      starttime = time()
      for i, channel in enumerate(channels):
        nexstval = int(steps[i]["startval"] + ((n+1) * steps[i]["step"]))
        self.setChannel(channel, nexstval)
      self.render()
      # account for time it took to run
      elapsed = time() - starttime
      if sleeptime > elapsed:
          waittime = sleeptime - elapsed
      else:
          waittime = None

      self.logger.debug("Thread event waittime: {0}".format(waittime))
      if(self.stoprequest.wait(timeout=waittime)):
        self.logger.debug("STOP REQUESTED")
        self.stoprequest.clear()
        break
    self.logger.debug("EXITING THREAD!")

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

    try:
      self.com.write(chars)
    except serial.SerialTimeoutException as e:
      self.logger.error("Serial failed to write to port.")
      raise

  def close(self):
    self.com.close()
