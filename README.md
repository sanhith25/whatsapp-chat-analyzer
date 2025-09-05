# 💬 WhatsApp Chat Analyzer (NLP & Streamlit)  

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)  
[![NLP](https://img.shields.io/badge/NLP-Text%20Analysis-green)](https://en.wikipedia.org/wiki/Natural_language_processing)  
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red)](https://streamlit.io/)  
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange)](https://matplotlib.org/)  

---

## 📌 Project Overview  
This **NLP-powered interactive Streamlit app** analyzes WhatsApp chat exports to uncover **conversation trends, word usage, emoji insights, and activity heatmaps**.  
It transforms raw text files into **data-driven visualizations** for exploring engagement patterns and user behavior.  

**Key Features:**  
1. **Summary Stats** – Messages, words, media, and links shared.  
2. **Timelines** – Monthly & daily chat activity trends.  
3. **User Contribution** – Most active users and participation share.  
4. **Activity Maps** – Busiest days, months, and weekly heatmap.  
5. **Word Cloud & NLP** – Frequent terms and language usage.  
6. **Emoji Analysis** – Top emojis with counts and visual charts.  

---

## 📊 Screenshots  

### 1️⃣ Summary & Timelines  
![Summary](Snapshots/summary.png)  

### 2️⃣ Activity Map
![WordCloud](Snapshots/activity_map.png)  

---
## 🔑 Insights Delivered  
- ✅ Identified **most active users** and their contribution to chats.  
- ✅ Highlighted **peak chat days, months, and hours** via activity maps.  
- ✅ Extracted **most common words** using NLP preprocessing.  
- ✅ Generated **emoji usage breakdown** for richer interaction analysis.  
- ✅ Visualized **timelines of conversation growth**.  

---

## 🛠 Tech Stack & Tools  
- **Python (3.8+)** – Core programming  
- **Streamlit** – Interactive web app interface  
- **Pandas & NumPy** – Data preprocessing & transformations  
- **Matplotlib** – Data visualization (timelines, bar charts, heatmaps)  
- **WordCloud** – NLP-based frequent word analysis  
- **emoji** – Emoji parsing & insights  
- **Custom Modules** – `preprocessor.py` & `helper.py` for text cleaning & analysis  

---

## 📂 Project Workflow  
1. **Data Input** – Upload exported WhatsApp `.txt` chat file  
2. **Preprocessing** – Clean system messages, remove stopwords/media/deleted entries  
3. **Feature Extraction** – Derive users, words, links, emojis, timelines  
4. **NLP Processing** – Tokenization, stopword filtering, word cloud generation  
5. **Visualization** – Generate charts, activity heatmaps, and emoji barplots  
6. **Interactive Exploration** – Analyze chats overall or per user via Streamlit controls  

---

## 📁 Folder Structure  
WhatsApp-Chat-Analyzer/
├── app.py # Streamlit application
├── preprocessor.py # Data cleaning & formatting
├── helper.py # Stats, timelines, NLP & visualization functions
├── requirements.txt # Python dependencies
├── Screenshots/ # Output visuals (word cloud, timelines, heatmap, etc.)
│ ├── Summary.png
│ ├── WordCloud.png
│ └── EmojiAnalysis.png
└── README.md
---

## 🚀 How to Run  
```bash
# Clone the repository
git clone https://github.com/your-username/WhatsApp-Chat-Analyzer.git  
cd WhatsApp-Chat-Analyzer  

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py  
