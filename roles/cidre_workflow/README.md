cidre_workflow
==============

This role to do git-flow operation and interaction with github/gitlab API.

Role Variables
--------------

cidre_git_branch_main: The main branch name
cidre_git_branch_dev: The develop branch name
cidre_git_branch_release_prefix: The release branches prefix
cidre_version_file: The path to VERSION file, to store current version
cidre_changelog_file: the path to CHANGELOG file
cidre_repo: The repo ID or path name (user + repo for github)
cidre_platform: github or gitlab
cidre_version: "{{ lookup('file', './VERSION') | default('v0.1.0') }}

Example Playbook
----------------

```yaml
---
- name: CI/CD management, via cidre.io
  hosts: 127.0.0.1
  connection: local
  # remote_user: user
  # become: yes
  # become_method: sudo

  # ansible-playbook ./cidre.yaml --tags "issue_create" -e 'issue_title="CI: integrate cidre"' -e issue_description="cidre"

  vars:
    cidre_repo: ebuildy/ansible-cidre
    cidre_platform: github
    cidre_version: "{{ lookup('file', './VERSION') | default('v0.1.0') }}"

  roles:
  - cidre_workflow
```

License
-------

Apache 2.0

Author Information
------------------

Thomas Decaux (ebuildy)
