"""
규칙 기반 텍스트 요약 생성의 핵심 로직을 담당하는 모듈
- 핵심 문장 추출
- 키워드 기반 요약
- 구조화된 요약 생성
"""

import re
import random
from typing import List, Dict, Tuple, Set, Optional
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class SummaryRuleEngine:
    """규칙 기반 요약 생성 엔진"""
    
    def __init__(self, seed: int = 42):
        """요약 생성 엔진 초기화"""
        random.seed(seed)
        np.random.seed(seed)
        
        # 한국어/영어 혼합 stopwords
        self.stopwords = {
            'ko': {'이', '그', '저', '것', '수', '있', '하', '되', '되다', '있다', '하다', '되다', 
                   '의', '가', '을', '를', '에', '에서', '로', '으로', '와', '과', '도', '는', '은',
                   '이다', '다', '이다', '이다', '이다', '이다', '이다', '이다', '이다', '이다'},
            'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
                   'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
                   'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                   'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        }
        
        # TF-IDF 벡터화기 설정
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1000,
            stop_words=None,  # 커스텀 stopwords 사용
            token_pattern=r'\b\w+\b',
            lowercase=True
        )
    
    def split_sentences(self, text: str) -> List[str]:
        """정규식 기반 문장 분할"""
        # 문장 끝 패턴: ., ?, !, 줄바꿈
        sentence_pattern = r'[.!?]+\s*|\n+'
        sentences = re.split(sentence_pattern, text)
        
        # 빈 문장 제거 및 공백 정리
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def extract_keywords(self, text: str, lang: str = 'ko', top_k: int = 50) -> List[Tuple[str, float]]:
        """TF-IDF를 사용한 키워드 추출"""
        # 문장 분할
        sentences = self.split_sentences(text)
        
        # TF-IDF 벡터화
        try:
            tfidf_matrix = self.vectorizer.fit_transform(sentences)
            feature_names = self.vectorizer.get_feature_names_out()
            scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
            
            # 키워드-점수 쌍 생성
            keyword_scores = list(zip(feature_names, scores))
            
            # 점수 기준 정렬
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 필터링: stopwords 제거, 길이 체크, 숫자/특수문자 제거
            filtered_keywords = []
            for keyword, score in keyword_scores:
                if (len(keyword) >= 2 and 
                    keyword not in self.stopwords.get(lang, set()) and
                    not keyword.isdigit() and
                    keyword.isalnum()):
                    filtered_keywords.append((keyword, score))
            
            return filtered_keywords[:top_k]
            
        except Exception as e:
            print(f"키워드 추출 오류: {e}")
            return []
    
    def extract_important_sentences(self, text: str, num_sentences: int = 5) -> List[Tuple[str, float]]:
        """중요한 문장 추출"""
        sentences = self.split_sentences(text)
        if not sentences:
            return []
        
        # TF-IDF로 문장 중요도 계산
        try:
            tfidf_matrix = self.vectorizer.fit_transform(sentences)
            sentence_scores = np.asarray(tfidf_matrix.sum(axis=1)).flatten()
            
            # 문장-점수 쌍 생성
            sentence_score_pairs = list(zip(sentences, sentence_scores))
            
            # 점수 기준 정렬
            sentence_score_pairs.sort(key=lambda x: x[1], reverse=True)
            
            return sentence_score_pairs[:num_sentences]
            
        except Exception as e:
            print(f"문장 추출 오류: {e}")
            return []
    
    def create_keyword_summary(self, keywords: List[Tuple[str, float]], max_keywords: int = 20) -> str:
        """키워드 기반 요약 생성"""
        if not keywords:
            return "키워드를 추출할 수 없습니다."
        
        # 상위 키워드 선택
        top_keywords = keywords[:max_keywords]
        
        # 키워드를 카테고리별로 그룹화
        summary_parts = []
        
        # 핵심 키워드 (상위 5개)
        core_keywords = [kw for kw, score in top_keywords[:5]]
        summary_parts.append(f"**핵심 키워드**: {', '.join(core_keywords)}")
        
        # 주요 키워드 (6-15번째)
        if len(top_keywords) > 5:
            main_keywords = [kw for kw, score in top_keywords[5:15]]
            summary_parts.append(f"**주요 키워드**: {', '.join(main_keywords)}")
        
        return "\n\n".join(summary_parts)
    
    def create_sentence_summary(self, text: str, num_sentences: int = 5) -> str:
        """문장 기반 요약 생성"""
        important_sentences = self.extract_important_sentences(text, num_sentences)
        
        if not important_sentences:
            return "중요한 문장을 추출할 수 없습니다."
        
        # 문장들을 원문 순서대로 정렬
        sentences = self.split_sentences(text)
        summary_sentences = []
        
        for sentence, score in important_sentences:
            if sentence in sentences:
                summary_sentences.append(sentence)
        
        return " ".join(summary_sentences)
    
    def create_structured_summary(self, text: str, keywords: List[Tuple[str, float]]) -> Dict[str, str]:
        """구조화된 요약 생성"""
        # 문장 기반 요약
        sentence_summary = self.create_sentence_summary(text, 5)
        
        # 키워드 기반 요약
        keyword_summary = self.create_keyword_summary(keywords, 20)
        
        # 핵심 개념 추출
        core_concepts = [kw for kw, score in keywords[:10]]
        
        # 요약 통계
        sentences = self.split_sentences(text)
        words = text.split()
        
        stats = {
            '원문_문장수': len(sentences),
            '원문_단어수': len(words),
            '원문_문자수': len(text),
            '요약_문장수': len(sentence_summary.split('.')),
            '압축률': f"{len(sentence_summary) / len(text) * 100:.1f}%"
        }
        
        return {
            'sentence_summary': sentence_summary,
            'keyword_summary': keyword_summary,
            'core_concepts': core_concepts,
            'statistics': stats
        }
    
    def create_topic_summary(self, text: str, keywords: List[Tuple[str, float]]) -> str:
        """주제별 요약 생성"""
        # 키워드를 주제별로 그룹화 (간단한 규칙 기반)
        topics = {
            '개념/정의': [],
            '특징/장점': [],
            '응용/사용': [],
            '기술/방법': [],
            '기타': []
        }
        
        for keyword, score in keywords[:20]:
            # 간단한 키워드 분류 규칙
            if any(word in keyword.lower() for word in ['정의', '개념', '의미', '이해']):
                topics['개념/정의'].append(keyword)
            elif any(word in keyword.lower() for word in ['특징', '장점', '효과', '성능']):
                topics['특징/장점'].append(keyword)
            elif any(word in keyword.lower() for word in ['응용', '사용', '활용', '적용']):
                topics['응용/사용'].append(keyword)
            elif any(word in keyword.lower() for word in ['기술', '방법', '알고리즘', '기법']):
                topics['기술/방법'].append(keyword)
            else:
                topics['기타'].append(keyword)
        
        # 주제별 요약 생성
        topic_summary = []
        for topic, keywords_list in topics.items():
            if keywords_list:
                topic_summary.append(f"**{topic}**: {', '.join(keywords_list[:5])}")
        
        return "\n\n".join(topic_summary)
    
    def generate_comprehensive_summary(self, text: str, summary_type: str = 'mixed') -> Dict[str, any]:
        """종합적인 요약 생성"""
        # 키워드 추출
        keywords = self.extract_keywords(text, 'ko', 50)
        
        if summary_type == 'keywords':
            return {
                'type': 'keywords',
                'content': self.create_keyword_summary(keywords, 20),
                'keywords': keywords[:20],
                'core_concepts': [kw for kw, score in keywords[:15]]
            }
        elif summary_type == 'sentences':
            return {
                'type': 'sentences',
                'content': self.create_sentence_summary(text, 5),
                'keywords': keywords[:20],
                'core_concepts': [kw for kw, score in keywords[:15]]
            }
        else:  # mixed
            structured = self.create_structured_summary(text, keywords)
            topic = self.create_topic_summary(text, keywords)
            
            return {
                'type': 'mixed',
                'sentence_summary': structured['sentence_summary'],
                'keyword_summary': structured['keyword_summary'],
                'topic_summary': topic,
                'core_concepts': structured['core_concepts'],
                'statistics': structured['statistics'],
                'keywords': keywords[:20]
            }
