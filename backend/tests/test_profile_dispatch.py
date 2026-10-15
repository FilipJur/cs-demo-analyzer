"""Durable profile dispatch: only implemented profiles reach the queue.

The application and the catalog are trust boundaries for the extraction profile.
An unsupported key must be rejected before anything durable is written, so the
queue can never hold a job the parser is guaranteed to fail, while the current
default profile and the frozen foundation profile stay requestable.
"""

from __future__ import annotations

import pytest

from cs_demo_analyzer.domain.contracts import (
    PROFILE_KEY,
    RECONSTRUCTION_PROFILE_KEY,
    AppError,
)

from helpers import DEMO_ID, create_application, register_demo

UNSUPPORTED = "reconstruction-v9:awpy-9.9.9:schema-9:normalizer-9"


@pytest.fixture
def dispatch_app(tmp_path):
    application = create_application(tmp_path)
    try:
        yield application
    finally:
        application.close()


def test_reprocess_rejects_an_unsupported_profile_before_enqueueing(dispatch_app):
    register_demo(dispatch_app, DEMO_ID)

    with pytest.raises(AppError) as error:
        dispatch_app.reprocess(DEMO_ID, profile_key=UNSUPPORTED)

    assert error.value.code == "INVALID_PROFILE"
    assert dispatch_app.catalog.list_jobs() == []
    # The recording is untouched and still reprocessable under a real profile.
    assert dispatch_app.catalog.get_demo(DEMO_ID).generation_id is None


def test_reprocess_defaults_to_the_current_profile_and_still_accepts_foundation(dispatch_app):
    register_demo(dispatch_app, DEMO_ID)

    default = dispatch_app.reprocess(DEMO_ID)
    foundation = dispatch_app.reprocess(DEMO_ID, profile_key=PROFILE_KEY)

    assert default.job_id is not None and foundation.job_id is not None
    assert default.job_id != foundation.job_id
    default_job = dispatch_app.catalog.get_job(default.job_id)
    foundation_job = dispatch_app.catalog.get_job(foundation.job_id)
    assert default_job.profile_key == RECONSTRUCTION_PROFILE_KEY
    assert foundation_job.profile_key == PROFILE_KEY
    assert {job.state for job in dispatch_app.catalog.list_jobs()} == {"queued"}


def test_unknown_demo_still_reports_not_found_before_profile_validation(dispatch_app):
    with pytest.raises(AppError) as error:
        dispatch_app.reprocess("f" * 64, profile_key=UNSUPPORTED)
    assert error.value.code == "NOT_FOUND"
    assert dispatch_app.catalog.list_jobs() == []
