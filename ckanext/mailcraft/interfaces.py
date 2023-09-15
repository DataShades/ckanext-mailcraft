from typing import Type

from ckan.plugins.interfaces import Interface

from ckanext.mailcraft.mailer import Mailer, DefaultMailer


class IMailCraft(Interface):
    """Allow to register a custom mailer instead of a default one"""

    def get_mailer(self) -> Type[Mailer]:
        """Return the mailer class"""
        return DefaultMailer
