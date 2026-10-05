import pytest

from app.core.errors import ConflictError, DomainError
from app.domain.appointments import assert_transition, initial_status


def test_provider_confirmation_initial_state():
    assert initial_status("provider_confirmation").value == "pendingConfirmation"


def test_instant_initial_state():
    assert initial_status("instant").value == "confirmed"


def test_invalid_transition_is_rejected():
    with pytest.raises(ConflictError):
        assert_transition("completed", "confirmed")


def test_unknown_state_is_rejected():
    with pytest.raises(DomainError):
        assert_transition("bogus", "confirmed")
