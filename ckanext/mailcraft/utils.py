import ckan.plugins as p

from ckanext.mailcraft.mailer import DefaultMailer
from ckanext.mailcraft.interfaces import IMailCraft


def get_mailer() -> DefaultMailer:
    mailer = DefaultMailer

    for plugin in reversed(list(p.PluginImplementations(IMailCraft))):
        mailer = plugin.get_mailer()

    return mailer()
