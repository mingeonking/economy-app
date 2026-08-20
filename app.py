import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import quote

st.set_page_config(page_title="기업 리스크 & 경제 뉴스 검색엔진", layout="wide")
st.title("📊 기업 매출 & 악재 리스크 실시간 탐지 검색엔진")

search_query = st.text_input("검색하고 싶은 기업명 또는 경제 키워드를 입력하세요:", "카카오")

if search_query:
    st.subheader(f"🔍 '{search_query}' 실시간 분석 결과")
    
    with st.spinner("최신 경제 뉴스를 가져오는 중..."):
        news_results = []
        try:
            # 검색 범위를 넓히기 위해 기업명 뒤에 '뉴스' 키워드 조합
            encoded_query = quote(f"{search_query}")
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
            
            req = urllib.request.Request(
                rss_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            response = urllib.request.urlopen(req)
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # 수집 뉴스 건수를 30건으로 확대
            for item in root.findall('.//item')[:30]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else '#'
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                
                news_results.append({
                    'title': title,
                    'snippet': f"발행일: {pubDate}",
                    'link': link
                })
        except Exception as e:
            st.error(f"뉴스 수집 오류: {e}")

    if not news_results:
        st.warning("검색 결과가 없습니다.")
    else:
        sales_news = []
        risk_news = []
        all_news = []

        # 1. 악재 키워드 대폭 확장
        risk_keywords = [
            "소송", "횡령", "적자", "하락", "파업", "규제", "과징금", "위기", "수사", 
            "배임", "피소", "단속", "감소", "급락", "논란", "의혹", "검찰", "제재", 
            "반토막", "손실", "우려", "악재", "타격", "부진"
        ]
        
        # 2. 매출/실적 키워드 대폭 확장
        sales_keywords = [
            "매출", "실적", "영업이익", "순이익", "공시", "수주", "흑자", "성장", 
            "영업익", "IR", "배당", "전망", "증가", "최대", "달성"
        ]

        for item in news_results:
            title = item['title']
            snippet = item['snippet']
            link = item['link']

            news_data = {"title": title, "snippet": snippet, "link": link}
            all_news.append(news_data)

            # 제목 내 키워드 감지
            if any(word in title for word in sales_keywords):
                sales_news.append(news_data)

            if any(word in title for word in risk_keywords):
                risk_news.append(news_data)

        # 수치 요약 출력
        col1, col2, col3 = st.columns(3)
        col1.metric("수집된 전체 뉴스", f"{len(all_news)}건")
        col2.metric("매출/실적 관련 기사", f"{len(sales_news)}건")
        col3.metric("⚠️ 악재 리스크 감지", f"{len(risk_news)}건")

        st.markdown("---")

        # 결과 탭 출력
        tab1, tab2, tab3 = st.tabs(["🚨 악재(Risk) 경보 뉴스", "💰 매출/실적 뉴스", "📰 전체 뉴스 목록"])

        with tab1:
            if risk_news:
                st.error(f"주요 위험 키워드가 포착된 뉴스입니다. (총 {len(risk_news)}건)")
                for n in risk_news:
                    st.write(f"**[{n['title']}]({n['link']})**")
                    st.caption(n['snippet'])
                    st.write("---")
            else:
                st.info("포착된 악재 관련 뉴스가 없습니다.")

        with tab2:
            if sales_news:
                st.success(f"기업의 재무/실적 관련 뉴스입니다. (총 {len(sales_news)}건)")
                for n in sales_news:
                    st.write(f"**[{n['title']}]({n['link']})**")
                    st.caption(n['snippet'])
                    st.write("---")
            else:
                st.info("포착된 매출/실적 관련 뉴스가 없습니다.")

        with tab3:
            for n in all_news:
                st.write(f"**[{n['title']}]({n['link']})**")
                st.caption(n['snippet'])
                st.write("---")
                