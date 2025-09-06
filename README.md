# 🛡️ LLM Phishing Email Detector  

This project uses **Large Language Models (LLMs)** to detect phishing emails. It leverages prompt engineering, structured parsing, and evaluation metrics to classify emails as **benign** or **phishing**. The goal is to explore the capabilities of modern LLMs in cybersecurity tasks and evaluate their effectiveness through accuracy and recall.  

---

##  Features  
- Parses raw email datasets into structured format.  
- Uses **prompt engineering** to query different LLMs.  
- Classifies emails as *benign* or *phishing*.  
- Computes evaluation metrics (**Accuracy**, **Recall**).  
- Modular workflow → easy to plug in new models.  
  

---

##  Workflow  
1. **Dataset Parsing** → Convert raw email data into a structured format with labels.  
2. **Prompt Engineering** → Construct effective prompts for each email.  
3. **LLM Classification** → Query the LLM (e.g., GPT, Gemma, Qwen) for predictions.  
4. **Normalization** → Map outputs into unified categories (*benign* / *phishing*).  
5. **Evaluation** → Calculate accuracy and recall against ground truth labels.  

---

##  Example Results  

| Model       | Accuracy | Recall |
|-------------|----------|--------|
| Qwen2.5     | 88.24%   | 80.00% |
| Gemma3      | 88.24%   | 84.00% |
| GPT-4o-mini | 80.39%   | 92.00% |

>  **Note:** Recall is prioritized in phishing detection since missing a phishing email is riskier than flagging a benign one.  

---

##  Installation  

Clone the repo:  
```bash
git clone https://github.com/kosmits-ai/LetsGoPhishing.git

