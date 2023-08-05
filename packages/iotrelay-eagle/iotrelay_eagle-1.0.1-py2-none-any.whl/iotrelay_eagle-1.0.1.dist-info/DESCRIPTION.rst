IoT Relay-Eagle  -  An Eagle™ Home Energy Gateway plugin for IoT Relay
========================================================================
Release v1.0.1

iotrelay-eagle is a data source plugin for IoT Relay. It polls an
Eagle™ Home Energy Gateway for power readings and forwards those
readings to data handlers connected to IoT Relay. This lets you pull
data from a smart meter and forward it for logging or analysis.

More information about IoT Relay may be found in its
`Documentation <http://iot-relay.readthedocs.org>`_.

iotrelay-eagle uses the `Meter Reader
<https://github.com/eman/meter_reader>`_ library to communicate with
the Eagle™ Home Energy Gateway.

iotrelay-eagle is available on PyPI and can be installed via pip.

.. code-block:: bash

    $ pip install iotrelay-eagle


Configuration

.. code-block:: ini

    ; ~/.iotrelay.cfg

    [iotrelay-eagle]
    series key = power
    address = 192.168.3.253
    timeout = 4
    poll frequency = 9



License
===============================================================================
Copyright (c) 2014, Emmanuel Levijarvi
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Notice
===============================================================================
Eagle™ is a trademark of Rainforest™ Automation


