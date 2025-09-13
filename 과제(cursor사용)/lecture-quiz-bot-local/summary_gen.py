#!/usr/bin/env python3
"""
규칙 기반 요약 생성기 메인 CLI 인터페이스
외부 LLM이나 네트워크를 사용하지 않는 로컬 요약 생성 시스템
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional

from summary_rules import SummaryRuleEngine
from summary_io_utils import SummaryMarkdownWriter, FileProcessor, TextAnalyzer


def setup_logging(verbose: bool = False) -> None:
    """로깅 설정"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_arguments() -> argparse.Namespace:
    """명령행 인수 파싱"""
    parser = argparse.ArgumentParser(
        description='규칙 기반 요약 생성기 - 강의노트에서 자동으로 요약 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python summary_gen.py --notes notes --out summaries --type mixed
  python summary_gen.py --notes notes --out summaries --type keywords --lang ko --seed 42
  python summary_gen.py --notes notes --out summaries --type sentences --ext ".txt,.md" --verbose
        """
    )
    
    # 필수 인수
    parser.add_argument('--notes', required=True, 
                       help='강의노트가 있는 디렉토리 경로')
    parser.add_argument('--out', required=True,
                       help='요약 파일을 저장할 출력 디렉토리 경로')
    
    # 선택적 인수
    parser.add_argument('--type', choices=['keywords', 'sentences', 'mixed'], default='mixed',
                       help='요약 타입 (기본값: mixed)')
    parser.add_argument('--ext', default='.txt,.md',
                       help='처리할 파일 확장자 (쉼표로 구분, 기본값: .txt,.md)')
    parser.add_argument('--lang', choices=['ko', 'en'], default='ko',
                       help='언어 설정 (기본값: ko)')
    parser.add_argument('--seed', type=int, default=42,
                       help='랜덤 시드 (기본값: 42)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='상세 로그 출력')
    parser.add_argument('--max-keywords', type=int, default=50,
                       help='추출할 최대 키워드 수 (기본값: 50)')
    parser.add_argument('--chunk-size', type=int, default=8000,
                       help='텍스트 청킹 최대 크기 (기본값: 8000)')
    parser.add_argument('--summary-sentences', type=int, default=5,
                       help='요약에 포함할 문장 수 (기본값: 5)')
    
    return parser.parse_args()


def process_single_file(file_path: str, args: argparse.Namespace, 
                       summary_engine: SummaryRuleEngine, file_processor: FileProcessor,
                       markdown_writer: SummaryMarkdownWriter) -> Optional[str]:
    """단일 파일 처리"""
    logging.info(f"파일 처리 중: {file_path}")
    
    # 파일 읽기
    text = file_processor.read_file(file_path)
    if not text:
        logging.warning(f"파일 읽기 실패: {file_path}")
        return None
    
    # 텍스트 전처리
    text = file_processor.preprocess_text(text)
    
    # 텍스트 통계
    stats = TextAnalyzer.get_text_stats(text)
    logging.info(f"텍스트 통계 - 문자: {stats['char_count']}, 단어: {stats['word_count']}, 문장: {stats['sentence_count']}")
    
    # 청킹 필요 여부 확인
    if TextAnalyzer.should_chunk(text, args.chunk_size):
        logging.info("긴 텍스트 감지, 청킹 처리 중...")
        chunks = file_processor.chunk_text(text)
        logging.info(f"총 {len(chunks)}개 청크로 분할")
    else:
        chunks = [text]
    
    all_keywords = []
    all_summaries = []
    
    # 각 청크 처리
    for i, chunk in enumerate(chunks):
        logging.info(f"청크 {i+1}/{len(chunks)} 처리 중...")
        
        # 키워드 추출
        keywords = summary_engine.extract_keywords(chunk, args.lang, args.max_keywords)
        if not keywords:
            logging.warning(f"청크 {i+1}에서 키워드 추출 실패")
            continue
        
        all_keywords.extend(keywords)
        logging.info(f"청크 {i+1}에서 {len(keywords)}개 키워드 추출")
        
        # 요약 생성
        summary_data = summary_engine.generate_comprehensive_summary(chunk, args.type)
        
        if summary_data:
            all_summaries.append(summary_data)
            logging.info(f"청크 {i+1}에서 {args.type} 타입 요약 생성")
        else:
            logging.warning(f"청크 {i+1}에서 요약 생성 실패")
    
    if not all_summaries:
        logging.warning(f"파일에서 요약을 생성할 수 없습니다: {file_path}")
        return None
    
    # 키워드 정렬 및 중복 제거
    unique_keywords = list({kw: score for kw, score in all_keywords}.items())
    unique_keywords.sort(key=lambda x: x[1], reverse=True)
    
    # 통합 요약 생성
    if len(all_summaries) == 1:
        final_summary = all_summaries[0]
    else:
        # 여러 청크의 요약을 통합
        final_summary = merge_summaries(all_summaries, args.type)
    
    # 키워드 업데이트
    final_summary['keywords'] = unique_keywords[:50]
    
    # 마크다운 파일 작성
    basename = markdown_writer.get_basename(file_path)
    output_path = markdown_writer.write_summary_file(basename, final_summary)
    
    # 요약 통계
    logging.info(f"요약 완료 - 키워드: {len(unique_keywords)}개, 타입: {final_summary['type']}")
    
    return output_path


def merge_summaries(summaries: List[Dict], summary_type: str) -> Dict[str, any]:
    """여러 요약을 통합"""
    if summary_type == 'keywords':
        # 키워드 요약 통합
        all_keywords = []
        for summary in summaries:
            all_keywords.extend(summary.get('keywords', []))
        
        # 중복 제거 및 정렬
        unique_keywords = list({kw: score for kw, score in all_keywords}.items())
        unique_keywords.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'type': 'keywords',
            'content': f"**핵심 키워드**: {', '.join([kw for kw, score in unique_keywords[:10]])}\n\n**주요 키워드**: {', '.join([kw for kw, score in unique_keywords[10:20]])}",
            'keywords': unique_keywords[:20]
        }
    
    elif summary_type == 'sentences':
        # 문장 요약 통합
        all_sentences = []
        for summary in summaries:
            content = summary.get('content', '')
            if content:
                all_sentences.append(content)
        
        return {
            'type': 'sentences',
            'content': " ".join(all_sentences),
            'keywords': summaries[0].get('keywords', []) if summaries else []
        }
    
    else:  # mixed
        # 혼합 요약 통합
        all_sentences = []
        all_keywords = []
        
        for summary in summaries:
            if 'sentence_summary' in summary:
                all_sentences.append(summary['sentence_summary'])
            if 'keywords' in summary:
                all_keywords.extend(summary['keywords'])
        
        # 중복 제거 및 정렬
        unique_keywords = list({kw: score for kw, score in all_keywords}.items())
        unique_keywords.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'type': 'mixed',
            'sentence_summary': " ".join(all_sentences),
            'keyword_summary': f"**핵심 키워드**: {', '.join([kw for kw, score in unique_keywords[:10]])}",
            'core_concepts': [kw for kw, score in unique_keywords[:15]],
            'keywords': unique_keywords[:20]
        }


def main():
    """메인 함수"""
    args = parse_arguments()
    setup_logging(args.verbose)
    
    logging.info("규칙 기반 요약 생성기 시작")
    logging.info(f"설정 - 노트: {args.notes}, 출력: {args.out}, "
                f"타입: {args.type}")
    
    # 디렉토리 확인
    notes_path = Path(args.notes)
    if not notes_path.exists():
        logging.error(f"노트 디렉토리가 존재하지 않습니다: {args.notes}")
        sys.exit(1)
    
    # 컴포넌트 초기화
    summary_engine = SummaryRuleEngine(seed=args.seed)
    file_processor = FileProcessor(max_chunk_size=args.chunk_size)
    markdown_writer = SummaryMarkdownWriter(args.out)
    
    # 파일 확장자 파싱
    extensions = [ext.strip() for ext in args.ext.split(',')]
    logging.info(f"처리할 확장자: {extensions}")
    
    # 노트 파일 스캔
    note_files = file_processor.scan_notes_directory(args.notes, extensions)
    if not note_files:
        logging.error(f"노트 디렉토리에서 파일을 찾을 수 없습니다: {args.notes}")
        sys.exit(1)
    
    logging.info(f"총 {len(note_files)}개 파일 발견")
    
    # 각 파일 처리
    success_count = 0
    
    for file_path in note_files:
        try:
            output_path = process_single_file(
                file_path, args, summary_engine, file_processor, markdown_writer
            )
            
            if output_path:
                success_count += 1
                logging.info(f"요약 파일 생성 완료: {output_path}")
            else:
                logging.warning(f"파일 처리 실패: {file_path}")
                
        except Exception as e:
            logging.error(f"파일 처리 중 오류 발생 {file_path}: {e}")
            continue
    
    # 최종 결과
    logging.info("=" * 50)
    logging.info("처리 완료")
    logging.info(f"성공: {success_count}/{len(note_files)} 파일")
    logging.info(f"출력 디렉토리: {args.out}")
    
    if success_count == 0:
        logging.error("처리된 파일이 없습니다.")
        sys.exit(1)
    
    logging.info("요약 생성이 완료되었습니다!")


if __name__ == '__main__':
    main()
