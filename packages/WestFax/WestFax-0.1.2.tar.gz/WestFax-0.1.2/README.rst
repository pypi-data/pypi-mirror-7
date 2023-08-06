=======
WestFax
=======

A Python implementation of the WestFax API (http://westfax.com/)

Usage requires a WestFax account.

Usage
-----

.. code-block:: python

	wf = new westfax.WestFax( username, password, product )
	wf.add_number('555-555-5555')
	wf.set_header('This is a fax')
	wf.set_job_name('My fax job')
	wf.set_content("Yah! I'm a fax message!")

	try:
		wf.send()
	except westfax.FaxFail:
		print "Failed to send"


Methods
-------

`add_number( number )`
======================

Adds a number to the send the fax to. Mulitple numbers can be added.
``send()`` will raise ``westfax.NoRecipients`` if no valid numbers are found.

`set_billing_code( billing_code )`
==================================

Sets an optional billing code to track billing for the message in the WestFax dashboard

`set_job_name( name )`
======================

Sets an optional job name to identify the message in the WestFax dashboard

`set_header( header )`
======================

Sets the top header on the fax. (Sent with the fax. Often a company name or subject message)

`set_content( content )`
========================

Text or HTML content of the message. 
``send()`` will raise ``westfax.MissingFaxContent`` if no content was added to the message.

`send()`
========

Send the message to all recipients. If WestFax returns anything other than a 200 status then
``send()`` will raise ``westfax.FaxFail``

Exceptions
----------

All exceptions are raised on ``send()``

`NoRecipients`
==============

Raised when no numbers were added.

`MissingFaxContent`
===================

Raised when no content was added to the fax message

`FaxFail`
=========

Raised when the WestFax API returns anything other than a 200 status.
The error message is returned as the exception message.

TODO
----

* verify phone number validity on ``add_number()``
* Parse the error message from WestFax to raise more useful exceptions

AUTHOR
------

ConstituentVoice opensource@constituentvoice.com

COPYRIGHT
---------

Copyright (c) 2014 Constituent Voice LLC

This software is provided under the terms of the BSD License. 
It is free to redistribute and modify so long as this copyright notice is maintained.
The software is provided "AS-IS" with no warranty. See LICENSE.txt for details.

"WestFax" is a trademark of WestFax Inc. use of this software requires valid WestFax API
credentials and agreement with WestFax Inc.'s terms of service.

ConstituentVoice LLC is not affiliated or partnered with WestFax Inc.

