"""Tests for management commands"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from klasses.factories import BootcampRunFactory
from profiles.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "method,command_kwargs",
    [
        (
            "klasses.management.commands.manage_certificates.revoke_certificate",
            {"revoke": True},
        ),
        (
            "klasses.management.commands.manage_certificates.unrevoke_certificate",
            {"unrevoke": True},
        ),
        (
            "klasses.management.commands.manage_certificates.generate_single_certificate",
            {"generate": True},
        ),
        (
            "klasses.management.commands.manage_certificates.generate_batch_certificates",
            {"generate_batch": True},
        ),
        (
            "klasses.management.commands.manage_certificates.manage_user_certificate_blocking",
            {"block": ["testuser1@example.com", "testuser2@example.com"]},
        ),
        (None, None),
    ],
)
def test_manage_certificates_command(mocker, method, command_kwargs):
    """Verify manage_certificate command execution flow"""

    def run_command(command, *args, **kwargs):
        """Run management command"""
        output = StringIO()
        call_command(command, *args, stdout=output, stderr=StringIO(), **kwargs)
        return output.getvalue()

    if method:
        patched_method = mocker.patch(method, return_value={"updated": True, "msg": ""})

        bootcamp_run = BootcampRunFactory()
        user = UserFactory.create()

        if command_kwargs.get("generate_batch"):
            run_command("manage_certificates", run=bootcamp_run.id, **command_kwargs)
            patched_method.assert_called_once_with(bootcamp_run)
        elif command_kwargs.get("block"):
            users_to_block = command_kwargs.get("block")
            run_command("manage_certificates", run=bootcamp_run.id, **command_kwargs)
            patched_method.assert_called_once_with(users_to_block, True, bootcamp_run)  # noqa: FBT003
        elif command_kwargs.get("unblock"):
            users_to_unblock = command_kwargs.get("unblock")
            run_command("manage_certificates", run=bootcamp_run.id, **command_kwargs)
            patched_method.assert_called_once_with(
                users_to_unblock,
                False,
                bootcamp_run,  # noqa: FBT003
            )
        else:
            run_command(
                "manage_certificates",
                user=user.id,
                run=bootcamp_run.id,
                **command_kwargs,
            )
            patched_method.assert_called_once_with(user, bootcamp_run)
    else:
        with pytest.raises(CommandError):
            run_command("manage_certificates", run=None)
