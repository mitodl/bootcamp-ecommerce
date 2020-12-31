"""Utils tests"""
import factory
import pytest

from klasses.factories import (
    BootcampRunCertificateFactory,
    BootcampRunEnrollmentFactory,
    BootcampRunFactory,
)
from klasses.utils import (
    generate_batch_certificates,
    generate_single_certificate,
    revoke_certificate,
    unrevoke_certificate,
)
from profiles.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_generate_batch_certificates():
    """Verify generate_batch_certificates utility method"""

    users = UserFactory.create_batch(2)
    bootcamp_run = BootcampRunFactory()
    BootcampRunEnrollmentFactory.create_batch(
        2, bootcamp_run=bootcamp_run, user=factory.Iterator(users)
    )
    assert generate_batch_certificates(bootcamp_run) == {
        "updated": True,
        "msg": "2 new certificates have been created for bootcamp-run:{}".format(
            bootcamp_run
        ),
    }
    assert generate_batch_certificates(bootcamp_run) == {
        "updated": False,
        "msg": "No new certificates were made for bootcamp-run:{}".format(bootcamp_run),
    }
    assert bootcamp_run.certificates.count() == 2
    assert bootcamp_run.certificates.filter(user=users[0]).count() == 1
    assert bootcamp_run.certificates.filter(user=users[1]).count() == 1


def test_generate_single_certificate():
    """Verify generate_single_certificate utility method"""

    user = UserFactory.create()
    bootcamp_run = BootcampRunFactory()

    assert generate_single_certificate(user, bootcamp_run) == {
        "updated": False,
        "msg": "User:{} doesn't have an active enrollment in bootcamp-run:{}".format(
            user.email, bootcamp_run
        ),
    }

    BootcampRunEnrollmentFactory.create(bootcamp_run=bootcamp_run, user=user)
    result = generate_single_certificate(user, bootcamp_run)
    certificate = bootcamp_run.certificates.get(user=user)

    assert result == {
        "updated": True,
        "msg": "A certificate:{} has been generated for user:{} in bootcamp-run:{}".format(
            certificate.link, user.email, bootcamp_run
        ),
    }

    assert generate_single_certificate(user, bootcamp_run) == {
        "updated": False,
        "msg": "A  certificate:{} already exists for user:{} in bootcamp-run:{}".format(
            certificate.link, user.email, bootcamp_run
        ),
    }

    # revoking certificate
    certificate.revoke()

    assert generate_single_certificate(user, bootcamp_run) == {
        "updated": False,
        "msg": "A revoked certificate:{} already exists for user:{} in bootcamp-run:{}".format(
            certificate.link, user.email, bootcamp_run
        ),
    }


def test_revoke_certificate():
    """Verify revoke_certificate utility method"""

    user = UserFactory.create()
    bootcamp_run = BootcampRunFactory()

    assert revoke_certificate(user, bootcamp_run) == {
        "updated": False,
        "msg": "No Certificate found for user:{} in bootcamp-run:{}".format(
            user.email, bootcamp_run
        ),
    }

    certificate = BootcampRunCertificateFactory(user=user, bootcamp_run=bootcamp_run)

    assert revoke_certificate(user, bootcamp_run) == {
        "updated": True,
        "msg": "Certificate:{} has been revoked for user:{} in bootcamp-run:{}".format(
            certificate.link, user.email, bootcamp_run
        ),
    }

    assert revoke_certificate(user, bootcamp_run) == {
        "updated": False,
        "msg": "Certificate:{} is already in revoked state for user:{} in bootcamp-run:{}".format(
            certificate.link, user.email, bootcamp_run
        ),
    }


def test_unrevoke_certificate():
    """Verify unrevoke_certificate utility method"""

    user = UserFactory.create()
    bootcamp_run = BootcampRunFactory()

    assert unrevoke_certificate(user, bootcamp_run) == {
        "updated": False,
        "msg": "No Certificate found for user:{} in bootcamp-run:{}".format(
            user.email, bootcamp_run
        ),
    }

    # Create certificate
    certificate = BootcampRunCertificateFactory(user=user, bootcamp_run=bootcamp_run)

    assert unrevoke_certificate(user, bootcamp_run) == {
        "updated": False,
        "msg": "Certificate:{} is already in unrevoked state for user:{} in bootcamp-run:{}".format(
            certificate.link, user.email, bootcamp_run
        ),
    }

    # Revoking certificate
    certificate.revoke()

    assert unrevoke_certificate(user, bootcamp_run) == {
        "updated": True,
        "msg": "Certificate:{} has been unrevoked for user:{} in bootcamp-run:{}".format(
            certificate.link, user.email, bootcamp_run
        ),
    }
