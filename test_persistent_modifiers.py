#!/usr/bin/env python3
"""
Test the persistent modifier library system
"""

import os
import sys
import json

# Add the streamlit_app directory to path so we can import the functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

def test_persistent_libraries():
    """Test the persistent modifier library functionality"""
    print("🧪 Testing Persistent Modifier Libraries")
    print("=" * 50)
    
    # Import the functions from app.py
    from app import load_modifier_libraries, save_modifier_libraries, add_to_library, MODIFIER_STORAGE_FILE
    
    print(f"Storage file location: {MODIFIER_STORAGE_FILE}")
    
    # Test 1: Load initial libraries
    print("\n📂 Test 1: Loading initial libraries")
    libraries = load_modifier_libraries()
    print(f"✅ Loaded libraries with keys: {list(libraries.keys())}")
    print(f"   Prefixes: {len(libraries['prefixes'])} items")
    print(f"   Suffixes: {len(libraries['suffixes'])} items") 
    print(f"   Locations: {len(libraries['locations'])} items")
    
    # Test 2: Add new items to each library
    print("\n➕ Test 2: Adding new items")
    
    test_prefix = "premium"
    test_suffix = "specialist"
    test_location = "Windsor"
    
    # Add prefix
    success1 = add_to_library("prefixes", test_prefix)
    print(f"   Add prefix '{test_prefix}': {'✅' if success1 else '❌'}")
    
    # Add suffix
    success2 = add_to_library("suffixes", test_suffix)
    print(f"   Add suffix '{test_suffix}': {'✅' if success2 else '❌'}")
    
    # Add location
    success3 = add_to_library("locations", test_location)
    print(f"   Add location '{test_location}': {'✅' if success3 else '❌'}")
    
    # Test 3: Reload and verify persistence
    print("\n🔄 Test 3: Verify persistence")
    reloaded_libraries = load_modifier_libraries()
    
    prefix_found = test_prefix in reloaded_libraries['prefixes']
    suffix_found = test_suffix in reloaded_libraries['suffixes']
    location_found = test_location in reloaded_libraries['locations']
    
    print(f"   Prefix '{test_prefix}' persisted: {'✅' if prefix_found else '❌'}")
    print(f"   Suffix '{test_suffix}' persisted: {'✅' if suffix_found else '❌'}")
    print(f"   Location '{test_location}' persisted: {'✅' if location_found else '❌'}")
    
    # Test 4: Prevent duplicates
    print("\n🚫 Test 4: Duplicate prevention")
    
    # Try to add the same items again
    duplicate1 = add_to_library("prefixes", test_prefix)
    duplicate2 = add_to_library("suffixes", test_suffix)
    duplicate3 = add_to_library("locations", test_location)
    
    print(f"   Duplicate prefix rejected: {'✅' if not duplicate1 else '❌'}")
    print(f"   Duplicate suffix rejected: {'✅' if not duplicate2 else '❌'}")
    print(f"   Duplicate location rejected: {'✅' if not duplicate3 else '❌'}")
    
    # Test 5: Show current library contents
    print("\n📋 Test 5: Current library contents")
    final_libraries = load_modifier_libraries()
    
    print(f"   Prefixes ({len(final_libraries['prefixes'])}): {final_libraries['prefixes']}")
    print(f"   Suffixes ({len(final_libraries['suffixes'])}): {final_libraries['suffixes']}")
    print(f"   Locations ({len(final_libraries['locations'])}): {final_libraries['locations']}")
    
    # Overall test result
    all_tests_passed = (
        success1 and success2 and success3 and 
        prefix_found and suffix_found and location_found and
        not duplicate1 and not duplicate2 and not duplicate3
    )
    
    print(f"\n{'=' * 50}")
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Persistent modifier libraries are working correctly")
        print("✅ New items will be saved permanently")
        print("✅ Duplicates are prevented")
        print("✅ Libraries persist across app restarts")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Check the issues above")
    
    return all_tests_passed

def main():
    """Run the test"""
    print("🔧 Persistent Modifier Library Test")
    print("This tests whether added prefixes/suffixes/locations persist across sessions")
    print("=" * 60)
    
    success = test_persistent_libraries()
    
    print(f"\n{'=' * 60}")
    if success:
        print("🚀 Ready to test in Streamlit!")
        print("   1. Restart the Streamlit app")
        print("   2. Add new prefixes/suffixes/locations")
        print("   3. Restart the app again")
        print("   4. Verify the items are still there")
    else:
        print("🐛 Fix needed before proceeding")

if __name__ == "__main__":
    main()
