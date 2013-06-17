import time
import os
import pytest
from webtest.app import TestApp
from treeherder.webapp.wsgi import application
from treeherder.etl.buildapi import TreeherderBuildapiAdapter
from treeherder.etl.common import (JobData, get_revision_hash, get_job_guid)


@pytest.fixture
def buildapi_pending_url():
    tests_folder = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(
        tests_folder,
        "sample_data",
        "builds-pending.js"
    )
    return "file://{0}".format(path)


@pytest.fixture
def buildapi_running_url():
    tests_folder = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(
        tests_folder,
        "sample_data",
        "builds-running.js"
    )
    return "file://{0}".format(path)


@pytest.fixture
def mock_post_json_data():
    """mock the urllib call replacing it with a webtest call"""
    def _post_json_data(adapter, url, data):
        response = TestApp(application).post_json(url, params=data)
        response.getcode = lambda: response.status_int
        return response

    old_func = TreeherderBuildapiAdapter._post_json_data
    TreeherderBuildapiAdapter._post_json_data = _post_json_data

    # on tearDown, re-set the original function
    def fin():
        TreeherderBuildapiAdapter._post_json_data = old_func


def test_transform_pending_jobs(jm, buildapi_pending_url, mock_post_json_data):
    """
    a new buildapi pending job creates a new obj in the objectstore
    """
    adapter = TreeherderBuildapiAdapter()
    adapter.process_pending_jobs(buildapi_pending_url)

    stored_obj = jm.get_os_dhub().execute(
        proc="objectstore_test.selects.all")

    assert len(stored_obj) == 1


def test_transform_running_jobs(jm, buildapi_running_url, mock_post_json_data):
    """
    a new buildapi running job creates a new obj in the objectstore
    """
    adapter = TreeherderBuildapiAdapter()
    adapter.process_running_jobs(buildapi_running_url)

    stored_obj = jm.get_os_dhub().execute(
        proc="objectstore_test.selects.all")

    assert len(stored_obj) == 1
