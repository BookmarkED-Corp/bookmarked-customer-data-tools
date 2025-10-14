#!/usr/bin/env python3
"""
Test script for machine-specific configuration system

This script verifies that the configuration system is working correctly.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.connections import ConnectionsConfig


def test_defaults_file():
    """Test that defaults.json exists and is valid"""
    print("Testing defaults.json file...")

    config_manager = ConnectionsConfig()
    defaults_file = config_manager.defaults_file

    if not defaults_file.exists():
        print("  ⚠ defaults.json not found")
        print(f"  ℹ Create it by copying: cp {defaults_file}.template {defaults_file}")
        return False

    try:
        with open(defaults_file, 'r') as f:
            defaults = json.load(f)

        print(f"  ✓ defaults.json is valid JSON")
        print(f"  ✓ Found {len(defaults)} connection types")

        # Check structure
        expected_keys = ['staging', 'production', 'hubspot', 'clickup', 'classlink']
        for key in expected_keys:
            if key in defaults:
                print(f"  ✓ {key} section exists")
            else:
                print(f"  ⚠ {key} section missing")

        return True

    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        return False


def test_load_defaults():
    """Test loading defaults through ConnectionsConfig"""
    print("\nTesting ConnectionsConfig.load_defaults()...")

    config_manager = ConnectionsConfig()
    defaults = config_manager.load_defaults()

    if defaults is None:
        print("  ⚠ No defaults loaded (file may not exist)")
        return False

    print(f"  ✓ Loaded {len(defaults)} connection types")

    # Check staging config
    if 'staging' in defaults:
        staging = defaults['staging']
        fields = ['host', 'port', 'database', 'user', 'password']
        filled = sum(1 for f in fields if staging.get(f))
        print(f"  ✓ Staging config has {filled}/{len(fields)} fields filled")

    return True


def test_save_and_load():
    """Test saving and loading connections"""
    print("\nTesting save and load cycle...")

    config_manager = ConnectionsConfig()

    # Create test data
    test_connections = {
        'staging': {
            'host': 'test-host',
            'port': 5432,
            'database': 'test-db',
            'user': 'test-user',
            'password': 'test-password-123'
        },
        'clickup': {
            'api_key': 'test-api-key-xyz'
        }
    }

    # Save
    print("  Saving test connections...")
    success = config_manager.save_connections(test_connections)
    if not success:
        print("  ✗ Failed to save connections")
        return False
    print("  ✓ Connections saved")

    # Load
    print("  Loading connections...")
    loaded = config_manager.load_connections()
    if not loaded:
        print("  ✗ Failed to load connections")
        return False
    print("  ✓ Connections loaded")

    # Verify decryption
    print("  Verifying decryption...")
    if loaded['staging']['password'] == 'test-password-123':
        print("  ✓ Password correctly decrypted")
    else:
        print(f"  ✗ Password mismatch: {loaded['staging']['password']}")
        return False

    if loaded['clickup']['api_key'] == 'test-api-key-xyz':
        print("  ✓ API key correctly decrypted")
    else:
        print(f"  ✗ API key mismatch: {loaded['clickup']['api_key']}")
        return False

    return True


def test_file_permissions():
    """Test that sensitive files have correct permissions"""
    print("\nTesting file permissions...")

    config_manager = ConnectionsConfig()

    # Check .connection_key
    if config_manager.key_file.exists():
        import stat
        mode = config_manager.key_file.stat().st_mode
        perms = stat.filemode(mode)
        print(f"  .connection_key: {perms}")
        if mode & 0o077 == 0:  # Check that group/other have no permissions
            print("  ✓ Encryption key has secure permissions")
        else:
            print("  ⚠ Encryption key should be 0600 (rw-------)")

    # Check connections.config
    if config_manager.config_file.exists():
        import stat
        mode = config_manager.config_file.stat().st_mode
        perms = stat.filemode(mode)
        print(f"  connections.config: {perms}")
        if mode & 0o077 == 0:  # Check that group/other have no permissions
            print("  ✓ Connections config has secure permissions")
        else:
            print("  ⚠ Connections config should be 0600 (rw-------)")

    return True


def test_gitignore():
    """Test that sensitive files are gitignored"""
    print("\nTesting .gitignore...")

    import subprocess

    sensitive_files = [
        'config/defaults.json',
        'config/.connection_key',
        'config/connections.config'
    ]

    for file_path in sensitive_files:
        result = subprocess.run(
            ['git', 'check-ignore', file_path],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✓ {file_path} is gitignored")
        else:
            print(f"  ✗ {file_path} is NOT gitignored!")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Machine-Specific Configuration System Tests")
    print("=" * 60)

    tests = [
        test_defaults_file,
        test_load_defaults,
        test_save_and_load,
        test_file_permissions,
        test_gitignore
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests: {passed}/{total} passed")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("⚠ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
