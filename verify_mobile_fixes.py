"""
Quick verification script to check if mobile button fixes are in place
"""

import os

def verify_mobile_fixes():
    dashboard_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard.html')
    
    if not os.path.exists(dashboard_path):
        print(f"[ERROR] Dashboard file not found at: {dashboard_path}")
        return False
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Mobile CSS Media Query': '@media (max-width: 768px)',
        'Button Pointer Events Fix': 'pointer-events: auto !important',
        'Touch Action Fix': 'touch-action: manipulation !important',
        'Z-Index Fix': 'z-index: 100 !important',
        'Min Height Fix': 'min-height: 44px !important',
        'JavaScript Fix Function': 'function fixMobileButtons()',
        'Touch Event Listener': "addEventListener('touchstart'",
        'Resize Event Listener': "addEventListener('resize', fixMobileButtons)",
        'MutationObserver Integration': 'fixMobileButtons(); // Add mobile button fix',
    }
    
    print("[*] Verifying Mobile Button Fixes...\n")
    all_passed = True
    
    for check_name, check_string in checks.items():
        if check_string in content:
            print(f"[OK] {check_name}: Found")
        else:
            print(f"[FAIL] {check_name}: NOT FOUND")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] ALL CHECKS PASSED - Mobile fixes are properly installed!")
        print("\nNext Steps:")
        print("1. Clear browser cache")
        print("2. Test on mobile device or browser DevTools mobile emulation")
        print("3. Navigate to product creation/edit page")
        print("4. Verify submit button is clickable on mobile")
    else:
        print("[ERROR] SOME CHECKS FAILED - Please review the fixes")
    print("="*60)
    
    return all_passed

if __name__ == '__main__':
    verify_mobile_fixes()
