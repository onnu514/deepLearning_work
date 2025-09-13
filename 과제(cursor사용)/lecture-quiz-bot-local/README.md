# Lecture Summary Bot Local

외부 LLM이나 네트워크를 전혀 사용하지 않는 **규칙 기반 요약 생성기**입니다. 강의노트(.txt, .md)에서 핵심 개념을 추출하여 키워드/문장/혼합 형태의 요약을 자동 생성하고 Markdown으로 저장합니다.

## 🚀 주요 기능

- **완전 로컬 처리**: 외부 API나 네트워크 연결 없이 동작
- **다양한 요약 타입**: 키워드 중심, 문장 중심, 혼합 요약
- **지능적 텍스트 처리**: 긴 문서 자동 청킹, 문장 분할, 키워드 추출
- **구조화된 요약**: 주제별 분류, 핵심 개념 추출, 통계 정보 제공
- **재현성**: 시드 기반 랜덤 생성으로 일관된 결과
- **다국어 지원**: 한국어/영어 혼합 텍스트 처리

## 📦 설치

```bash
# 저장소 클론
git clone <repository-url>
cd lecture-quiz-bot-local

# 의존성 설치
pip install -r requirements.txt
```

## 🎯 사용법

### 기본 사용법

```bash
# 기본 실행 (혼합 타입 요약)
python summary_gen.py --notes notes --out summaries

# 키워드 중심 요약
python summary_gen.py --notes notes --out summaries --type keywords

# 문장 중심 요약
python summary_gen.py --notes notes --out summaries --type sentences

# 한국어 텍스트, 상세 로그
python summary_gen.py --notes notes --out summaries --lang ko --verbose

# 특정 확장자만 처리
python summary_gen.py --notes notes --out summaries --ext ".md" --verbose
```

### Makefile 사용법

```bash
# 기본 실행
make run

# 다양한 요약 타입
make run-mixed      # 혼합 요약 (문장 + 키워드)
make run-keywords   # 키워드 중심 요약
make run-sentences  # 문장 중심 요약

# 테스트 및 정리
make test           # 요약 생성 테스트
make clean          # 생성된 파일 정리
```

### 고급 옵션

```bash
# 시드 고정으로 재현 가능한 결과
python summary_gen.py --notes notes --out summaries --seed 42

# 더 많은 키워드 추출
python summary_gen.py --notes notes --out summaries --max-keywords 100

# 청크 크기 조정 (긴 문서용)
python summary_gen.py --notes notes --out summaries --chunk-size 10000

# 요약 문장 수 조정
python summary_gen.py --notes notes --out summaries --summary-sentences 10
```

## 📁 프로젝트 구조

```
lecture-quiz-bot-local/
├── summary_gen.py              # 메인 CLI 인터페이스
├── summary_rules.py            # 핵심 규칙 기반 로직
├── summary_io_utils.py         # 요약 마크다운 작성
├── requirements.txt            # 의존성 목록
├── Makefile                   # 편의 명령어
├── notes/                     # 입력 노트 파일들
│   ├── sample.md
│   └── algorithm_basics.txt
└── summaries/                 # 생성된 요약 파일들
    ├── sample_summary.md
    └── algorithm_basics_summary.md
```

## 🔧 명령행 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--notes` | 노트 디렉토리 경로 | (필수) |
| `--out` | 출력 디렉토리 경로 | (필수) |
| `--type` | 요약 타입 (keywords/sentences/mixed) | mixed |
| `--ext` | 처리할 파일 확장자 | .txt,.md |
| `--lang` | 언어 설정 (ko/en) | ko |
| `--seed` | 랜덤 시드 | 42 |
| `--verbose` | 상세 로그 출력 | False |
| `--max-keywords` | 최대 키워드 수 | 50 |
| `--chunk-size` | 텍스트 청킹 크기 | 8000 |
| `--summary-sentences` | 요약 문장 수 | 5 |

## 📝 요약 타입

### 1. 키워드 요약 (keywords)
```
## 키워드 요약

**핵심 키워드**: 인공지능, 머신러닝, 딥러닝, 알고리즘, 데이터

**주요 키워드**: 학습, 패턴, 예측, 분류, 신경망, 자연어처리, 컴퓨터비전

## 핵심 개념
1. **인공지능**
2. **머신러닝**
3. **딥러닝**
4. **알고리즘**
5. **데이터**
```

### 2. 문장 요약 (sentences)
```
## 문장 요약

인공지능(Artificial Intelligence, AI)은 인간의 지능을 모방하여 학습, 추론, 문제해결 등의 능력을 가진 시스템을 개발하는 컴퓨터 과학의 한 분야입니다. 머신러닝(Machine Learning, ML)은 인공지능의 핵심 기술로, 명시적으로 프로그래밍하지 않고도 데이터로부터 패턴을 학습하여 예측이나 분류를 수행하는 알고리즘입니다. 딥러닝(Deep Learning)은 인공신경망을 기반으로 한 머신러닝의 한 분야입니다.
```

### 3. 혼합 요약 (mixed)
```
## 핵심 내용 요약
[핵심 문장들로 구성된 요약]

## 키워드 요약
[핵심 키워드와 주요 키워드]

## 주제별 키워드
**개념/정의**: 인공지능, 머신러닝, 딥러닝
**기술/방법**: 알고리즘, 신경망, 학습
**응용/사용**: 자연어처리, 컴퓨터비전, 예측

## 요약 통계
- **원문 문장 수**: 45개
- **원문 단어 수**: 440개
- **압축률**: 29.3%
```

## 🧪 테스트

```bash
# 요약 생성 테스트 실행
make test

# 또는 직접 실행
python summary_gen.py --notes notes --out test_summaries --type mixed --ext ".md" --verbose
```

## 📊 요약 품질 지표

생성된 요약의 품질을 다음과 같은 지표로 평가합니다:

- **압축률**: 원문 대비 요약 길이 비율
- **키워드 다양성**: 추출된 키워드의 분포
- **문장 중요도**: TF-IDF 기반 문장 점수
- **주제 분류**: 키워드의 주제별 그룹화

## ⚠️ 한계사항

- **규칙 기반**: 의미적 이해보다는 통계적 패턴에 의존
- **언어 제한**: 한국어/영어 혼합 텍스트에 최적화
- **컨텍스트**: 문맥적 이해보다는 키워드 중심
- **복잡성**: 복잡한 추론이나 요약에는 한계

## 🔮 확장 아이디어

- **더 많은 언어 지원**: 일본어, 중국어 등
- **요약 스타일 확장**: 불릿 포인트, 계층적 구조 등
- **요약 길이 조절**: 사용자 정의 요약 길이 설정
- **템플릿 시스템**: 커스터마이징 가능한 요약 템플릿
- **통계 대시보드**: 생성된 요약 분석 및 시각화

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License

## 📞 문의

프로젝트에 대한 문의사항이나 버그 리포트는 Issues를 통해 제출해주세요.

---

**Made with ❤️ for education**