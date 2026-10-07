from app.services.profile_service import extract_profile_from_text, detect_missing_fields


def test_extracts_student_profile():
    text = "I am a 20 year old engineering student from Tamil Nadu. My family income is around 1.5 lakh per year."
    profile = extract_profile_from_text(text)
    assert profile["age"] == 20
    assert profile["state"] == "Tamil Nadu"
    assert profile["student"] is True
    assert profile["course"] == "engineering"
    assert profile["annual_income"] == 150000


def test_extracts_farmer_profile():
    text = "I'm a 45 year old farmer from Tamil Nadu. I have 2 acres of land and my annual income is around 2 lakh."
    profile = extract_profile_from_text(text)
    assert profile["age"] == 45
    assert profile["occupation"] == "farmer"
    assert profile["land_area_acres"] == 2.0


def test_does_not_assume_land_ownership_when_leased():
    text = "I farm on my uncle's land in Tamil Nadu."
    profile = extract_profile_from_text(text)
    assert profile.get("land_ownership") == "family"
    assert profile.get("land_ownership") != "owned"


def test_missing_fields_detected_not_fabricated():
    profile = {"age": 20}
    missing = detect_missing_fields(profile, {"age", "state", "annual_income"})
    assert "state" in missing
    assert "annual_income" in missing
    assert "age" not in missing


def test_extracts_student_profile_in_hindi():
    text = "मैं 20 साल का इंजीनियरिंग छात्र हूं और तमिलनाडु में रहता हूं। मेरी वार्षिक आय 1.5 लाख रुपये है।"
    profile = extract_profile_from_text(text)
    assert profile["age"] == 20
    assert profile["state"] == "Tamil Nadu"
    assert profile["student"] is True
    assert profile["course"] == "engineering"
    assert profile["annual_income"] == 150000


def test_extracts_farmer_profile_in_hindi():
    text = "मैं 45 साल का किसान हूं, तमिलनाडु से। मेरे पास 2 एकड़ ज़मीन है।"
    profile = extract_profile_from_text(text)
    assert profile["age"] == 45
    assert profile["occupation"] == "farmer"
    assert profile["land_area_acres"] == 2.0


def test_does_not_assume_land_ownership_when_leased_in_hindi():
    text = "मैं अपने चाचा की ज़मीन पर खेती करता हूं।"
    profile = extract_profile_from_text(text)
    assert profile.get("land_ownership") == "family"
    assert profile.get("land_ownership") != "owned"
