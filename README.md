pySimpleDMX
===========

### c0z3n 2012, James Hannon 2016, Limbic Media 2019 GPL v3 ###


pySimpleDMX is a simple python module designed to make basic DMX control in python easy.

pySimpleDMX is designed for and requires an [Enttec USB DMX Pro](http://www.enttec.com/index.php?main_menu=Products&pn=70304&show=description&name=dmxusbpro) or compatible hardware for communication over a DMX network.

#### Installation ####

```
# head
pip install git+https://github.com/limbicmedia/pySimpleDMX.git
```

or

```
# specivic version
pip install git+https://github.com/limbicmedia/pySimpleDMX.git@v0.2.0
```

#### Initialization ####
To initialize pySimpleDMX, initialize a `pysimpledmx.DMXConnection()` object, using the com port number of your enttec DMX USB Pro as an argument. 

On windows, for example, if our DMX USB Pro is on com port 3, we would initialize our dmx connection using `dmx = pysimpledmx.DMXConnection(3)`

On mac/linux, the serial device will show up in `/dev/` and will generally appear as something like this: `/dev/ttyUSB0`. The equivalent connection is `dmx = pysimpledmx.DMXConnection("/dev/ttyUSB0")`.

If `softfail=False`, the default setting for the `DMXConnection` initializer, and for any reason the dmx connection fails to initialize on the provided com port, pysimpledmx will log the error and close.

If `softfail=True`, the error will be logged and a "mock" device will be created. This allows for a system which can fail gracefully (continuing on with the rest of the code) and in development when access to an *Enttec* might not be necessary. 

    # example
    import pysimpledmx
    dmx = pysimpledmx.DMXConnection("/dev/ttyUSB0")
    ...


#### Usage ####
DMX output through pySimpleDMX is managed using a local list of size 512 in the `DMXConnection()` object, which represents the values for all 512 dmx channels in a single universe. The number of DMX channels used can be explicitly set with the `numChannels` argument in the `DMXCOnnection()` initializer. A smaller number of channels can greatly increase the speed of writing to the `Enttec` device.

When initialized, the default value for each channel is zero. to push the current list of values out over the dmx network, or 'update' the network, you must call the `.render()` method on your `DMXConnection()` object.

To change the value for a channel, use the `setChannel()` method on your `DMXConnection()` object. `setChannel()` requires `chan` (channel) and `val` (value) arguments, as well as an optional `autorender` argument, which should be set to `True` if you wish to have PySimpleDMX automatically update the dmx output immediately upon changing the specified channel value.

The `chan` and `val` arguments should be between 1 and `numChannels` (defaults to 512) and between 0 and 255, respectively.

Unless the `autorender` argument is specified `True`, the `.render()` method must be called to update the dmx output. Because of the serial communication with the DMX USB Pro, this is a relatively slow operation, and thus rendering should be done sparingly to avoid bottlenecking. Therefore, `autorender` is not recommended.

An *asynchronous ramp* method, `ramp()`, can be used to automatically ramp DMX values from their current state to an end state over a specified amount of time. The input of the `ramp()` method. The input `channels` and `vals` for the `ramp()` can be single values or lists.

    # example
    import pysimpledmx
    dmx = pysimpledmx.DMXConnection(3)

    dmx.setChannel(1, 255) # set DMX channel 1 to full
    dmx.setChannel(2, 128) # set DMX channel 2 to 128
    dmx.setChannel(3, 0)   # set DMX channel 3 to 0
    dmx.render() render    # render all of the above changes onto the DMX network

    dmx.setChannel(4, 255, autorender=True) # set channel 4 to full and render to the network

    # asynchronous ramp
    channels = [1, 2, 3]
    vals = [255, 0, 255]
    dmx.ramp(channels, vals, 10) # ramp values over 10 seconds
