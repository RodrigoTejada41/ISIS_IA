import time

import pytest

from aurora.core.permissions import ActionRisk, AuthorizationMode, PermissionPolicy, PrivilegeProfile


def test_medium_blocks_delete_and_allows_read():
    policy = PermissionPolicy(profile=PrivilegeProfile.MEDIUM)

    assert policy.authorize("files.read", ActionRisk.READ_ONLY) == AuthorizationMode.AUTO_ALLOW
    assert policy.authorize("files.delete", ActionRisk.HIGH, destructive=True) == AuthorizationMode.REQUIRE_STRONG_CONFIRMATION


def test_profile_change_requires_authentication():
    policy = PermissionPolicy()

    with pytest.raises(PermissionError):
        policy.set_profile(PrivilegeProfile.TOTAL, authenticated=False)


def test_total_temporary_expires():
    policy = PermissionPolicy(profile=PrivilegeProfile.CONTROLLED)
    policy.set_profile(PrivilegeProfile.TOTAL, authenticated=True, duration_seconds=1)
    assert policy.profile == PrivilegeProfile.TOTAL

    policy.total_until = time.time() - 1
    policy.expire_if_needed()

    assert policy.profile == PrivilegeProfile.CONTROLLED


def test_emergency_stop_denies_actions():
    policy = PermissionPolicy(profile=PrivilegeProfile.TOTAL)
    policy.emergency_stop()

    assert policy.profile == PrivilegeProfile.MEDIUM
    assert policy.authorize("files.read", ActionRisk.READ_ONLY) == AuthorizationMode.DENY
