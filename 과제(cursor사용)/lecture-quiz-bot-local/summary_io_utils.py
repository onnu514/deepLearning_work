"""
요약 생성을 위한 파일 입출력 및 마크다운 작성 모듈
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class SummaryMarkdownWriter:
    """요약 마크다운 파일 작성 클래스"""
    
    def __init__(self, output_dir: str):
        """마크다운 작성기 초기화"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def get_basename(self, file_path: str) -> str:
        """파일 경로에서 기본 이름 추출"""
        return Path(file_path).stem
    
    def write_summary_file(self, filename: str, summary_data: Dict[str, any]) -> str:
        """요약 파일을 마크다운으로 작성"""
        output_path = self.output_dir / f"{filename}_summary.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 헤더
            f.write(f"# {filename} 요약\n\n")
            
            # 요약 타입에 따른 내용 작성
            if summary_data['type'] == 'keywords':
                f.write("## 키워드 요약\n\n")
                f.write(summary_data['content'])
                f.write("\n\n")
                
            elif summary_data['type'] == 'sentences':
                f.write("## 문장 요약\n\n")
                f.write(summary_data['content'])
                f.write("\n\n")
                
            else:  # mixed
                # 문장 요약
                f.write("## 핵심 내용 요약\n\n")
                f.write(summary_data['sentence_summary'])
                f.write("\n\n")
                
                # 키워드 요약
                f.write("## 키워드 요약\n\n")
                f.write(summary_data['keyword_summary'])
                f.write("\n\n")
                
                # 주제별 요약
                f.write("## 주제별 키워드\n\n")
                f.write(summary_data['topic_summary'])
                f.write("\n\n")
            
            # 핵심 개념
            f.write("## 핵심 개념\n\n")
            for i, concept in enumerate(summary_data['core_concepts'][:15], 1):
                f.write(f"{i}. **{concept}**\n")
            f.write("\n")
            
            # 통계 정보 (mixed 타입인 경우)
            if summary_data['type'] == 'mixed' and 'statistics' in summary_data:
                f.write("## 요약 통계\n\n")
                stats = summary_data['statistics']
                f.write(f"- **원문 문장 수**: {stats['원문_문장수']}개\n")
                f.write(f"- **원문 단어 수**: {stats['원문_단어수']}개\n")
                f.write(f"- **원문 문자 수**: {stats['원문_문자수']}자\n")
                f.write(f"- **요약 문장 수**: {stats['요약_문장수']}개\n")
                f.write(f"- **압축률**: {stats['압축률']}\n\n")
            
            # 상세 키워드 목록
            f.write("## 상세 키워드 목록\n\n")
            keywords = summary_data['keywords']
            for i, (keyword, score) in enumerate(keywords, 1):
                f.write(f"{i}. **{keyword}** (중요도: {score:.3f})\n")
        
        return str(output_path)
    
    def write_simple_summary(self, filename: str, summary_text: str, keywords: List[Tuple[str, float]]) -> str:
        """간단한 요약 파일 작성"""
        output_path = self.output_dir / f"{filename}_simple_summary.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {filename} 간단 요약\n\n")
            f.write("## 요약\n\n")
            f.write(summary_text)
            f.write("\n\n")
            f.write("## 주요 키워드\n\n")
            for keyword, score in keywords[:10]:
                f.write(f"- **{keyword}** (중요도: {score:.3f})\n")
        
        return str(output_path)


class FileProcessor:
    """파일 처리 및 전처리 클래스"""
    
    def __init__(self, max_chunk_size: int = 8000, min_chunk_size: int = 6000):
        """파일 프로세서 초기화"""
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
    
    def scan_notes_directory(self, notes_dir: str, extensions: List[str]) -> List[str]:
        """노트 디렉토리에서 파일 스캔"""
        notes_path = Path(notes_dir)
        if not notes_path.exists():
            return []
        
        files = []
        for ext in extensions:
            pattern = f"**/*{ext}"
            files.extend(notes_path.glob(pattern))
        
        return [str(f) for f in files if f.is_file()]
    
    def read_file(self, file_path: str) -> Optional[str]:
        """파일 읽기 (인코딩 자동 감지)"""
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        print(f"파일 읽기 실패: {file_path}")
        return None
    
    def chunk_text(self, text: str) -> List[str]:
        """긴 텍스트를 청크로 분할"""
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # 문단 단위로 분할 (빈 줄 기준)
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            # 문단이 너무 크면 문장 단위로 분할
            if len(paragraph) > self.max_chunk_size:
                sentences = self._split_into_sentences(paragraph)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > self.max_chunk_size:
                        if len(current_chunk) >= self.min_chunk_size:
                            chunks.append(current_chunk.strip())
                            current_chunk = sentence
                        else:
                            current_chunk += " " + sentence
                    else:
                        current_chunk += " " + sentence
            else:
                if len(current_chunk) + len(paragraph) > self.max_chunk_size:
                    if len(current_chunk) >= self.min_chunk_size:
                        chunks.append(current_chunk.strip())
                        current_chunk = paragraph
                    else:
                        current_chunk += "\n\n" + paragraph
                else:
                    current_chunk += "\n\n" + paragraph
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """문장 단위로 분할"""
        # 문장 끝 패턴
        sentence_pattern = r'[.!?]+\s*'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 불필요한 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        # 마크다운 문법 정리
        text = re.sub(r'#{1,6}\s*', '', text)  # 헤더 제거
        text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)  # 볼드/이탤릭 제거
        text = re.sub(r'`([^`]+)`', r'\1', text)  # 인라인 코드 제거
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # 링크 제거
        
        return text.strip()


class TextAnalyzer:
    """텍스트 분석 및 통계 클래스"""
    
    @staticmethod
    def get_text_stats(text: str) -> Dict[str, int]:
        """텍스트 통계 정보 반환"""
        return {
            'char_count': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()])
        }
    
    @staticmethod
    def should_chunk(text: str, max_size: int = 10000) -> bool:
        """텍스트를 청킹해야 하는지 판단"""
        return len(text) > max_size
