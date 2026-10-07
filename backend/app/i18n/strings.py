"""Single source of truth for every backend-generated user-facing phrase.

Previously `translation_service.py` and `profile_service.py` each kept their
own separate en/ta dictionaries (plus a third ad hoc fallback dict inline in
profile_service). That made adding a language a hunt across files. Every
phrase now lives here, keyed by a stable id, with one entry per supported
language — adding language #4 is a matter of adding one key per entry, not
finding every place text was hardcoded.

Scheme facts (names, documents, official rules) are NOT here — those are
structured, verified data from data/seed_schemes.json and are intentionally
language-independent identifiers; only the natural-language phrasing around
them is translated.
"""
from __future__ import annotations

SUPPORTED_LANGUAGES = ["en", "hi", "ta"]  # architecture allows adding te, kn, ml, bn, mr later

# ---- Response phrases (used by translation_service.translate_phrase) ----
PHRASES: dict[str, dict[str, str]] = {
    "eligible_intro": {
        "en": "You may be eligible for {count} scheme(s).",
        "hi": "आप {count} योजनाओं के लिए पात्र हो सकते हैं।",
        "ta": "நீங்கள் {count} திட்டங்களுக்கு தகுதியுடையவராக இருக்கலாம்.",
    },
    "no_schemes_found": {
        "en": "Sorry, we couldn't identify a matching scheme based on the information provided.",
        "hi": "क्षमा करें, दी गई जानकारी के आधार पर हमें कोई उपयुक्त योजना नहीं मिली।",
        "ta": "மன்னிக்கவும், வழங்கப்பட்ட தகவலின் அடிப்படையில் பொருந்தக்கூடிய திட்டத்தை கண்டறிய முடியவில்லை.",
    },
    "need_more_info": {
        "en": "We need a bit more information to check your eligibility.",
        "hi": "आपकी पात्रता जांचने के लिए हमें थोड़ी और जानकारी चाहिए।",
        "ta": "உங்கள் தகுதியை சரிபார்க்க இன்னும் சில தகவல்கள் தேவை.",
    },
    "generic_follow_up": {
        "en": "Could you share a bit more about your situation?",
        "hi": "क्या आप अपनी स्थिति के बारे में थोड़ा और बता सकते हैं?",
        "ta": "உங்கள் நிலைமை பற்றி இன்னும் கொஞ்சம் தெரிவிக்க முடியுமா?",
    },
    "dashboard_action_complete_profile": {
        "en": "Complete missing profile information to unlock more accurate matches.",
        "hi": "अधिक सटीक मिलान अनलॉक करने के लिए अपनी प्रोफ़ाइल की छूटी हुई जानकारी पूरी करें।",
        "ta": "மேலும் துல்லியமான பொருத்தங்களைத் திறக்க உங்கள் சுயவிவரத்தில் விடுபட்ட தகவலை நிறைவு செய்யவும்.",
    },
    "dashboard_action_review_eligible": {
        "en": "Review your likely-eligible schemes and prepare the listed documents.",
        "hi": "अपनी पात्र होने की संभावना वाली योजनाओं की समीक्षा करें और सूचीबद्ध दस्तावेज़ तैयार करें।",
        "ta": "தகுதியுடையவையாக இருக்கக்கூடிய உங்கள் திட்டங்களை மதிப்பாய்வு செய்து பட்டியலிடப்பட்ட ஆவணங்களைத் தயார் செய்யவும்.",
    },
    "dashboard_action_tell_more": {
        "en": "Tell us more about your situation to discover relevant schemes.",
        "hi": "संबंधित योजनाओं को खोजने के लिए हमें अपनी स्थिति के बारे में और बताएं।",
        "ta": "தொடர்புடைய திட்டங்களைக் கண்டறிய உங்கள் நிலைமை பற்றி மேலும் எங்களிடம் தெரிவிக்கவும்.",
    },
}

# ---- Follow-up questions for a specific missing profile field ----
FIELD_QUESTIONS: dict[str, dict[str, str]] = {
    "age": {
        "en": "What is your age?",
        "hi": "आपकी उम्र क्या है?",
        "ta": "உங்கள் வயது என்ன?",
    },
    "state": {
        "en": "Which state do you live in?",
        "hi": "आप किस राज्य में रहते हैं?",
        "ta": "நீங்கள் எந்த மாநிலத்தில் வசிக்கிறீர்கள்?",
    },
    "annual_income": {
        "en": "What is your approximate annual family income?",
        "hi": "आपकी अनुमानित वार्षिक पारिवारिक आय कितनी है?",
        "ta": "உங்கள் ஆண்டு குடும்ப வருமானம் எவ்வளவு?",
    },
    "occupation": {
        "en": "What is your occupation?",
        "hi": "आपका व्यवसाय क्या है?",
        "ta": "நீங்கள் என்ன தொழில் செய்கிறீர்கள்?",
    },
    "student": {
        "en": "Are you currently a student?",
        "hi": "क्या आप वर्तमान में छात्र हैं?",
        "ta": "நீங்கள் தற்போது மாணவரா?",
    },
    "previous_academic_percentage": {
        "en": "What percentage did you receive in your previous qualification?",
        "hi": "आपकी पिछली परीक्षा में कितने प्रतिशत अंक मिले?",
        "ta": "உங்கள் முந்தைய தேர்வில் எத்தனை சதவீதம் பெற்றீர்கள்?",
    },
    "land_ownership": {
        "en": "Do you own the land you farm, or is it leased/family land?",
        "hi": "क्या आप जिस ज़मीन पर खेती करते हैं वह आपकी अपनी है, पट्टे पर है, या पारिवारिक ज़मीन है?",
        "ta": "நீங்கள் பயிரிடும் நிலம் உங்களுக்கு சொந்தமா, குத்தகையா அல்லது குடும்ப நிலமா?",
    },
    "disability_status": {
        "en": "Do you have a disability?",
        "hi": "क्या आपको कोई दिव्यांगता है?",
        "ta": "உங்களுக்கு ஏதேனும் இயலாமை உள்ளதா?",
    },
    "gender": {
        "en": "What is your gender?",
        "hi": "आपका लिंग क्या है?",
        "ta": "உங்கள் பாலினம் என்ன?",
    },
}


# ---- Field labels: human-readable names for profile fields, used when
# building eligibility explanation sentences (and anywhere else a raw field
# key like "annual_income" shouldn't be shown to a user directly). ----
FIELD_LABELS: dict[str, dict[str, str]] = {
    "age": {"en": "age", "hi": "उम्र", "ta": "வயது"},
    "gender": {"en": "gender", "hi": "लिंग", "ta": "பாலினம்"},
    "state": {"en": "state", "hi": "राज्य", "ta": "மாநிலம்"},
    "district": {"en": "district", "hi": "ज़िला", "ta": "மாவட்டம்"},
    "residence_type": {"en": "area type", "hi": "क्षेत्र प्रकार", "ta": "பகுதி வகை"},
    "occupation": {"en": "occupation", "hi": "व्यवसाय", "ta": "தொழில்"},
    "annual_income": {"en": "annual income", "hi": "वार्षिक आय", "ta": "ஆண்டு வருமானம்"},
    "education_level": {"en": "education level", "hi": "शिक्षा स्तर", "ta": "கல்வி நிலை"},
    "student": {"en": "student status", "hi": "छात्र स्थिति", "ta": "மாணவர் நிலை"},
    "course": {"en": "course", "hi": "पाठ्यक्रम", "ta": "படிப்பு"},
    "previous_academic_percentage": {
        "en": "previous academic percentage",
        "hi": "पिछली शैक्षणिक प्रतिशत",
        "ta": "முந்தைய கல்வி சதவீதம்",
    },
    "family_size": {"en": "family size", "hi": "परिवार का आकार", "ta": "குடும்ப அளவு"},
    "land_ownership": {"en": "land ownership", "hi": "भूमि स्वामित्व", "ta": "நில உரிமை"},
    "land_area_acres": {"en": "land area", "hi": "भूमि क्षेत्र", "ta": "நில பரப்பளவு"},
    "employment_status": {"en": "employment status", "hi": "रोज़गार स्थिति", "ta": "வேலை நிலை"},
    "disability_status": {"en": "disability status", "hi": "दिव्यांगता स्थिति", "ta": "இயலாமை நிலை"},
}

BOOL_LABELS: dict[str, dict[str, str]] = {
    "true": {"en": "yes", "hi": "हां", "ta": "ஆம்"},
    "false": {"en": "no", "hi": "नहीं", "ta": "இல்லை"},
}

# ---- Eligibility explanation sentence templates ----
CONDITION_TEMPLATES: dict[str, dict[str, str]] = {
    "condition_met": {
        "en": "Your reported {field} ({value}) meets the requirement ({operator} {expected}).",
        "hi": "आपकी बताई गई {field} ({value}) इस आवश्यकता को पूरा करती है ({operator} {expected})।",
        "ta": "உங்கள் தெரிவிக்கப்பட்ட {field} ({value}) தேவையை பூர்த்தி செய்கிறது ({operator} {expected}).",
    },
    "condition_not_met": {
        "en": "Your reported {field} ({value}) does not meet the requirement ({operator} {expected}).",
        "hi": "आपकी बताई गई {field} ({value}) इस आवश्यकता को पूरा नहीं करती ({operator} {expected})।",
        "ta": "உங்கள் தெரிவிக்கப்பட்ட {field} ({value}) தேவையை பூர்த்தி செய்யவில்லை ({operator} {expected}).",
    },
    "condition_missing": {
        "en": "'{field}' was not provided.",
        "hi": "'{field}' नहीं दी गई थी।",
        "ta": "'{field}' வழங்கப்படவில்லை.",
    },
    "condition_uncomparable": {
        "en": "Could not compare {field} against the required condition.",
        "hi": "{field} की आवश्यक शर्त से तुलना नहीं की जा सकी।",
        "ta": "{field} தேவையான நிபந்தனையுடன் ஒப்பிட முடியவில்லை.",
    },
    "unknown_operator": {
        "en": "Unknown comparison operator '{operator}' for {field}.",
        "hi": "{field} के लिए अज्ञात तुलना ऑपरेटर '{operator}'।",
        "ta": "{field} க்கான தெரியாத ஒப்பீட்டு ஆபரேட்டர் '{operator}'.",
    },
    "status_likely_eligible": {
        "en": "Based on the information you provided, you appear to meet the listed conditions.",
        "hi": "आपके द्वारा दी गई जानकारी के आधार पर, आप सूचीबद्ध शर्तों को पूरा करते दिख रहे हैं।",
        "ta": "நீங்கள் வழங்கிய தகவலின் அடிப்படையில், நீங்கள் பட்டியலிடப்பட்ட நிபந்தனைகளை பூர்த்தி செய்வதாகத் தெரிகிறது.",
    },
    "status_not_matching": {
        "en": "You do not appear to meet one or more required conditions for this scheme.",
        "hi": "आप इस योजना के लिए एक या अधिक आवश्यक शर्तों को पूरा नहीं करते दिख रहे हैं।",
        "ta": "இந்தத் திட்டத்திற்கான ஒன்று அல்லது அதற்கு மேற்பட்ட தேவையான நிபந்தனைகளை நீங்கள் பூர்த்தி செய்யவில்லை எனத் தெரிகிறது.",
    },
    "status_missing_with_matches": {
        "en": "You match some conditions, but we still need some information from you to fully determine eligibility.",
        "hi": "आप कुछ शर्तों को पूरा करते हैं, लेकिन पात्रता पूरी तरह तय करने के लिए हमें अभी भी आपसे कुछ जानकारी चाहिए।",
        "ta": "நீங்கள் சில நிபந்தனைகளுடன் பொருந்துகிறீர்கள், ஆனால் தகுதியை முழுமையாகத் தீர்மானிக்க எங்களுக்கு இன்னும் சில தகவல்கள் தேவை.",
    },
    "status_missing_no_matches": {
        "en": "We need a bit more information from you to determine eligibility for this scheme.",
        "hi": "इस योजना के लिए पात्रता तय करने के लिए हमें आपसे थोड़ी और जानकारी चाहिए।",
        "ta": "இந்தத் திட்டத்திற்கான தகுதியைத் தீர்மானிக்க எங்களுக்கு உங்களிடமிருந்து இன்னும் கொஞ்சம் தகவல் தேவை.",
    },
    "status_no_rules": {
        "en": "This scheme has no structured eligibility rules on record. Please check the official source.",
        "hi": "इस योजना के लिए कोई संरचित पात्रता नियम रिकॉर्ड में नहीं हैं। कृपया आधिकारिक स्रोत देखें।",
        "ta": "இந்தத் திட்டத்திற்கு கட்டமைக்கப்பட்ட தகுதி விதிகள் எதுவும் பதிவில் இல்லை. அதிகாரப்பூர்வ மூலத்தைச் சரிபார்க்கவும்.",
    },
    "final_authority_note": {
        "en": "Final eligibility is determined by the relevant government authority — please verify on the official source before applying.",
        "hi": "अंतिम पात्रता संबंधित सरकारी प्राधिकरण द्वारा तय की जाती है — कृपया आवेदन करने से पहले आधिकारिक स्रोत पर पुष्टि करें।",
        "ta": "இறுதி தகுதி சம்பந்தப்பட்ட அரசு அதிகாரத்தால் தீர்மானிக்கப்படுகிறது — விண்ணப்பிக்கும் முன் அதிகாரப்பூர்வ மூலத்தில் உறுதிப்படுத்தவும்.",
    },
}


def field_label(field: str, language: str = "en") -> str:
    entry = FIELD_LABELS.get(field, {})
    return entry.get(language) or entry.get("en") or field.replace("_", " ")


def bool_label(value: bool, language: str = "en") -> str:
    entry = BOOL_LABELS["true" if value else "false"]
    return entry.get(language) or entry.get("en")


def translate(key: str, language: str = "en", table: dict[str, dict[str, str]] = PHRASES, **kwargs) -> str:
    entry = table.get(key, {})
    template = entry.get(language) or entry.get("en") or key
    return template.format(**kwargs) if kwargs else template


def is_supported(language: str) -> bool:
    return language in SUPPORTED_LANGUAGES
