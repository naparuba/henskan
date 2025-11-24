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
    
    Setup test environment:
    - Clean the splits directory
    - Configure UNWANTED and DELETED directories for tests
    """
    test_dir = os.path.dirname(__file__)
    
    # Clean and recreate splits directory
    splits_dir = os.path.join(test_dir, "splits")
    if os.path.exists(splits_dir):
        shutil.rmtree(splits_dir)
    os.makedirs(splits_dir)
    
    # Configure UNWANTED and DELETED directories for tests
    # Import parameters here to avoid circular imports
    from henskan import parameters as params_module
    
    # Setup unwanted_images directory (do NOT clean it)
    unwanted_dir = os.path.join(test_dir, "unwanted_images")
    if not os.path.exists(unwanted_dir):
        os.makedirs(unwanted_dir)
    
    # Setup deleted_images directory (clean it before tests)
    deleted_dir = os.path.join(test_dir, "deleted_images")
    if os.path.exists(deleted_dir):
        shutil.rmtree(deleted_dir)
    os.makedirs(deleted_dir)
    
    # Override the global constants in parameters module
    params_module.UNWANTED = unwanted_dir
    params_module.DELETED = deleted_dir
    
    print(f"\n[Test Config] UNWANTED set to: {unwanted_dir}")
    print(f"[Test Config] DELETED set to: {deleted_dir} (cleaned)")
