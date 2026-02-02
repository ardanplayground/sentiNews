import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from collections import Counter
import requests

# ============================================================================
# SENTIMENT ANALYZER CLASS
# ============================================================================
class SentimentAnalyzer:
    """Analisis sentimen menggunakan keyword-based approach"""
    
    def __init__(self):
        # Kata-kata positif dalam bahasa Indonesia dan Inggris
        self.positive_words_id = [
            'naik', 'meningkat', 'positif', 'untung', 'profit', 'bagus', 'baik',
            'optimis', 'bullish', 'rally', 'menguat', 'cemerlang', 'peluang',
            'potensi', 'keuntungan', 'surplus', 'tumbuh', 'berkembang', 'maju',
            'sukses', 'hebat', 'luar biasa', 'fantastis', 'menggembirakan',
            'menjanjikan', 'kuat', 'solid', 'stabil', 'aman', 'percaya diri'
        ]
        
        self.positive_words_en = [
            'surge', 'gain', 'rise', 'up', 'higher', 'growth', 'increase',
            'boost', 'strong', 'recover', 'soar', 'jump', 'rally', 'bullish',
            'positive', 'profit', 'good', 'great', 'excellent', 'outstanding',
            'impressive', 'promising', 'optimistic', 'confident', 'solid',
            'stable', 'secure', 'success', 'win', 'breakthrough', 'advance'
        ]
        
        # Kata-kata negatif dalam bahasa Indonesia dan Inggris
        self.negative_words_id = [
            'turun', 'menurun', 'negatif', 'rugi', 'loss', 'buruk', 'jelek',
            'pesimis', 'bearish', 'crash', 'anjlok', 'melemah', 'risiko',
            'bahaya', 'krisis', 'kerugian', 'defisit', 'gagal', 'mundur',
            'jatuh', 'tertekan', 'lemah', 'khawatir', 'takut', 'panik',
            'masalah', 'kesulitan', 'hambatan', 'kendala', 'ancaman'
        ]
        
        self.negative_words_en = [
            'drop', 'fall', 'down', 'lower', 'decline', 'decrease', 'plunge',
            'weak', 'slump', 'tumble', 'bearish', 'negative', 'loss', 'bad',
            'poor', 'terrible', 'awful', 'disappointing', 'concerning',
            'worrying', 'risk', 'danger', 'crisis', 'fail', 'problem',
            'difficulty', 'obstacle', 'threat', 'fear', 'panic', 'crash'
        ]
        
        self.all_positive = self.positive_words_id + self.positive_words_en
        self.all_negative = self.negative_words_id + self.negative_words_en
    
    def analyze(self, text):
        """Analisis sentimen dari teks"""
        if not text:
            return 'neutral', 0, {'positive': [], 'negative': []}
        
        text_lower = text.lower()
        
        # Hitung kata-kata positif dan negatif yang ditemukan
        positive_matches = [word for word in self.all_positive if word in text_lower]
        negative_matches = [word for word in self.all_negative if word in text_lower]
        
        positive_count = len(positive_matches)
        negative_count = len(negative_matches)
        
        total_sentiment_words = positive_count + negative_count
        
        # Tentukan sentimen
        if total_sentiment_words == 0:
            sentiment = 'neutral'
            confidence = 0
        elif positive_count > negative_count:
            sentiment = 'positive'
            confidence = (positive_count / total_sentiment_words) * 100
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = (negative_count / total_sentiment_words) * 100
        else:
            sentiment = 'neutral'
            confidence = 50
        
        keyword_matches = {
            'positive': positive_matches[:5],
            'negative': negative_matches[:5]
        }
        
        return sentiment, round(confidence, 1), keyword_matches
    
    def analyze_batch(self, articles):
        """Analisis sentimen untuk banyak artikel sekaligus"""
        analyzed = []
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
            sentiment, confidence, keywords = self.analyze(text)
            
            analyzed.append({
                **article,
                'sentiment': sentiment,
                'confidence': confidence,
                'keywords': keywords
            })
        
        return analyzed


# ============================================================================
# NEWS API CLIENT CLASS
# ============================================================================
class NewsAPIClient:
    """Client untuk berbagai News API gratis"""
    
    def __init__(self):
        # ========================================================================
        # API KEYS - SUDAH DIISI
        # ========================================================================
        
        self.newsdata_key = "pub_cde750ce48074b45a714654be4063bf4"
        self.gnews_key = "20279dd1f36d7ad62d50144631657942"
        
    def fetch_newsdata_io(self, query, language='en', max_results=50):
        """NewsData.io API - Free tier: 200 requests/day"""
        url = "https://newsdata.io/api/1/news"
        
        params = {
            'apikey': self.newsdata_key,
            'q': query,
            'language': language,
            'size': min(max_results, 50)
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                if data.get('status') == 'success' and 'results' in data:
                    for item in data['results']:
                        articles.append({
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'content': item.get('content', ''),
                            'source': item.get('source_id', 'Unknown'),
                            'url': item.get('link', ''),
                            'publishedAt': item.get('pubDate', ''),
                            'image': item.get('image_url', '')
                        })
                
                return articles
            else:
                return []
                
        except Exception as e:
            st.warning(f"NewsData.io: {str(e)[:50]}")
            return []
    
    def fetch_gnews(self, query, language='en', country=None, max_results=50):
        """GNews API - Free tier: 100 requests/day"""
        url = "https://gnews.io/api/v4/search"
        
        params = {
            'q': query,
            'lang': language,
            'max': min(max_results, 100),
            'apikey': self.gnews_key
        }
        
        if country:
            params['country'] = country
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                if 'articles' in data:
                    for item in data['articles']:
                        articles.append({
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'content': item.get('content', ''),
                            'source': item.get('source', {}).get('name', 'Unknown'),
                            'url': item.get('url', ''),
                            'publishedAt': item.get('publishedAt', ''),
                            'image': item.get('image', '')
                        })
                
                return articles
            else:
                return []
                
        except Exception as e:
            st.warning(f"GNews: {str(e)[:50]}")
            return []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def aggregate_news(query, news_type='both', max_articles=100):
    """Mengumpulkan berita dari berbagai sumber API"""
    client = NewsAPIClient()
    all_articles = []
    
    if news_type in ['international', 'both']:
        # Ambil dari NewsData.io (English)
        articles1 = client.fetch_newsdata_io(query, language='en', max_results=50)
        all_articles.extend(articles1)
        time.sleep(0.5)
        
        # Ambil dari GNews (English)
        articles2 = client.fetch_gnews(query, language='en', max_results=50)
        all_articles.extend(articles2)
        time.sleep(0.5)
    
    if news_type in ['local', 'both']:
        # Ambil dari GNews (Indonesia)
        articles3 = client.fetch_gnews(query, language='id', country='id', max_results=50)
        all_articles.extend(articles3)
        time.sleep(0.5)
        
        # Ambil dari NewsData.io (Indonesia)
        articles4 = client.fetch_newsdata_io(query, language='id', max_results=50)
        all_articles.extend(articles4)
    
    # Hapus duplikat
    seen_titles = set()
    unique_articles = []
    
    for article in all_articles:
        title = article.get('title', '').strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    return unique_articles[:max_articles]


def create_sentiment_summary(analyzed_articles):
    """Membuat ringkasan sentimen"""
    if not analyzed_articles:
        return None
    
    total = len(analyzed_articles)
    sentiments = [a['sentiment'] for a in analyzed_articles]
    
    positive_count = sentiments.count('positive')
    negative_count = sentiments.count('negative')
    neutral_count = sentiments.count('neutral')
    
    positive_pct = (positive_count / total) * 100
    negative_pct = (negative_count / total) * 100
    neutral_pct = (neutral_count / total) * 100
    
    if positive_pct > negative_pct + 15:
        overall_trend = "SANGAT POSITIF"
        trend_emoji = "📈🚀"
    elif positive_pct > negative_pct + 5:
        overall_trend = "POSITIF"
        trend_emoji = "📈"
    elif negative_pct > positive_pct + 15:
        overall_trend = "SANGAT NEGATIF"
        trend_emoji = "📉💔"
    elif negative_pct > positive_pct + 5:
        overall_trend = "NEGATIF"
        trend_emoji = "📉"
    else:
        overall_trend = "NETRAL"
        trend_emoji = "➡️"
    
    avg_confidence = sum(a.get('confidence', 0) for a in analyzed_articles) / total if total > 0 else 0
    
    return {
        'total': total,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'positive_pct': positive_pct,
        'negative_pct': negative_pct,
        'neutral_pct': neutral_pct,
        'overall_trend': overall_trend,
        'trend_emoji': trend_emoji,
        'avg_confidence': avg_confidence
    }


# ============================================================================
# STREAMLIT APP
# ============================================================================
st.set_page_config(
    page_title="Sentiment Analysis - Berita & Saham",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .positive-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .negative-box {
        background-color: #f8d7da;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .neutral-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if 'analyzed_articles' not in st.session_state:
    st.session_state.analyzed_articles = None
if 'summary' not in st.session_state:
    st.session_state.summary = None

# Header
st.markdown("""
    <div class="main-header">
        <h1>📊 Sentiment Analysis Dashboard</h1>
        <p style="font-size: 1.1rem;">Analisis Sentimen Real-time untuk Crypto & Saham</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan Analisis")
    
    # Preset topics
    preset_topics = {
        "Custom": "",
        "Bitcoin (BTC)": "BTC Bitcoin",
        "Ripple (XRP)": "XRP Ripple",
        "Ethereum (ETH)": "ETH Ethereum",
        "Aneka Tambang (ANTM)": "ANTM Aneka Tambang",
        "Telkom (TLKM)": "TLKM Telkom Indonesia",
        "Bank BRI (BBRI)": "BBRI Bank BRI",
        "Bank BCA (BBCA)": "BBCA Bank BCA"
    }
    
    selected_preset = st.selectbox(
        "Pilih Preset atau Custom",
        list(preset_topics.keys())
    )
    
    if selected_preset == "Custom":
        topic = st.text_input(
            "Masukkan Topik/Ticker",
            value="",
            placeholder="Contoh: BTC, XRP, ANTM, TLKM"
        ).strip()
    else:
        topic = preset_topics[selected_preset]
        st.info(f"📌 Topik: **{selected_preset}**")
    
    st.markdown("---")
    
    news_source = st.radio(
        "🌍 Sumber Berita",
        ["Keduanya", "Internasional", "Lokal (Indonesia)"]
    )
    
    news_type_map = {
        "Keduanya": "both",
        "Internasional": "international",
        "Lokal (Indonesia)": "local"
    }
    news_type = news_type_map[news_source]
    
    st.markdown("---")
    
    with st.expander("🔧 Pengaturan Lanjutan"):
        max_articles = st.slider(
            "Jumlah Maksimal Berita",
            min_value=10,
            max_value=200,
            value=100,
            step=10
        )
        
        show_confidence = st.checkbox("Tampilkan Confidence Score", value=True)
        show_keywords = st.checkbox("Tampilkan Keyword Matches", value=True)
    
    st.markdown("---")
    
    analyze_button = st.button("🚀 MULAI ANALISIS", type="primary")
    
    st.markdown("---")
    
    st.markdown("""
    ### 💡 API yang Digunakan
    
    **2 Sumber Berita:**
    - ✅ NewsData.io (200 req/hari)
    - ✅ GNews.io (100 req/hari)
    
    **Status:** Siap Digunakan! 🚀
    
    Total: ~300 requests/hari
    """)

# Main Content
if analyze_button:
    if not topic:
        st.warning("⚠️ Mohon masukkan topik/ticker!")
    else:
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        with progress_placeholder.container():
            st.markdown(f"### 🔍 Menganalisis: **{topic.upper()}**")
            progress_bar = st.progress(0)
            
            status_placeholder.info("📡 Mengumpulkan berita...")
            progress_bar.progress(10)
            
            start_time = time.time()
            
            # Fetch news
            all_articles = aggregate_news(topic, news_type, max_articles)
            progress_bar.progress(40)
            
            if not all_articles:
                status_placeholder.error("❌ Tidak ada berita ditemukan")
                progress_bar.empty()
            else:
                status_placeholder.success(f"✅ {len(all_articles)} berita dikumpulkan")
                time.sleep(0.3)
                
                # Analyze sentiment
                status_placeholder.info("🤖 Menganalisis sentimen...")
                progress_bar.progress(60)
                
                analyzer = SentimentAnalyzer()
                analyzed_articles = analyzer.analyze_batch(all_articles)
                
                progress_bar.progress(80)
                
                # Create summary
                status_placeholder.info("📊 Membuat ringkasan...")
                summary = create_sentiment_summary(analyzed_articles)
                
                progress_bar.progress(100)
                
                st.session_state.analyzed_articles = analyzed_articles
                st.session_state.summary = summary
                
                elapsed_time = time.time() - start_time
                status_placeholder.success(f"✅ Selesai dalam {elapsed_time:.1f} detik!")
                time.sleep(1)
                
        progress_placeholder.empty()
        status_placeholder.empty()

# Display Results
if st.session_state.summary and st.session_state.analyzed_articles:
    summary = st.session_state.summary
    analyzed_articles = st.session_state.analyzed_articles
    
    # Overall Sentiment
    trend_class = "positive-box" if "POSITIF" in summary['overall_trend'] else \
                  "negative-box" if "NEGATIF" in summary['overall_trend'] else "neutral-box"
    
    st.markdown(f"""
        <div class="{trend_class}">
            <h2>{summary['trend_emoji']} Trend: {summary['overall_trend']}</h2>
            <p>Berdasarkan {summary['total']} berita</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📰 Total Berita", summary['total'])
    
    with col2:
        st.metric("😊 Positif", f"{summary['positive_pct']:.1f}%",
                 delta=f"{summary['positive_count']} berita")
    
    with col3:
        st.metric("😟 Negatif", f"{summary['negative_pct']:.1f}%",
                 delta=f"{summary['negative_count']} berita", delta_color="inverse")
    
    with col4:
        st.metric("😐 Netral", f"{summary['neutral_pct']:.1f}%",
                 delta=f"{summary['neutral_count']} berita", delta_color="off")
    
    # Visualization
    st.markdown("---")
    st.markdown("### 📊 Visualisasi Sentimen")
    
    chart_data = pd.DataFrame({
        'Sentimen': ['Positif', 'Negatif', 'Netral'],
        'Jumlah': [summary['positive_count'], summary['negative_count'], summary['neutral_count']]
    })
    
    st.bar_chart(chart_data.set_index('Sentimen')['Jumlah'])
    
    # News List
    st.markdown("---")
    st.markdown("### 📰 Daftar Berita")
    
    # Filters
    col1, col2 = st.columns([2, 2])
    
    with col1:
        sentiment_filter = st.multiselect(
            "Filter Sentimen",
            ['positive', 'negative', 'neutral'],
            default=['positive', 'negative', 'neutral'],
            format_func=lambda x: {'positive': '😊 Positif', 'negative': '😟 Negatif', 'neutral': '😐 Netral'}[x]
        )
    
    with col2:
        all_sources = sorted(list(set([a['source'] for a in analyzed_articles])))
        source_filter = st.multiselect(
            "Filter Sumber",
            all_sources,
            default=all_sources[:10] if len(all_sources) > 10 else all_sources
        )
    
    filtered_articles = [
        a for a in analyzed_articles
        if a['sentiment'] in sentiment_filter and a['source'] in source_filter
    ]
    
    st.markdown(f"**Menampilkan {len(filtered_articles)} dari {summary['total']} berita**")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs([
        f"😊 Positif ({summary['positive_count']})",
        f"😟 Negatif ({summary['negative_count']})",
        f"😐 Netral ({summary['neutral_count']})"
    ])
    
    def display_articles(articles, max_display=30):
        if not articles:
            st.info("Tidak ada berita")
            return
        
        for idx, article in enumerate(articles[:max_display], 1):
            emoji = {'positive': '😊', 'negative': '😟', 'neutral': '😐'}[article['sentiment']]
            color = {'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#ffc107'}[article['sentiment']]
            
            with st.expander(f"{emoji} {idx}. {article['title'][:80]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Sumber:** {article['source']}")
                    st.markdown(f"**Deskripsi:** {article.get('description', 'N/A')}")
                    
                    if show_keywords and 'keywords' in article:
                        kw = article['keywords']
                        if kw['positive']:
                            st.markdown(f"✅ **Positif:** {', '.join(kw['positive'][:3])}")
                        if kw['negative']:
                            st.markdown(f"❌ **Negatif:** {', '.join(kw['negative'][:3])}")
                    
                    if article.get('url'):
                        st.markdown(f"[🔗 Baca]({article['url']})")
                
                with col2:
                    st.markdown(f"<div style='background:{color};color:white;padding:0.5rem;border-radius:5px;text-align:center;'><b>{article['sentiment'].upper()}</b></div>", unsafe_allow_html=True)
                    if show_confidence:
                        st.metric("Confidence", f"{article.get('confidence', 0):.1f}%")
    
    with tab1:
        display_articles([a for a in filtered_articles if a['sentiment'] == 'positive'])
    
    with tab2:
        display_articles([a for a in filtered_articles if a['sentiment'] == 'negative'])
    
    with tab3:
        display_articles([a for a in filtered_articles if a['sentiment'] == 'neutral'])
    
    # Export
    st.markdown("---")
    st.markdown("### 💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        df_export = pd.DataFrame([{
            'Title': a['title'],
            'Description': a.get('description', ''),
            'Source': a['source'],
            'Sentiment': a['sentiment'],
            'Confidence': a.get('confidence', 0),
            'URL': a.get('url', '')
        } for a in analyzed_articles])
        
        csv = df_export.to_csv(index=False)
        
        st.download_button(
            "📥 Download CSV",
            csv,
            f"sentiment_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        report = f"""SENTIMENT ANALYSIS REPORT
========================
Topik: {topic.upper()}
Tanggal: {datetime.now().strftime('%d %B %Y %H:%M')}

RINGKASAN:
- Total: {summary['total']}
- Trend: {summary['overall_trend']}

DISTRIBUSI:
- Positif: {summary['positive_count']} ({summary['positive_pct']:.1f}%)
- Negatif: {summary['negative_count']} ({summary['negative_pct']:.1f}%)
- Netral: {summary['neutral_count']} ({summary['neutral_pct']:.1f}%)
"""
        
        st.download_button(
            "📄 Download Report",
            report,
            f"report_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            "text/plain",
            use_container_width=True
        )

else:
    # Welcome Screen
    st.markdown("### 👋 Selamat Datang!")
    
    st.info("""
    **Cara Pakai:**
    1. 👈 Pilih topik di sidebar
    2. 🌍 Pilih sumber berita
    3. 🚀 Klik "MULAI ANALISIS"
    4. 📊 Lihat hasil & export data
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### ✨ Fitur
        - Analisis otomatis
        - Multi-source
        - Real-time
        - Export CSV/TXT
        """)
    
    with col2:
        st.markdown("""
        #### 🎯 Topik
        - Crypto (BTC, XRP)
        - Saham (ANTM, TLKM)
        - Custom topic
        """)
    
    with col3:
        st.markdown("""
        #### 📡 API
        - NewsData.io ✅
        - GNews.io ✅
        - Total: 300 req/hari
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#666;padding:1rem;">
    <p><b>📊 Sentiment Analysis Dashboard</b></p>
    <p>Powered by NewsData.io & GNews.io</p>
    <p style="font-size:0.9rem;">✅ API Keys sudah terpasang - Siap digunakan!</p>
</div>
""", unsafe_allow_html=True)
