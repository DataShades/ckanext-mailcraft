import pytest
from faker import Faker
from pytest_factoryboy import register
from factory.declarations import LazyFunction

from ckan.tests import factories

from ckanext.mailcraft_dashboard.model import Email

fake = Faker()


@register(_name="email")
class EmailFactory(factories.CKANFactory):
    class Meta:  # type: ignore
        model = Email
        action = "mc_mail_create"

    subject = LazyFunction(lambda: fake.sentence())
    timestamp = LazyFunction(lambda: fake.date())
    sender = LazyFunction(lambda: fake.email())
    recipient = LazyFunction(lambda: fake.email())
    message = LazyFunction(lambda: fake.text())
    state = LazyFunction(
        lambda: fake.random_element(
            elements=[
                Email.State.success,
                Email.State.failed,
                Email.State.stopped,
            ]
        )
    )
    extras = {"key": "value"}


@pytest.fixture()
def clean_db(reset_db, migrate_db_for):
    reset_db()

    migrate_db_for("mailcraft_dashboard")


@register(_name="sysadmin")
class SysadminFactory(factories.Sysadmin):
    pass
