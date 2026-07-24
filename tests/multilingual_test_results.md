# Phase 3.4 - Multilingual Pipeline Test Results

**Auto-checked (in-scope) questions: 12/12 passed (100.0%)** - Checkpoint (>=90%): MET

Out-of-scope questions are marked REVIEW and require a manual read (refusal-language detection in Hindi/Gujarati isn't reliably automatable with a simple keyword match).

| # | Category | Question | Detected Lang | English Translation | Status | Sources |
|---|----------|----------|----------------|----------------------|--------|---------|
| 1 | hindi_script | पीएम किसान के तहत कितना पैसा मिलता है? | hindi | How much money is given under PM Kisan? | PASS | pm-kisan, pm-vishwakarma-yojana, pm-mudra-yojana, pm-jan-dhan-yojana, pm-kusum |
| 2 | hindi_script | आयुष्मान भारत के लिए कौन से दस्तावेज़ चाहिए? | hindi | Which documents are required for Ayushman Bharat? | PASS | ayushman-bharat-pmjay, gujarat-post-matric-scholarship, pm-kisan, pm-jan-dhan-yojana, nsp-pre-matric-scholarship |
| 3 | hindi_script | सुकन्या समृद्धि योजना की ब्याज दर क्या है? | hindi | What is the interest rate of the Sukanya Samriddhi Yojana? | PASS | sukanya-samriddhi-yojana, pm-kisan, pm-matru-vandana-yojana, pm-jan-dhan-yojana, pm-jeevan-jyoti-bima-yojana |
| 4 | gujarati_script | પીએમ કિસાન યોજનામાં કેટલા પૈસા મળે છે? | gujarati | How much money is provided under the PM Kisan Yojana? | PASS | pm-kisan, pm-vishwakarma-yojana, pm-matru-vandana-yojana, pm-jan-dhan-yojana, sukanya-samriddhi-yojana |
| 5 | gujarati_script | ઉજ્જવલા યોજનાનો લાભ શું છે? | gujarati | What are the benefits of the Ujjwala Yojana? | PASS | pm-jan-dhan-yojana, pm-ujjwala-yojana, pm-matru-vandana-yojana, pm-vishwakarma-yojana, vahli-dikri-yojana |
| 6 | gujarati_script | વ્હાલી દીકરી યોજના માટે કોણ પાત્ર છે? | gujarati | Who is eligible for the Vhali Dikri Yojana? | PASS | vahli-dikri-yojana, pm-suraksha-bima-yojana, pm-vishwakarma-yojana, ayushman-bharat-pmjay, pm-jan-dhan-yojana |
| 7 | transliterated_hindi | PM Kisan yojana mein kitna paisa milta hai? | hinglish | How much money is received under the PM Kisan Yojana? | PASS | pm-kisan, pm-matru-vandana-yojana, pm-vishwakarma-yojana, pm-jan-dhan-yojana, vahli-dikri-yojana |
| 8 | transliterated_hindi | Ayushman Bharat ke liye kaunse documents chahiye? | hinglish | What documents are required for Ayushman Bharat? | PASS | ayushman-bharat-pmjay, gujarat-post-matric-scholarship, pm-kisan, pm-jan-dhan-yojana, mukhyamantri-gruh-yojana |
| 9 | transliterated_gujarati | PM Kisan yojanama ketla paisa made chhe? | gujlish | How much money is received under the PM Kisan scheme? | PASS | pm-kisan, pm-vishwakarma-yojana, pm-jan-dhan-yojana, pm-matru-vandana-yojana, pm-kusum |
| 10 | transliterated_gujarati | Ujjwala yojanano labh shu chhe? | gujlish | What are the benefits of the Ujjwala scheme? | PASS | pm-jan-dhan-yojana, pm-ujjwala-yojana, pm-vishwakarma-yojana, pm-jeevan-jyoti-bima-yojana, vahli-dikri-yojana |
| 11 | mixed_language | PM-KISAN scheme ke under kitna benefit milta hai per year? | hinglish | How much benefit is received per year under the PM-KISAN scheme? | PASS | pm-kisan, pmay-urban, pm-kusum, pm-vishwakarma-yojana, ayushman-bharat-pmjay |
| 12 | mixed_language | Mujhe Sukanya Samriddhi Yojana ka interest rate batao please | hinglish | Please tell me the interest rate of the Sukanya Samriddhi Yojana. | PASS | sukanya-samriddhi-yojana, pm-kisan, pm-jan-dhan-yojana, pm-matru-vandana-yojana, pm-jeevan-jyoti-bima-yojana |
| 13 | out_of_scope_hindi | मंगल ग्रह पर बसने की योजना क्या है? | hindi | What is the plan to settle on Mars? | REVIEW | pm-kisan, pm-kusum, pmay-urban, manav-garima-yojana, pm-fasal-bima-yojana |
| 14 | out_of_scope_gujarati | અમેરિકામાં નોકરી વિઝા માટે પાત્રતા શું છે? | gujarati | What is the eligibility for a work visa in America? | REVIEW | manav-garima-yojana, atal-pension-yojana, nsp-pre-matric-scholarship, gujarat-post-matric-scholarship, nsp-post-matric-scholarship |

## Full answers

### 1. [PASS] (hindi_script) पीएम किसान के तहत कितना पैसा मिलता है?

**Detected language:** hindi

**English translation:** How much money is given under PM Kisan?

**Answer:**

PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) योजना के अंतर्गत पात्र किसान परिवारों को प्रति वर्ष Rs. 6,000 की वित्तीय सहायता दी जाती है। यह राशि हर चार महीने में Rs. 2,000 की तीन समान किस्तों में सीधे लाभार्थियों के बैंक खाते में हस्तांतरित की जाती है।

आप इस योजना के बारे में अधिक जानकारी प्राप्त करने या आवेदन करने के लिए इसकी आधिकारिक वेबसाइट https://pmkisan.gov.in पर जा सकते हैं।

### 2. [PASS] (hindi_script) आयुष्मान भारत के लिए कौन से दस्तावेज़ चाहिए?

**Detected language:** hindi

**English translation:** Which documents are required for Ayushman Bharat?

**Answer:**

Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PMJAY) के लिए आवश्यक दस्तावेज निम्नलिखित हैं:

*   आधार कार्ड (Aadhaar card)
*   राशन कार्ड (Ration card) या हाउसहोल्ड आईडी (household ID)
*   पहचान का प्रमाण (जैसे वोटर आईडी, पासपोर्ट, या ड्राइविंग लाइसेंस)
*   निवास का प्रमाण (Proof of residence)
*   परिवार के सदस्यों का विवरण (हाउसहोल्ड रजिस्ट्रेशन के लिए)

इस योजना के बारे में अधिक जानकारी और आवेदन प्रक्रिया की पुष्टि के लिए आप आधिकारिक वेबसाइट https://pmjay.gov.in पर देख सकते हैं।

### 3. [PASS] (hindi_script) सुकन्या समृद्धि योजना की ब्याज दर क्या है?

**Detected language:** hindi

**English translation:** What is the interest rate of the Sukanya Samriddhi Yojana?

**Answer:**

Sukanya Samriddhi Yojana (SSY) के तहत वर्तमान में ब्याज दर 8.2% p.a. (Q2 FY 2026-27 के लिए) है। यह ब्याज सालाना आधार पर चक्रवृद्धि (compounded) होता है और इसे हर तिमाही संशोधित किया जाता है।

अधिक जानकारी और आवेदन के लिए आप आधिकारिक वेबसाइट देख सकते हैं: https://www.nsiindia.gov.in/InternalPage.aspx?Id_Pk=89

### 4. [PASS] (gujarati_script) પીએમ કિસાન યોજનામાં કેટલા પૈસા મળે છે?

**Detected language:** gujarati

**English translation:** How much money is provided under the PM Kisan Yojana?

**Answer:**

નમસ્તે! **PM-KISAN** (Pradhan Mantri Kisan Samman Nidhi) યોજના હેઠળ મળતા લાભો વિશેની માહિતી નીચે મુજબ છે:

આ યોજના હેઠળ પાત્ર ખેડૂત પરિવારોને વર્ષના કુલ **Rs. 6,000** આપવામાં આવે છે. આ રકમ દર ચાર મહિને **Rs. 2,000** ના ત્રણ સમાન હપ્તામાં સીધી ખેડૂતોના બેંક ખાતામાં જમા કરવામાં આવે છે.

વધુ માહિતી મેળવવા અને અરજી કરવા માટે, તમે યોજનાની સત્તાવાર વેબસાઇટની મુલાકાત લઈ શકો છો: https://pmkisan.gov.in

### 5. [PASS] (gujarati_script) ઉજ્જવલા યોજનાનો લાભ શું છે?

**Detected language:** gujarati

**English translation:** What are the benefits of the Ujjwala Yojana?

**Answer:**

Pradhan Mantri Ujjwala Yojana (PMUY 2.0) હેઠળ મળતા લાભો નીચે મુજબ છે:

*   પાત્ર મહિલાના નામે વિના મૂલ્યે LPG કનેક્શન, જેમાં ડિપોઝિટ-ફ્રી સિલિન્ડર (5 kg અથવા 14.2 kg) અને ફ્રી સ્ટવ આપવામાં આવે છે.
*   પ્રથમ રિફિલ વિના મૂલ્યે આપવામાં આવે છે.
*   લાભાર્થીઓને વર્ષમાં 12 રિફિલ સુધી, પ્રતિ 14.2 kg સિલિન્ડર રિફિલ પર Rs. 300 ની લક્ષિત DBT સબસિડી મળે છે.

વધુ માહિતી માટે તમે આ સત્તાવાર વેબસાઇટની મુલાકાત લઈ શકો છો: https://pmuy.gov.in

### 6. [PASS] (gujarati_script) વ્હાલી દીકરી યોજના માટે કોણ પાત્ર છે?

**Detected language:** gujarati

**English translation:** Who is eligible for the Vhali Dikri Yojana?

**Answer:**

Vahli Dikri Yojana માટેની પાત્રતા નીચે મુજબ છે:

*   અરજદાર (માતા-પિતા) ગુજરાતના કાયમી રહેવાસી હોવા જોઈએ.
*   દીકરીનો જન્મ 02-08-2019 ના રોજ અથવા તે પછી થયેલો હોવો જોઈએ.
*   આ યોજના માત્ર પરિવારની પ્રથમ બે દીકરીઓ માટે જ લાગુ પડે છે.
*   પરિવારની વાર્ષિક આવક Rs. 2 lakh થી વધુ ન હોવી જોઈએ.
*   લાભ સીધા મેળવવા માટે પરિવાર પાસે સક્રિય બેંક ખાતું હોવું જરૂરી છે.

વધુ માહિતી અને અરજી કરવા માટે તમે અધિકૃત વેબસાઇટ https://wcd.gujarat.gov.in ની મુલાકાત લઈ શકો છો.

### 7. [PASS] (transliterated_hindi) PM Kisan yojana mein kitna paisa milta hai?

**Detected language:** hinglish

**English translation:** How much money is received under the PM Kisan Yojana?

**Answer:**

**PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)** योजना के तहत, पात्र किसान परिवारों को प्रति वर्ष **Rs. 6,000** की वित्तीय सहायता दी जाती है। यह राशि हर चार महीने में **Rs. 2,000** की तीन समान किस्तों में सीधे लाभार्थियों के बैंक खातों में जमा की जाती है।

अधिक जानकारी के लिए और आवेदन करने के लिए कृपया इस आधिकारिक लिंक को देखें: https://pmkisan.gov.in

### 8. [PASS] (transliterated_hindi) Ayushman Bharat ke liye kaunse documents chahiye?

**Detected language:** hinglish

**English translation:** What documents are required for Ayushman Bharat?

**Answer:**

Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PMJAY) के लिए आवश्यक दस्तावेज निम्नलिखित हैं:

*   Aadhaar card
*   Ration card या household ID
*   Proof of identity (voter ID, passport, या driver's license)
*   Proof of residence
*   Family member details (household registration के लिए)

इस योजना के बारे में अधिक जानकारी और आवेदन करने के लिए कृपया आधिकारिक वेबसाइट https://pmjay.gov.in देखें।

### 9. [PASS] (transliterated_gujarati) PM Kisan yojanama ketla paisa made chhe?

**Detected language:** gujlish

**English translation:** How much money is received under the PM Kisan scheme?

**Answer:**

PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) યોજના હેઠળ, પાત્ર ખેડૂત પરિવારોને દર વર્ષે Rs. 6,000 ની સહાય આપવામાં આવે છે. આ રકમ ચાર મહિનાના અંતરે Rs. 2,000 ના ત્રણ સમાન હપ્તામાં સીધી ખેડૂતોના બેંક ખાતામાં (Direct Benefit Transfer - DBT દ્વારા) જમા કરવામાં આવે છે.

વધુ માહિતી અને અરજી કરવા માટે તમે આ સત્તાવાર વેબસાઇટની મુલાકાત લઈ શકો છો: https://pmkisan.gov.in

### 10. [PASS] (transliterated_gujarati) Ujjwala yojanano labh shu chhe?

**Detected language:** gujlish

**English translation:** What are the benefits of the Ujjwala scheme?

**Answer:**

Pradhan Mantri Ujjwala Yojana (PMUY 2.0) હેઠળ મળતા લાભો નીચે મુજબ છે:

*   પાત્ર મહિલાના નામે વિનામૂલ્યે LPG ગેસ કનેક્શન આપવામાં આવે છે, જેમાં ડિપોઝિટ-ફ્રી સિલિન્ડર (5 kg અથવા 14.2 kg) અને ફ્રી સ્ટવ (સગડી)નો સમાવેશ થાય છે.
*   પ્રથમ રિફિલ સંપૂર્ણપણે મફત આપવામાં આવે છે.
*   લાભાર્થીઓને વાર્ષિક 12 રિફિલ સુધી, દરેક 14.2 kg ના સિલિન્ડર દીઠ Rs. 300 ની ટાર્ગેટેડ DBT સબસિડી આપવામાં આવે છે.

વધુ માહિતી માટે તમે આ સત્તાવાર વેબસાઇટની મુલાકાત લઈ શકો છો: https://pmuy.gov.in

### 11. [PASS] (mixed_language) PM-KISAN scheme ke under kitna benefit milta hai per year?

**Detected language:** hinglish

**English translation:** How much benefit is received per year under the PM-KISAN scheme?

**Answer:**

नमस्ते! **PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)** योजना के तहत पात्र किसान परिवारों को प्रति वर्ष **Rs. 6,000** की वित्तीय सहायता दी जाती है।

यह राशि हर चार महीने में **Rs. 2,000** की तीन समान किस्तों में सीधे लाभार्थी के बैंक खाते में जमा की जाती है।

इस योजना के बारे में अधिक जानकारी प्राप्त करने या आवेदन करने के लिए आप आधिकारिक वेबसाइट **https://pmkisan.gov.in** पर जा सकते हैं।

### 12. [PASS] (mixed_language) Mujhe Sukanya Samriddhi Yojana ka interest rate batao please

**Detected language:** hinglish

**English translation:** Please tell me the interest rate of the Sukanya Samriddhi Yojana.

**Answer:**

Sukanya Samriddhi Yojana (SSY) के तहत वर्तमान में ब्याज दर 8.2% p.a. (Q2 FY 2026-27 के लिए) है, जो वार्षिक रूप से संयोजित (compounded annually) होती है और त्रैमासिक आधार पर संशोधित की जाती है।

आप इस योजना के बारे में अधिक जानकारी और अपडेट्स के लिए आधिकारिक वेबसाइट: https://www.nsiindia.gov.in/InternalPage.aspx?Id_Pk=89 पर देख सकते हैं।

### 13. [REVIEW] (out_of_scope_hindi) मंगल ग्रह पर बसने की योजना क्या है?

**Detected language:** hindi

**English translation:** What is the plan to settle on Mars?

**Answer:**

क्षमा करें, मेरे पास मौजूद जानकारी में मंगल ग्रह (Mars) पर बसने की किसी भी सरकारी योजना के बारे में कोई उल्लेख नहीं है। ऊपर दी गई जानकारी केवल विशिष्ट भारतीय सरकारी कल्याणकारी योजनाओं (PM-KISAN, PM-KUSUM, PMAY-U, Manav Garima Yojana, और PMFBY) से संबंधित है।

### 14. [REVIEW] (out_of_scope_gujarati) અમેરિકામાં નોકરી વિઝા માટે પાત્રતા શું છે?

**Detected language:** gujarati

**English translation:** What is the eligibility for a work visa in America?

**Answer:**

તમે પૂછેલા પ્રશ્ન વિશેની માહિતી ઉપલબ્ધ સંદર્ભમાં નથી. મારી પાસે ભારત સરકારની કલ્યાણકારી યોજનાઓ સંબંધિત માહિતી જ છે, જે તમારા પ્રશ્નનો જવાબ આપવા માટે પૂરતી નથી.

વધુ સચોટ અને અધિકૃત માહિતી માટે, કૃપા કરીને વિઝા સંબંધિત સરકારી અથવા સત્તાવાર વેબસાઇટ્સ તપાસો. 

તમે ભારત સરકારની જે યોજનાઓ વિશે માહિતી મેળવી શકો છો, તેના માટે તમે નીચેની સત્તાવાર લિંક્સ જોઈ શકો છો:
- Manav Garima Yojana (Gujarat): https://esamajkalyan.gujarat.gov.in
- Atal Pension Yojana (APY): https://www.jansuraksha.gov.in
- National Scholarship Portal: https://scholarships.gov.in
- Digital Gujarat Portal: https://digitalgujarat.gov.in
