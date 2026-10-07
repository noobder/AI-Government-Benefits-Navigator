"""Scoped "how do I use this app" assistant — deliberately NOT a general
chatbot. It answers questions about navigating and using the Benefits
Navigator itself (how to search, what a status badge means, whether an
account is required, etc), matched against a small curated FAQ set by
default — the same offline-first, swappable pattern as MockLLMProvider in
llm_service.py. It never answers general knowledge questions and never
invents scheme facts; questions about actual benefits belong in the main
chat (app/graph/workflow.py), which is grounded in the verified scheme
database.
"""
from __future__ import annotations

import re

FAQ: list[dict] = [
    {
        "id": "find_benefits",
        "keywords": ["find", "search", "discover", "benefit", "scheme", "how do i start", "kaise"],
        "answer": {
            "en": "Tap 'Find My Benefits' on the home page to fill a short guided form, or 'Ask a Question' to describe your situation in your own words (typed or spoken). Either way, you'll see schemes you may be eligible for with a clear explanation for each one.",
            "hi": "होम पेज पर 'मेरे लाभ खोजें' पर टैप करके एक छोटा फ़ॉर्म भरें, या 'एक प्रश्न पूछें' पर टैप करके अपनी स्थिति अपने शब्दों में बताएं (टाइप करके या बोलकर)। दोनों ही तरीकों से, आपको उन योजनाओं की सूची मिलेगी जिनके लिए आप पात्र हो सकते हैं, हर एक के लिए स्पष्ट स्पष्टीकरण के साथ।",
            "ta": "'எனது நலன்களைக் கண்டறியவும்' என்பதைத் தட்டி ஒரு சிறிய படிவத்தை நிரப்பவும், அல்லது 'ஒரு கேள்வி கேளுங்கள்' மூலம் உங்கள் நிலைமையை உங்கள் சொந்த வார்த்தைகளில் (தட்டச்சு செய்து அல்லது பேசி) விவரிக்கவும். இரு வழிகளிலும், நீங்கள் தகுதியுடையவராக இருக்கக்கூடிய திட்டங்களை தெளிவான விளக்கத்துடன் காண்பீர்கள்.",
        },
    },
    {
        "id": "eligibility_meaning",
        "keywords": ["eligible", "eligibility", "status", "badge", "green", "yellow", "red", "likely", "possibly", "matching"],
        "answer": {
            "en": "The colored badge on each scheme tells you where you stand: green means you appear to meet all the listed conditions, yellow means we need more information or you partly match, and red means you don't currently match based on what you've told us. None of these are a guarantee — the government authority makes the final decision.",
            "hi": "प्रत्येक योजना पर रंगीन बैज आपकी स्थिति बताता है: हरा मतलब आप सभी सूचीबद्ध शर्तों को पूरा करते दिख रहे हैं, पीला मतलब हमें अधिक जानकारी चाहिए या आप आंशिक रूप से मेल खाते हैं, और लाल मतलब आप जो बताया है उसके आधार पर आप वर्तमान में मेल नहीं खाते। इनमें से कोई भी गारंटी नहीं है — अंतिम निर्णय सरकारी प्राधिकरण करता है।",
            "ta": "ஒவ்வொரு திட்டத்திலும் உள்ள வண்ண பேட்ஜ் உங்கள் நிலையைக் காட்டுகிறது: பச்சை என்றால் நீங்கள் பட்டியலிடப்பட்ட அனைத்து நிபந்தனைகளையும் பூர்த்தி செய்வதாகத் தெரிகிறது, மஞ்சள் என்றால் எங்களுக்கு கூடுதல் தகவல் தேவை அல்லது நீங்கள் ஓரளவு பொருந்துகிறீர்கள், சிவப்பு என்றால் நீங்கள் தெரிவித்தவற்றின் அடிப்படையில் தற்போது பொருந்தவில்லை. இவை எதுவும் உத்தரவாதம் அல்ல — இறுதி முடிவை அரசு அதிகாரம் எடுக்கும்.",
        },
    },
    {
        "id": "documents",
        "keywords": ["document", "papers", "certificate", "proof", "required", "need"],
        "answer": {
            "en": "Open any scheme and look at the 'Documents needed' or 'Required documents' section — it's built from the official scheme record, not guessed. A checked box means it's required for that scheme; an unchecked one is possibly required and worth confirming before you apply.",
            "hi": "किसी भी योजना को खोलें और 'आवश्यक दस्तावेज़' अनुभाग देखें — यह अधिकारिक योजना रिकॉर्ड से बनाया गया है, अनुमान से नहीं। चेक किया गया बॉक्स मतलब वह उस योजना के लिए आवश्यक है; अनचेक किया गया संभवतः आवश्यक है और आवेदन करने से पहले पुष्टि करने योग्य है।",
            "ta": "எந்த ஒரு திட்டத்தையும் திறந்து 'தேவையான ஆவணங்கள்' பிரிவைப் பார்க்கவும் — இது அதிகாரப்பூர்வ திட்ட பதிவிலிருந்து உருவாக்கப்பட்டது, யூகிக்கப்படவில்லை. சரிபார்க்கப்பட்ட பெட்டி என்றால் அது அந்தத் திட்டத்திற்கு தேவை; சரிபார்க்கப்படாதது தேவைப்படலாம், விண்ணப்பிக்கும் முன் உறுதிப்படுத்துவது நல்லது.",
        },
    },
    {
        "id": "apply",
        "keywords": ["apply", "application", "how to apply", "submit", "process"],
        "answer": {
            "en": "Each scheme page has a 'How to apply' section with numbered steps, plus a link to the official government source at the bottom. This app helps you find and prepare — the actual application always happens on the official government site or office, never inside this app.",
            "hi": "हर योजना पृष्ठ पर एक 'आवेदन कैसे करें' अनुभाग है जिसमें क्रमांकित चरण हैं, साथ ही नीचे आधिकारिक सरकारी स्रोत का लिंक भी है। यह ऐप आपको खोजने और तैयार करने में मदद करता है — वास्तविक आवेदन हमेशा आधिकारिक सरकारी वेबसाइट या कार्यालय में होता है, इस ऐप के अंदर कभी नहीं।",
            "ta": "ஒவ்வொரு திட்ட பக்கத்திலும் எண் இட்ட படிகளுடன் 'விண்ணப்பிப்பது எப்படி' பிரிவு உள்ளது, மேலும் கீழே அதிகாரப்பூர்வ அரசு மூலத்திற்கான இணைப்பும் உள்ளது. இந்த பயன்பாடு உங்களைக் கண்டறியவும் தயார்படுத்தவும் உதவுகிறது — உண்மையான விண்ணப்பம் எப்போதும் அதிகாரப்பூர்வ அரசு தளத்திலோ அலுவலகத்திலோ நடைபெறும், இந்த பயன்பாட்டிற்குள் ஒருபோதும் இல்லை.",
        },
    },
    {
        "id": "privacy",
        "keywords": ["aadhaar", "password", "otp", "bank", "safe", "privacy", "data", "secure", "store"],
        "answer": {
            "en": "This app never asks for your Aadhaar number, bank account details, passwords, or OTPs. Your guided-profile answers are only used to match you with schemes. Creating an account is optional and only ever adds cross-device sync — the app works fully as a guest.",
            "hi": "यह ऐप कभी भी आपका आधार नंबर, बैंक खाता विवरण, पासवर्ड या OTP नहीं मांगता। आपके गाइडेड-प्रोफ़ाइल उत्तर केवल आपको योजनाओं से मिलाने के लिए उपयोग किए जाते हैं। खाता बनाना वैकल्पिक है और यह केवल डिवाइसों में सिंक जोड़ता है — यह ऐप गेस्ट के रूप में पूरी तरह से काम करता है।",
            "ta": "இந்த பயன்பாடு உங்கள் ஆதார் எண், வங்கிக் கணக்கு விவரங்கள், கடவுச்சொற்கள் அல்லது OTP-களை ஒருபோதும் கேட்காது. உங்கள் வழிகாட்டப்பட்ட-சுயவிவர பதில்கள் உங்களை திட்டங்களுடன் பொருத்துவதற்கு மட்டுமே பயன்படுத்தப்படும். கணக்கை உருவாக்குவது விருப்பத்தேர்வு மற்றும் இது சாதனங்களில் ஒத்திசைவை மட்டுமே சேர்க்கிறது — இந்த பயன்பாடு விருந்தினராக முழுமையாக செயல்படுகிறது.",
        },
    },
    {
        "id": "language",
        "keywords": ["language", "hindi", "tamil", "english", "switch language", "bhasha", "mozhi"],
        "answer": {
            "en": "Use the language dropdown in the top-right corner to switch between English, Hindi, and Tamil at any time — the whole app, including voice input and output, follows your choice.",
            "hi": "किसी भी समय अंग्रेज़ी, हिंदी और तमिल के बीच बदलने के लिए ऊपर दाईं ओर भाषा ड्रॉपडाउन का उपयोग करें — पूरा ऐप, आवाज़ इनपुट और आउटपुट सहित, आपकी पसंद का अनुसरण करता है।",
            "ta": "எப்போது வேண்டுமானாலும் ஆங்கிலம், இந்தி, தமிழ் ஆகியவற்றுக்கு இடையே மாற ​மேல்-வலது மூலையில் உள்ள மொழி கீழ்தோன்றலைப் பயன்படுத்தவும் — குரல் உள்ளீடு மற்றும் வெளியீடு உட்பட முழு பயன்பாடும் உங்கள் தேர்வைப் பின்பற்றும்.",
        },
    },
    {
        "id": "voice",
        "keywords": ["voice", "speak", "microphone", "mic", "listen", "audio"],
        "answer": {
            "en": "Tap the microphone icon and speak — your words appear live as you talk. If it doesn't catch anything, check that microphone access is allowed for this site and try again; you can always type instead.",
            "hi": "माइक्रोफ़ोन आइकन पर टैप करें और बोलें — आपके शब्द बोलते ही दिखाई देते हैं। यदि यह कुछ नहीं पकड़ता है, तो जांचें कि इस साइट के लिए माइक्रोफ़ोन एक्सेस की अनुमति है, और फिर से प्रयास करें; आप हमेशा इसके बजाय टाइप कर सकते हैं।",
            "ta": "மைக்ரோஃபோன் ஐகானைத் தட்டி பேசுங்கள் — நீங்கள் பேசும்போதே உங்கள் வார்த்தைகள் தோன்றும். எதுவும் பிடிக்கவில்லை என்றால், இந்த தளத்திற்கு மைக்ரோஃபோன் அணுகல் அனுமதிக்கப்பட்டுள்ளதா எனச் சரிபார்த்து மீண்டும் முயற்சிக்கவும்; நீங்கள் எப்போதும் பதிலாக தட்டச்சு செய்யலாம்.",
        },
    },
    {
        "id": "save_scheme",
        "keywords": ["save", "bookmark", "later", "favorite"],
        "answer": {
            "en": "Open a scheme's details page and tap 'Save this scheme' — it needs a profile (guest or account) so it can be found again later on your My Benefits page.",
            "hi": "किसी योजना का विवरण पृष्ठ खोलें और 'यह योजना सहेजें' पर टैप करें — इसके लिए एक प्रोफ़ाइल चाहिए (गेस्ट या खाता) ताकि इसे बाद में आपके मेरे लाभ पेज पर फिर से पाया जा सके।",
            "ta": "ஒரு திட்டத்தின் விவரப் பக்கத்தைத் திறந்து 'இந்தத் திட்டத்தைச் சேமி' என்பதைத் தட்டவும் — இதற்கு ஒரு சுயவிவரம் தேவை (விருந்தினர் அல்லது கணக்கு) இதனால் அதை பின்னர் உங்கள் எனது நலன்கள் பக்கத்தில் மீண்டும் காணலாம்.",
        },
    },
    {
        "id": "account",
        "keywords": ["account", "sign up", "register", "login", "sign in", "required"],
        "answer": {
            "en": "No — an account is completely optional. You can use every core feature as a guest. Creating an account only adds the ability to sync your profile and saved schemes across different devices.",
            "hi": "नहीं — खाता पूरी तरह से वैकल्पिक है। आप गेस्ट के रूप में हर मुख्य सुविधा का उपयोग कर सकते हैं। खाता बनाने से केवल आपकी प्रोफ़ाइल और सहेजी गई योजनाओं को विभिन्न डिवाइसों में सिंक करने की क्षमता जुड़ती है।",
            "ta": "இல்லை — கணக்கு முற்றிலும் விருப்பத்தேர்வு. நீங்கள் விருந்தினராக ஒவ்வொரு முக்கிய அம்சத்தையும் பயன்படுத்தலாம். கணக்கை உருவாக்குவது உங்கள் சுயவிவரம் மற்றும் சேமிக்கப்பட்ட திட்டங்களை வெவ்வேறு சாதனங்களில் ஒத்திசைக்கும் திறனை மட்டுமே சேர்க்கிறது.",
        },
    },
    {
        "id": "accessibility",
        "keywords": ["accessible", "accessibility", "disability", "sign language", "read aloud", "simple mode", "large text", "contrast"],
        "answer": {
            "en": "Settings has a Simple Mode (fewer options, bigger buttons), Large Text, High Contrast, and an experimental hand-sign input for yes/no questions. Every page can also be read aloud with captions using the speaker button in the bottom corner.",
            "hi": "सेटिंग्स में एक सरल मोड (कम विकल्प, बड़े बटन), बड़ा टेक्स्ट, उच्च कंट्रास्ट, और हाँ/नहीं प्रश्नों के लिए एक प्रायोगिक हाथ-संकेत इनपुट है। नीचे कोने में स्पीकर बटन का उपयोग करके किसी भी पृष्ठ को कैप्शन के साथ ज़ोर से भी पढ़ा जा सकता है।",
            "ta": "அமைப்புகளில் எளிய பயன்முறை (குறைவான விருப்பங்கள், பெரிய பொத்தான்கள்), பெரிய உரை, அதிக மாறுபாடு, மற்றும் ஆம்/இல்லை கேள்விகளுக்கான ஒரு பரிசோதனை கை-சைகை உள்ளீடு உள்ளது. கீழ் மூலையில் உள்ள ஸ்பீக்கர் பொத்தானைப் பயன்படுத்தி எந்தப் பக்கத்தையும் தலைப்புகளுடன் சத்தமாகவும் படிக்க முடியும்.",
        },
    },
    {
        "id": "settings_location",
        "keywords": ["setting", "settings", "gear", "preferences", "options page", "where is the setting", "where are settings"],
        "answer": {
            "en": "Tap the ⚙️ gear icon in the top bar (inside the ☰ menu on a phone) to open Settings. From there you can change language, theme, text size, contrast, and turn on accessibility features like Simple Mode or hand-sign input.",
            "hi": "सेटिंग्स खोलने के लिए ऊपर की पट्टी में ⚙️ गियर आइकन पर टैप करें (फ़ोन पर ☰ मेनू के अंदर)। वहाँ से आप भाषा, थीम, टेक्स्ट का आकार, कंट्रास्ट बदल सकते हैं, और सरल मोड या हाथ-संकेत इनपुट जैसी सुविधाएं चालू कर सकते हैं।",
            "ta": "அமைப்புகளைத் திறக்க மேல் பட்டியில் உள்ள ⚙️ கியர் ஐகானைத் தட்டவும் (மொபைலில் ☰ மெனுவுக்குள்). அங்கிருந்து நீங்கள் மொழி, தீம், உரை அளவு, மாறுபாட்டை மாற்றலாம், மேலும் எளிய பயன்முறை அல்லது கை-சைகை உள்ளீடு போன்ற அணுகல்தன்மை அம்சங்களை இயக்கலாம்.",
        },
    },
    {
        "id": "header_buttons",
        "keywords": ["button", "icon", "top of the screen", "top right", "header", "menu", "hamburger", "what does this do", "what does that do", "ct", "a+"],
        "answer": {
            "en": "In the top bar: the sun/moon/monitor icon switches Light, Dark, or System theme. 'CT' toggles high contrast. 'A+' makes text bigger. The dropdown changes language. The ⚙️ gear opens Settings. On a phone, tap the ☰ menu icon to see the page links and all of these controls.",
            "hi": "ऊपर की पट्टी में: सूरज/चाँद/मॉनिटर आइकन लाइट, डार्क या सिस्टम थीम बदलता है। 'CT' उच्च कंट्रास्ट चालू/बंद करता है। 'A+' टेक्स्ट को बड़ा करता है। ड्रॉपडाउन भाषा बदलता है। ⚙️ गियर सेटिंग्स खोलता है। फ़ोन पर, पेज लिंक और ये सभी नियंत्रण देखने के लिए ☰ मेनू आइकन पर टैप करें।",
            "ta": "மேல் பட்டியில்: சூரியன்/நிலா/திரை ஐகான் லைட், டார்க் அல்லது சிஸ்டம் தீமை மாற்றுகிறது. 'CT' அதிக மாறுபாட்டை இயக்கும்/அணைக்கும். 'A+' உரையை பெரிதாக்கும். கீழ்தோன்றல் மொழியை மாற்றும். ⚙️ கியர் அமைப்புகளைத் திறக்கும். மொபைலில், பக்க இணைப்புகளையும் இந்த கட்டுப்பாடுகள் அனைத்தையும் பார்க்க ☰ மெனு ஐகானைத் தட்டவும்.",
        },
    },
]

FALLBACK_ANSWER = {
    "en": "I can only help with questions about using this app — like how to search for benefits, what a status badge means, or how to apply. For questions about your actual eligibility or specific schemes, try 'Ask a Question' on the main chat instead.",
    "hi": "मैं केवल इस ऐप का उपयोग करने से जुड़े प्रश्नों में मदद कर सकता हूं — जैसे लाभ कैसे खोजें, स्थिति बैज का क्या मतलब है, या आवेदन कैसे करें। आपकी वास्तविक पात्रता या विशिष्ट योजनाओं के बारे में प्रश्नों के लिए, इसके बजाय मुख्य चैट पर 'एक प्रश्न पूछें' आज़माएं।",
    "ta": "இந்த பயன்பாட்டைப் பயன்படுத்துவது தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் உதவ முடியும் — நலன்களைத் தேடுவது எப்படி, ஒரு நிலை பேட்ஜ் என்ன அர்த்தம், அல்லது எப்படி விண்ணப்பிப்பது போன்றவை. உங்கள் உண்மையான தகுதி அல்லது குறிப்பிட்ட திட்டங்கள் பற்றிய கேள்விகளுக்கு, முதன்மை அரட்டையில் 'ஒரு கேள்வி கேளுங்கள்' என்பதை முயற்சிக்கவும்.",
}


TUTORIAL_STEPS: list[dict] = [
    {
        "id": "welcome",
        "route": "/",
        "title": {"en": "Welcome", "hi": "स्वागत है", "ta": "வரவேற்பு"},
        "narration": {
            "en": "Welcome to Benefits Navigator. This app helps you find government schemes you may be eligible for. Let's take a quick look around.",
            "hi": "बेनिफिट्स नेविगेटर में आपका स्वागत है। यह ऐप आपको उन सरकारी योजनाओं को खोजने में मदद करता है जिनके लिए आप पात्र हो सकते हैं। आइए एक त्वरित नज़र डालें।",
            "ta": "பெனிஃபிட்ஸ் நேவிகேட்டருக்கு வரவேற்கிறோம். இந்த பயன்பாடு நீங்கள் தகுதியுடையவராக இருக்கக்கூடிய அரசு திட்டங்களைக் கண்டறிய உதவுகிறது. ஒரு விரைவான சுற்றுப்பயணம் செய்வோம்.",
        },
    },
    {
        "id": "find_or_ask",
        "route": "/",
        "title": {"en": "Two ways to start", "hi": "शुरू करने के दो तरीके", "ta": "தொடங்க இரண்டு வழிகள்"},
        "narration": {
            "en": "You can fill a short guided form with 'Find My Benefits', or just describe your situation in your own words with 'Ask a Question' — typed or spoken, whichever is easier for you.",
            "hi": "आप 'मेरे लाभ खोजें' के साथ एक छोटा गाइडेड फ़ॉर्म भर सकते हैं, या बस 'एक प्रश्न पूछें' के साथ अपनी स्थिति अपने शब्दों में बता सकते हैं — टाइप करके या बोलकर, जो भी आपके लिए आसान हो।",
            "ta": "நீங்கள் 'எனது நலன்களைக் கண்டறியவும்' மூலம் ஒரு சிறிய வழிகாட்டப்பட்ட படிவத்தை நிரப்பலாம், அல்லது 'ஒரு கேள்வி கேளுங்கள்' மூலம் உங்கள் நிலைமையை உங்கள் சொந்த வார்த்தைகளில் விவரிக்கலாம் — தட்டச்சு செய்தோ பேசியோ, உங்களுக்கு எது எளிதோ அது.",
        },
    },
    {
        "id": "recommendations",
        "route": "/chat",
        "title": {"en": "Your recommendations", "hi": "आपकी सिफारिशें", "ta": "உங்கள் பரிந்துரைகள்"},
        "narration": {
            "en": "After you share your situation, you'll see scheme cards with a colored status badge. Tap 'Why this scheme?' on any card to see exactly which conditions matched, and what's still missing.",
            "hi": "अपनी स्थिति साझा करने के बाद, आपको रंगीन स्थिति बैज के साथ योजना कार्ड दिखाई देंगे। किसी भी कार्ड पर 'यह योजना क्यों?' पर टैप करें ताकि यह देख सकें कि कौन सी शर्तें मेल खाईं, और अभी क्या कमी है।",
            "ta": "உங்கள் நிலைமையைப் பகிர்ந்த பிறகு, வண்ண நிலை பேட்ஜுடன் திட்ட அட்டைகளைக் காண்பீர்கள். எந்த நிபந்தனைகள் பொருந்தின, இன்னும் என்ன குறைவு என்பதைப் பார்க்க எந்த அட்டையிலும் 'இந்தத் திட்டம் ஏன்?' என்பதைத் தட்டவும்.",
        },
    },
    {
        "id": "documents_and_apply",
        "route": "/chat",
        "title": {"en": "Documents & applying", "hi": "दस्तावेज़ और आवेदन", "ta": "ஆவணங்கள் & விண்ணப்பம்"},
        "narration": {
            "en": "Every scheme lists the documents you'll likely need, and step-by-step instructions for applying — with a link to the official government source. This app helps you prepare; the real application always happens on the government's own site.",
            "hi": "हर योजना में वे दस्तावेज़ सूचीबद्ध हैं जिनकी आपको संभवतः आवश्यकता होगी, और आवेदन के लिए चरण-दर-चरण निर्देश — आधिकारिक सरकारी स्रोत के लिंक के साथ। यह ऐप आपको तैयार करने में मदद करता है; वास्तविक आवेदन हमेशा सरकार की अपनी साइट पर होता है।",
            "ta": "ஒவ்வொரு திட்டமும் உங்களுக்குத் தேவைப்படக்கூடிய ஆவணங்களையும், விண்ணப்பிப்பதற்கான படிப்படியான வழிமுறைகளையும் பட்டியலிடுகிறது — அதிகாரப்பூர்வ அரசு மூலத்திற்கான இணைப்புடன். இந்த பயன்பாடு தயார்படுத்த உதவுகிறது; உண்மையான விண்ணப்பம் எப்போதும் அரசின் சொந்த தளத்தில் நடைபெறும்.",
        },
    },
    {
        "id": "my_benefits",
        "route": "/benefits",
        "title": {"en": "My Benefits", "hi": "मेरे लाभ", "ta": "எனது நலன்கள்"},
        "narration": {
            "en": "My Benefits keeps track of everything: how many schemes you're likely eligible for, which need more information, and any you've saved for later.",
            "hi": "मेरे लाभ सब कुछ का ट्रैक रखता है: आप कितनी योजनाओं के लिए पात्र होने की संभावना है, किन्हें अधिक जानकारी चाहिए, और आपने बाद के लिए क्या सहेजा है।",
            "ta": "எனது நலன்கள் அனைத்தையும் கண்காணிக்கிறது: நீங்கள் எத்தனை திட்டங்களுக்கு தகுதியுடையவராக இருக்கலாம், எவற்றிற்கு கூடுதல் தகவல் தேவை, மேலும் நீங்கள் பின்னர் பயன்படுத்த சேமித்தவை.",
        },
    },
    {
        "id": "accessibility",
        "route": "/settings",
        "title": {"en": "Make it yours", "hi": "इसे अपने अनुसार बनाएं", "ta": "உங்களுக்கேற்றதாக மாற்றுங்கள்"},
        "narration": {
            "en": "In Settings you can switch language, turn on Simple Mode for a bigger, simpler layout, enable Large Text or High Contrast, and turn on experimental hand-sign input. That's the tour — tap the help button any time you have a question.",
            "hi": "सेटिंग्स में आप भाषा बदल सकते हैं, एक बड़े, सरल लेआउट के लिए सरल मोड चालू कर सकते हैं, बड़ा टेक्स्ट या उच्च कंट्रास्ट सक्षम कर सकते हैं, और प्रायोगिक हाथ-संकेत इनपुट चालू कर सकते हैं। यह रहा टूर — जब भी आपका कोई प्रश्न हो, सहायता बटन पर टैप करें।",
            "ta": "அமைப்புகளில் நீங்கள் மொழியை மாற்றலாம், பெரிய, எளிய தளவமைப்புக்கு எளிய பயன்முறையை இயக்கலாம், பெரிய உரை அல்லது அதிக மாறுபாட்டை இயக்கலாம், மேலும் பரிசோதனை கை-சைகை உள்ளீட்டை இயக்கலாம். இதுதான் சுற்றுப்பயணம் — உங்களுக்கு ஒரு கேள்வி இருக்கும்போதெல்லாம் உதவி பொத்தானைத் தட்டவும்.",
        },
    },
]


def get_tutorial(language: str = "en") -> list[dict]:
    return [
        {
            "step_id": step["id"],
            "route": step["route"],
            "title": step["title"].get(language) or step["title"]["en"],
            "narration": step["narration"].get(language) or step["narration"]["en"],
        }
        for step in TUTORIAL_STEPS
    ]


def _score(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def answer_question(question: str, language: str = "en") -> dict:
    best_entry = None
    best_score = 0
    for entry in FAQ:
        score = _score(question, entry["keywords"])
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry and best_score > 0:
        answer = best_entry["answer"].get(language) or best_entry["answer"]["en"]
        return {"answer": answer, "matched": True, "topic": best_entry["id"]}

    fallback = FALLBACK_ANSWER.get(language) or FALLBACK_ANSWER["en"]
    return {"answer": fallback, "matched": False, "topic": None}
