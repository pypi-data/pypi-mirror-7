Jirafs-Graphviz
===============

Automatically converts graphviz (dot) files into PNG images before
uploading to JIRA.

Installation
------------

1. Install from PIP::

    pip install jirafs-graphviz

2. Enable for a ticket folder::

    jirafs config --set plugins.graphviz on

Note that you can globally enable this (or any) plugin by adding the
``--global`` flag to the above command::

    jirafs config --global --set plugins.graphviz on

Requirements
------------

* Graphviz
