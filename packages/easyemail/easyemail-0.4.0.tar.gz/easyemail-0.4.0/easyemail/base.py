from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import email.utils
import smtplib


class EasyEmail(object):

    """Send prepared email using smtplib buildin capabilities.

    Usage::

        >>> email = EasyEmail()
        >>> email.to = ["roman@sample.com", "roman@sample.eu"]
        >>> email.subject = "Enlarge your library for FREE!"
        >>> email.sender = "kingslawyer@sample.com"
        >>> email.send()

    or::

        >>> email = EasyEmail(
        ...             to="kingslawyer@sample.com",
        ...             subject="No",
        ...             sender="roman@sample.com"
        ...         )
        >>> email.send()

    :param to: Defaults to empty list, can be list of emails or string.
    :param sender: Defaults to empty string - this should contain email
        of the sender (from).
    :param subject: Defaults to empty string - should contain subject of
        the message.
    :param charset: Defaults to UTF-8 but can be used to specify message
        encoding.
    :param parent: Optional class subclassing MIMEBase that will be a base
        message with default MIMEMultipart('alternative') inside. Useful in
        case of adding attachments, you then can add MIMEMultipart('mixed')
        as a parent. Leave as `None` to not pack default message in anything.

    """

    def __init__(self, to=[], sender='', subject='', charset='utf-8',
                 parent=None):

        if parent is not None:
            if not isinstance(parent, MIMEBase):
                raise ValueError("Optional parent need to subclass MIMEBase")

        self.parent = parent

        self.message = MIMEMultipart('alternative')
        self.message.set_charset(charset)
        self.subject = subject
        self.to = to
        self.sender = sender

    def attach_image(self, image_content, subtype=None):
        """Attach image binary data to message.

        :param image_content: :py:class:`email.mime.image.MIMEImage`
            parameter `_imagedata`.
        :param _subtype: :py:class:`email.mime.image.MIMEImage`
            parameter `_subtype` (defaults to None).

        """
        self.message.attach(MIMEImage(image_content, _subtype=subtype))

    def attach_binary(self, binary_data, subtype=None):
        """Attach binary data to message.

        :param binary_data: :py:class:`email.mime.application.MIMEApplication`
            parameter `_data`.
        :param _subtype: :py:class:`email.mime.application.MIMEApplication`
            parameter `_subtype` (defaults to None).

        """
        self.message.attach(MIMEApplication(binary_data, _subtype=subtype))

    def attach_text(self, text, subtype='plain', charset='utf-8'):
        """Attach text data to message.

        :param text: :py:class:`email.mime.text.MIMEText`
            parameter `_text`.
        :param _subtype: :py:class:`email.mime.text.MIMEText`
            parameter `_subtype` (defaults to None).

        """
        self.message.attach(MIMEText(text, _subtype=subtype, _charset=charset))

    def attach_audio(self, audio_data, subtype=None):
        """Attach text data to message.

        :param audio_data: :py:class:`email.mime.audio.MIMEAudio`
            parameter `_audiodata`.
        :param _subtype: :py:class:`email.mime.audio.MIMEAudio`
            parameter `_subtype` (defaults to None).

        """
        self.message.attach(MIMEAudio(audio_data, _subtype=subtype))

    def load_template(self, template_file_path, context, data_type='html',
                      ttype='mako', filelike=None):
        """Removed method, need to be implemented outside of the library.

        This totally didn't work the way I hoped. Using this we can't
        load anythin that has inheritance. This was silly idea, that kind
        of template rendering should be done externally, when you can define
        loaders, env and use library that you want to render.

        Sorry.

        """

        raise NotImplementedError(
            "This was stupid idea and didn't work at all. If you use it, "
            "stay on 0.2, but remember that it won't be developed. When using "
            ">0.3 just render template on your own and feed it to attach_text."
        )

    def send(self, connection_type='smtp', authentication=False,
             **smtp_params):
        r"""Send prebuilded message.

        :param connection_type: string with type of connection. Possible
            choices are: `smtp` (default), `ssl` and `tls`.
        :param authentication: `boolean` (default False), set it to True if
            server that you use for sending uses authentication. If this
            parameter is set to True - you need to supply `login` and
            `password` keyword arguments.
        :param \*\*smtp_params: Additional parameters depending on
            `connection_type` chosen. For full list and description please go
            to :py:mod:`smtplib`.

        """

        message = self._compose()
        smtp_connection = self._connect(
            connection_type, authentication, **smtp_params
        )
        smtp_connection.sendmail(
            from_addr=self.sender,
            to_addrs=self.to,
            msg=message.as_string()
        )
        smtp_connection.quit()

    def dump(self):
        """Generate simple testing drop of message.

        Returns string that has all the information that would be sent.

        """

        message = self._compose()
        dumped = message.as_string()

        return dumped

    def _connect(self, connection_type, authentication, **smtp_params):
        r"""Create smtplib connection for different connection types.

        Returns active smtp connection that need to be closed after usage.

        :param connection_type: string with type of connection. Possible
            choices are: `smtp` (default), `ssl` and `tls`.
        :param authentication: `boolean` (default False), set it to True if
            server that you use for sending uses authentication. If this
            parameter is set to True - you need to supply `login` and
            `password` keyword arguments.
        :param \*\*smtp_params: Additional parameters depending on
            `connection_type` chosen. For full list and description please go
            to :py:mod:`smtplib`.

        """

        if connection_type == 'smtp':
            smtp_connection = smtplib.SMTP(
                smtp_params.get('host', 'localhost'),
                smtp_params.get('port', 25),
                smtp_params.get('local_hostname'),
                smtp_params.get('timeout')
            )

        elif connection_type == 'ssl':
            smtp_connection = smtplib.SMTP_SSL(
                smtp_params.get('host'),
                smtp_params.get('port'),
                smtp_params.get('local_hostname'),
                smtp_params.get('keyfile'),
                smtp_params.get('certfile'),
                smtp_params.get('timeout')
            )

        elif connection_type == 'tls':
            smtp_connection = smtplib.SMTP(
                smtp_params.get('host'),
                smtp_params.get('port'),
                smtp_params.get('local_hostname'),
                smtp_params.get('timeout')
            )
            smtp_connection.starttls(
                smtp_params.get('keyfile'),
                smtp_params.get('certfile')
            )

        if authentication:
            smtp_connection.login(
                smtp_params.get('login'),
                smtp_params.get('password')
            )

        return smtp_connection

    def _compose(self):
        """Compose message from object attributes."""

        if self.parent is not None:
            self.parent.attach(self.message)
            message = self.parent
        else:
            message = self.message

        message['Subject'] = self.subject
        message['From'] = self.sender
        if isinstance(self.to, list):
            message['To'] = ', '.join(self.to)
        else:
            message['To'] = self.to

        # We need to make sure that proper date is set in email header.
        if message.get('Date') is None:
            now = email.utils.formatdate(localtime=True)
            message['Date'] = now

        return message
