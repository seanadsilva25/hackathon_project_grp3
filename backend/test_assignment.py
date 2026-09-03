import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.authority_assignment_service import determine_department, fetch_oldest_matching_authority, assign_complaint_authority

def run_tests():
    test_cases = [
        {"id": "test-1", "category": "Theft", "jurisdiction": "Mumbai North", "expected_dept": "Police"},
        {"id": "test-2", "category": "Assault", "jurisdiction": "Mumbai Central", "expected_dept": "Police"},
        {"id": "test-3", "category": "Suspicious Activity", "jurisdiction": "Mumbai North", "expected_dept": "Police"},
        {"id": "test-4", "category": "Traffic", "jurisdiction": "Mumbai Central", "expected_dept": "Police"},
        {"id": "test-5", "category": "Road Damage", "jurisdiction": "Mumbai North", "expected_dept": "BMC"},
        {"id": "test-6", "category": "Garbage/Waste", "jurisdiction": "Mumbai North", "expected_dept": "BMC"},
        {"id": "test-7", "category": "Streetlight", "jurisdiction": "Mumbai Central", "expected_dept": "BMC"},
        {"id": "test-8", "category": "Drainage", "jurisdiction": "Mumbai North", "expected_dept": "BMC"},
        {"id": "test-9", "category": "Water Supply", "jurisdiction": "Mumbai North", "expected_dept": "BMC"},
        {"id": "test-10", "category": "Encroachment", "jurisdiction": "Mumbai North", "expected_dept": "BMC"},
        {"id": "test-11", "category": "Public Sanitation", "jurisdiction": "Mumbai North", "expected_dept": "BMC"},
        {"id": "test-12", "category": "Public Disturbance", "jurisdiction": "Mumbai North", "expected_dept": None}, # Removed from police
    ]
    
    print("Running mapping tests...")
    for t in test_cases:
        dept = determine_department(t["category"])
        status = "PASS" if dept == t["expected_dept"] else "FAIL"
        print(f"[{status}] {t['category']} -> {dept} (Expected: {t['expected_dept']})")

if __name__ == "__main__":
    run_tests()
