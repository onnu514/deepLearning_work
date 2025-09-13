# Lecture Summary Bot Local - Makefile

.PHONY: help install test run clean sample-summary

# 기본 타겟
help:
	@echo "Lecture Summary Bot Local - 사용 가능한 명령어:"
	@echo ""
	@echo "  install         - 의존성 설치"
	@echo "  test            - 단위 테스트 실행"
	@echo "  run             - 샘플 요약 생성 (기본 설정)"
	@echo "  run-mixed       - 혼합 타입 요약 생성"
	@echo "  run-keywords    - 키워드 요약 생성"
	@echo "  run-sentences   - 문장 요약 생성"
	@echo "  sample-summary  - 샘플 노트로 요약 생성"
	@echo "  clean           - 생성된 파일 정리"
	@echo "  lint            - 코드 스타일 검사"
	@echo ""

# 의존성 설치
install:
	pip install -r requirements.txt

# 단위 테스트 실행 (요약 생성기 테스트)
test:
	@echo "요약 생성기 테스트 실행"
	python summary_gen.py --notes notes --out test_summaries --type mixed --ext ".md" --verbose
	@echo "테스트 완료"

# 기본 실행 (mixed 타입)
run:
	python summary_gen.py --notes notes --out summaries --type mixed --verbose

# 혼합 타입 요약 생성
run-mixed:
	python summary_gen.py --notes notes --out summaries --type mixed --verbose

# 키워드 요약 생성
run-keywords:
	python summary_gen.py --notes notes --out summaries --type keywords --verbose

# 문장 요약 생성
run-sentences:
	python summary_gen.py --notes notes --out summaries --type sentences --verbose

# 샘플 노트로 요약 생성
sample-summary:
	python summary_gen.py --notes notes --out summaries --type mixed --ext ".md" --verbose

# 생성된 파일 정리
clean:
	rm -rf summaries/*.md
	rm -rf test_summaries/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete

# 코드 스타일 검사
lint:
	@echo "코드 스타일 검사 중..."
	@python -m py_compile summary_gen.py summary_rules.py summary_io_utils.py
	@echo "기본 문법 검사 완료"

# 개발용 전체 테스트
dev-test: clean test sample-summary
	@echo "개발 테스트 완료"

# 프로덕션 빌드 준비
build: clean test
	@echo "프로덕션 빌드 준비 완료"

# 도움말 표시
.DEFAULT_GOAL := help
