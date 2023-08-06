email/phone block
=================

A simple python function to substitute emails and phone number with dummies.

Unittest included.

Install
-------

pip install email_phone_block 

or

easy_install email_phone_block 


Usage
-----

    >>> from email_phone_block import filter_email_phone, filter_email, filter_phone
    >>> filter_email("So please send me an email at name@domain.com, thanks!")
    'So please send me an email at xxxx@xxxxx.xxx, thanks!'
    >>> filter_phone("So please call me at 333-333-3333, thanks!'")
    'So please call me at xxx-xxx-xxxx, thanks!'
    >>> filter_email_phone("So please call me at 333-333-3333 or email me at name@domain.com, thanks!'")
    'So please call me at xxx-xxx-xxxx or email at xxxx@xxxxx.xxx, thanks!'

For legacy reason you can still use from email_phone_block import block


Format Recognized
=================

Emails
------
- name@domain.com
- name(at)domain.com
- name at domain.com
 
Phone numbers
-------------
- 333-333-3333
- 3333333333
- 333 333 3333
- 333 333-3333
- 333333-3333
- 333-3333333
