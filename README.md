# LawDecodes – AI-Powered Legal & Government Document Simplifier

## 📌 Project Title
**LawDecodes** – An AI-powered web platform that simplifies legal and government documents into easy-to-understand language for the common citizen.

---

## 📝 Problem Statement
Most citizens struggle to understand government schemes, legal notices, contracts, and official documents due to:
- Complex sentence structures  
- Technical jargon and legalese  
- Long, tedious formatting  
- English-only or overly formal Hindi versions  
- Lack of accessible summaries or translations  

**Who is affected?**
- Common citizens with limited education  
- Senior citizens or visually impaired people  
- Rural populations with minimal legal exposure  
- Students, journalists, and activists needing simplified interpretation  

**Real-world impact:**
- Missed benefits and schemes  
- Signing documents without understanding them  
- Exploitation due to lack of comprehension  
- Dependence on middlemen or misinformation  
- Inequity in access to rights and resources  

---

## 💡 Proposed Solution
A **web-based platform** where users can:
1. Upload documents (PDF, image, or text)  
2. Automatically extract and simplify content using AI  
3. Compare **original vs simplified** versions side-by-side  
4. Access legal term definitions via tooltips  
5. Translate simplified text into Indian languages  
6. Listen to the explanation via text-to-speech  
7. Ask follow-up questions via an integrated chatbot  

---

## 🚀 Core Features
- **AI-Powered Text Simplification** – T5/BART NLP models  
- **Document Upload Support** – Text, PDFs, and Images  
- **OCR for Scanned Docs** – Tesseract  
- **Dual View** – Original vs Simplified comparison  
- **Tooltip Glossary** – Legal word explanations  
- **Multilingual Support** – Indian language translations  
- **Text-to-Speech** – Audio output for simplified text  
- **AI Chatbot** – Follow-up question answering  
- **Responsive UI** – Mobile and desktop-friendly  

---

## 🛠 Tech Stack
**Frontend:**
- HTML, CSS, JavaScript  
- Tailwind CSS / Bootstrap   

**Backend:**
- Python (Flask)  

**AI/NLP Tools:**
- Hugging Face Transformers (T5, BART)  
- MarianMT / M2M100 for translation  
- SpaCy / NLTK for preprocessing  
- pyttsx3 or gTTS for TTS  
- Tesseract OCR for scanned docs  

**PDF/Image Processing:**
- PyMuPDF, pdfminer.six  
- Pillow, OpenCV  

**Hosting Platforms:**
- Hugging Face Spaces (models)  
- Render / Replit / Vercel (web hosting)   

---

## 🔄 Workflow
1. **Upload Document** (PDF/Image/Text)  
2. **OCR + PDF Parsing** (Tesseract, PyMuPDF)  
3. **Text Simplification** (T5/BART)  
4. **Glossary Generation** (Tooltip terms)  
5. **Optional Translation** (local languages)  
6. **Optional Text-to-Speech** output  
7. **Final Output + Chatbot**  

---

## 📂 Example Use Case
**Original:**  
> All beneficiaries belonging to SC/ST households with an annual income below Rs. 2.5 lakh are eligible for interest subvention under this scheme.  

**Simplified:**  
> If your family belongs to the SC/ST category and earns less than Rs. 2.5 lakh a year, you can get a discount on loan interest under this scheme.  

---

## 🌟 Uniqueness
- India-centric legal use case  
- Designed for non-experts & underrepresented groups  
- Regional language support  
- Multi-modal accessibility (text, audio, visual)  
- Open-source civic tech potential  

---

## 🔮 Future Enhancements
- Chrome Extension for web simplification  
- WhatsApp/Telegram bot integration  
- Voice-based input/output  
- "Explain My Contract" clause-by-clause explanation  
- Document tagging and classification  
- Mobile app for accessibility  

---

## 🎯 Ideal Use Cases
- Awareness about government schemes  
- Simplifying RTI replies or court notices  
- NGOs assisting citizens with paperwork  
- Legal aid volunteers & students  
- Civic tech & multilingual education platforms  

---

## 📅 Suggested Development Timeline (8 Weeks)
| Week | Task |
|------|------|
| 1 | Requirement gathering, wireframes |
| 2 | Frontend + Upload & PDF Parsing UI |
| 3 | OCR & Text Extraction Module |
| 4 | AI Text Simplification Model Integration |
| 5 | Translation + TTS Integration |
| 6 | Glossary + Tooltip Functionality |
| 7 | AI Chatbot + Final Testing |
| 8 | Deployment + Documentation |

---

## 🎯 Expected Outcomes
- Functional MVP web application  
- Impactful social accessibility solution  
- Portfolio-worthy AI project  
- Potential for real-world deployment  
- Open-source release for civic tech adoption  

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).



## Command for running backend(Run inside backend directory) 

- uvicorn main:app --reload --timeout-keep-alive 300

## Command for running frontend(Run inside frontend directory) 

- python -m http.server 8000
