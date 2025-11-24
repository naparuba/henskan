#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures
"""
import os
import shutil


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and before performing collection
    and entering the run test loop.
    
    Clean the splits directory once at the start of the test session.
    """
    splits_dir = os.path.join(os.path.dirname(__file__), "splits")
    
    # Clean and recreate splits directory
    if os.path.exists(splits_dir):
        shutil.rmtree(splits_dir)
    os.makedirs(splits_dir)

