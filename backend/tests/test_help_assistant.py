from app.services.help_assistant_service import answer_question, get_tutorial


def test_where_is_the_setting_matches_settings_location():
    result = answer_question("where is the setting ?", language="en")
    assert result["matched"] is True
    assert result["topic"] == "settings_location"
    assert "gear" in result["answer"].lower() or "⚙" in result["answer"]


def test_what_does_the_ct_button_do_matches_header_buttons():
    result = answer_question("what does the CT button do", language="en")
    assert result["matched"] is True
    assert result["topic"] == "header_buttons"


def test_genuinely_off_topic_question_falls_back():
    result = answer_question("what is the capital of France", language="en")
    assert result["matched"] is False
    assert result["topic"] is None


def test_settings_location_answer_is_translated_to_hindi():
    result = answer_question("setting kahan hai", language="hi")
    assert result["matched"] is True
    assert any("ऀ" <= ch <= "ॿ" for ch in result["answer"])


def test_get_tutorial_includes_settings_step():
    steps = get_tutorial("en")
    assert any(step["route"] == "/settings" for step in steps)
