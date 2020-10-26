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
    git:
      branches:
        main: "master"
        develop: "develop"
        release: "release"

    cidre_paths:
      version: "./VERSION"

    project:
      id: 431
      version: "{{ lookup('file', cidre_paths.version) }}"
      version_wanted: "{{ lookup('env', 'VERSION_WANTED') }}"

    gitlab:
      endpoint: https://XXXXX/api/v4
      access_token: "{{ lookup('env', 'GITLAB_ACCESS_TOKEN') }}"
      username: "{{ lookup('env', 'GITLAB_LOGIN') }}"

    tags:
    - release_start
    - release_end
    - issue_create
    - milestone_update
    - change_log
    - build


  tasks:
  # Include cidre tasks
  - include_role:
      name: cidre
    tags:
    - release_start
    - release_end
    - issue_create
    - milestone_update
    - change_log
    - never

  # Exemple of build a Java progam with Gradle
  - name: Build app
    shell: "gradle -Prelease.version={{ project.version }} clean djobiAssemble -x test"
    tags: ["build", "never"]

```

Then, execute playbook:

```
# Start a release
VERSION_WANTED=v4.4.0 ansible-playbook ./cidre.yaml --tags "release_start"

# Create new issue
ansible-playbook ./cidre.yaml --tags "issue_create" -e 'issue_title="CI: integrate cidre"' -e issue_description="cidre"

# Commit some changes
git commit -am "stuff"

# Update change log (milestone description)
ansible-playbook ./cidre.yaml --tags "milestone_update"

# Finish release
ansible-playbook ./cidre.yaml --tags "release_end"

```
