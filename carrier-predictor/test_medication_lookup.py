#!/usr/bin/env python3
"""
Quick medication lookup tester
Tests the medication reference file without running the full API
"""

def search_medication_file(medication_name):
    """Search for a medication in the reference file"""
    file_path = "data/medical_conditions_medication_reference.txt"

    with open(file_path, 'r') as f:
        content = f.read()

    # Search in medication index
    if f"MEDICATION_NAME: {medication_name}" in content:
        # Find the condition reference
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if f"MEDICATION_NAME: {medication_name}" in line:
                if i + 1 < len(lines):
                    see_condition = lines[i + 1]
                    print(f"\n✓ Found: {medication_name}")
                    print(f"  {see_condition}")
                    return see_condition.split(": ")[1] if ": " in see_condition else None
    else:
        print(f"\n✗ Medication '{medication_name}' not found in index")
        return None

def get_carrier_recommendations(condition_name):
    """Get carrier recommendations for a condition"""
    file_path = "data/medical_conditions_medication_reference.txt"

    with open(file_path, 'r') as f:
        content = f.read()

    # Find the condition section
    condition_marker = f"===CONDITION"
    sections = content.split(condition_marker)

    for section in sections:
        if condition_name.lower() in section.lower():
            print(f"\n{'='*60}")
            print(f"CONDITION: {condition_name}")
            print(f"{'='*60}")

            # Extract carrier positioning
            if "CARRIER_POSITIONING:" in section:
                positioning_start = section.find("CARRIER_POSITIONING:")
                positioning_end = section.find("AGENT_GUIDANCE:", positioning_start)
                if positioning_end == -1:
                    positioning_end = section.find("===", positioning_start + 1)

                positioning = section[positioning_start:positioning_end]
                print(positioning)

            return True

    return False

def main():
    """Interactive medication lookup"""
    print("\n" + "="*60)
    print("MEDICATION LOOKUP TESTER")
    print("="*60)

    test_cases = [
        ("Metformin", "Should recommend Box 2 (Mutual of Omaha)"),
        ("Lantus", "Should recommend Box 3/4 (UHL/ELCO)"),
        ("Levothyroxine", "Should work at all carriers"),
        ("Lipitor", "Can indicate multiple conditions"),
        ("Lithium", "Should recommend Box 4 guaranteed issue only"),
    ]

    print("\nRunning test cases...\n")

    for medication, expected in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST: {medication}")
        print(f"Expected: {expected}")
        print(f"{'='*60}")

        condition = search_medication_file(medication)
        if condition:
            get_carrier_recommendations(condition)

    # Interactive mode
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("\nEnter medications to lookup (or 'quit' to exit)")

    while True:
        med = input("\nMedication name: ").strip()
        if med.lower() in ['quit', 'exit', 'q']:
            break

        if med:
            condition = search_medication_file(med)
            if condition:
                get_carrier_recommendations(condition)

if __name__ == "__main__":
    main()
