emailutil
=========

imap utils can be used to get the latest email from specified sender

####usage: 

from mailbox import util<br><br>
host = 'imap.126.com'<br>
user = ('username@126.com', 'password')<br>
sender = 'sender@example.com'<br>
email_message = util.get_email(host, user, sender)<br>
email_body = util.get_first_text_block(email_message)<br>
