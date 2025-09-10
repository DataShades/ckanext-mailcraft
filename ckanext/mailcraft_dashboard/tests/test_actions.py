from typing import Any, Callable

import pytest

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestCreateMail:
    def test_create_mail(self, email_factory: Callable[..., dict[str, Any]]):
        mail = email_factory()

        assert mail is not None
        assert mail["subject"] is not None
        assert mail["sender"] is not None
        assert mail["recipient"] is not None
        assert mail["message"] is not None
        assert mail["state"] is not None
        assert mail["extras"] is not None


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestListMails:
    def test_list_mails(self, email: dict[str, Any]):
        assert call_action("mc_mail_list")

    def test_no_mails(self):
        assert call_action("mc_mail_list") == []


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestShowMail:
    def test_show_mail(self, email: dict[str, Any]):
        assert call_action("mc_mail_show", {}, id=email["id"]) == email

    def test_no_mail(self):
        with pytest.raises(tk.ValidationError):
            call_action("mc_mail_show", id="123")


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestDeleteMail:
    def test_delete_mail(self, email: dict[str, Any]):
        assert call_action("mc_mail_delete", {}, id=email["id"])

    def test_no_mail(self):
        with pytest.raises(tk.ValidationError):
            call_action("mc_mail_delete", {}, id="123")


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestClearMails:
    def test_clear_no_mails(self):
        assert call_action("mc_mail_clear")["deleted"] == 0

    def test_clear_mails(self, email_factory: Callable[..., dict[str, Any]]):
        for _ in range(10):
            email_factory()

        assert len(call_action("mc_mail_list")) == 10
        assert call_action("mc_mail_clear")["deleted"] == 10
        assert call_action("mc_mail_list") == []
