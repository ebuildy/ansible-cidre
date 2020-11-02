# ansible-cidre
An Ansible playbook to do some CI/CD stuff with Gitlab

## Motivation

As a (lazy) good dev, I want to automate everything (so I can spend more time in my swimming-pool):
- git-flow
- create gitlab issue/milestone

## Usage

### Define "cidre.yaml" playbook at git project root

```
---
- name: CI/CD management, via cidre.io
  hosts: 127.0.0.1
  connection: local

  vars:
    cidre:
      git:
        branches:
          main: "master"
          develop: "develop"
          release: "release"
      project:
        id: ebuildy/ansible-cidre
        platform: github
      version:
        file: './VERSION'
        current: "{{ lookup('file', './VERSION') | default('v0.1.0') }}"
        to: "{{ cidre_version_to }}"

  roles:
  - cidre_workflow
```

Then, execute playbook:

```
# Get info
ansible-playbook ./cidre.yaml --tags cidre_info

# Start a release
ansible-playbook ./cidre.yaml -e "cidre_version_to=v0.1.0" --tags cidre_release_start

# Create new issue
ansible-playbook ./cidre.yaml --tags "issue_create" -e 'issue_title="CI: integrate cidre"' -e issue_description="cidre"

# Commit some changes
git commit -am "stuff"

# Update change log (milestone description)
ansible-playbook ./cidre.yaml --tags "milestone_update"

# Finish release
ansible-playbook ./cidre.yaml --tags "release_end"

```
