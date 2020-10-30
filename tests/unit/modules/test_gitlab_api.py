# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys, os

#sys.path.append("/Users/dev/ebuildy/ansible")

from ansible.module_utils import basic
from ansible_collections.community.cidre.plugins.modules import gitlab_api

def test_gitlab_api_get_http_method():
    f = gitlab_api.gitlab_api_get_http_method
    assert f("projects", "create") == "POST"
    assert f("projects", "update") == "PUT"

def test_urls_part_to_url():
    f = gitlab_api.urls_part_to_url

    assert f([]) == "/"
    assert f(["toto"]) == "/toto"
    assert f(["hello", "world"]) == "/hello/world"

def test_gitlab_api_build_url():
    f = gitlab_api.gitlab_api_build_url

    assert f("G", "projects", {}, { }) == "G/projects"
    assert f("G", "projects", {}, { "type" : "private"}) == "G/projects?type=private"

    assert f("G", "milestones", { "project" : 1}, { }) == "G/projects/1/milestones"
    assert f("G", "milestones", { "project" : 1}, { "type" : "private"}) == "G/projects/1/milestones?type=private"

    assert f("G", "milestones", { "project" : 1, "milestone" : 1}, { }) == "G/projects/1/milestones/1"
