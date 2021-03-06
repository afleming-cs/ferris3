from . import settings, template
from google.appengine.api import mail, app_identity
import logging


def send(recipient, subject, body, sender=None, reply_to=None, **kwargs):
    """
    Sends an html email to ``recipient`` with the given ``subject`` and ``body``.

    If sender is none, it's automatically set to ``app_config['email']['sender']``.

    Any additionally arguments are passed to ``mail.send_mail``, such as headers.
    """
    sender = sender if sender else settings.get('email')['sender']
    if not sender:
        sender = "noreply@%s.appspotmail.com" % app_identity.get_application_id()
        logging.info("No sender configured, using the default one: %s" % sender)

    res = mail.send_mail(
        sender=sender,
        to=recipient,
        subject=subject,
        body=body,
        html=body,
        reply_to=reply_to if reply_to else sender,
        **kwargs)
    logging.info('Email sent to %s by %s with subject %s and result %s' % (recipient, sender, subject, res))
    return res


def send_template(recipient, subject, template_name, context=None, theme=None, **kwargs):
    """
    Renders a template and sends an email in the same way as :func:`send`.
    templates should be stored in ``/templates/email/<template>.html``.

    For example::

        mail.send_template(
            recipient='jondoe@example.com',
            subject='A Test Email',
            template_name='test',
            context={
                'name': 'George'
            }
        )

    Would render the template ``/templates/email/test.html`` and email the rendered html.
    """
    name = ('email/' + template_name + '.html', template)
    context = context if context else {}
    body = template.render(name, context, theme=theme)
    res = send(recipient, subject, body, **kwargs)
    return res, body
