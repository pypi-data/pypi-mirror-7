TempoDB Archive tool archives datapoints that you no longer want hosted
at TempoDB but want to keep. By default, it keeps the most recent
thirty days of datapoints and looks back in 24 hour intervals,
archiving the datapoints in each interval until no datapoints are
found.

Datapoints are saved to an SQLite3 database - one table per series. The
TempoDB Archive tool will take care of creating the necessary schema.

.. note:: Deleting datapoints from TempoDB is optional but if there is
  more than one tempodb-archive run with the same sqlite3 file, the tool
  will generate a duplicate record error.

.. note:: When searching back through 24 hour (default setting)
  interval, the tool will stop as soon as it finds an empty interval.
  If there are data points beyond the empty interval, they will not be
  archived.

.. note:: This tool is not developed by TempoDB. Please do not contact
  them for support.

Installation
-----------------------------------------------------------------------
.. code:: bash

    pip install tempodb-archive


Configuration
-----------------------------------------------------------------------
TempoDB Archive tool does not require configuration but frequently (or
always) used options my be stored in a conifuration file for
convenience. The TempoDB Archive tool uses the ini format. If left
unspecified, the TempoDB Archive tool will look for a configuration
file at ``$HOME/.tempodb-archive.cfg``. This may be overriden by using
the ``-c`` option (see usage).

The following options, stored in a "tempodb", section are recognized:

============ ================== ===========================================================
Option       Default Value      Description
============ ================== ===========================================================
api key      no default         TempoDB api key (from tempo-db.com)
api secret   no default         TempoDB api secret (from tempo-db.com)
interval     24 (hours)         Length of the interval to fetch datapoints from TempoDB
keep days    30 (days)          Archive datapoints that are older then this number of days
delete       false              Delete datapoints after saving them to the local archive
series keys  archive all series Comma delimited list of series keys
============ ================== ===========================================================

Example:

.. code:: ini

    ; ~/.tempodb-archive.cfg

    [tempodb]
    api key = < your api key >
    api secret = < your api secret >
    interval = 48
    keep days = 15
    delete = true
    series names = temp, windspeed, humidity


Usage
-----------------------------------------------------------------------
::

  tempodb-archive        [-h] [--version] [-c CONFIG_FILE] [--api-key API_KEY]
                         [--api-secret API_SECRET]
                         {list,archive} ...

  TempoDB Archive Tool

  positional arguments:
    {list,archive}        commands
      list                list available series
      archive             archive datapoints

  optional arguments:
    -h, --help            show this help message and exit
    --version             Display Version
    -c CONFIG_FILE, --config-file CONFIG_FILE
                          Configuration Filename
    --api-key API_KEY     TempoDB API Key
    --api-secret API_SECRET
                          TempoDB API Secret


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


