# 마중 (Majung) — 어르신 복지 도우미 AI 에이전트

> 인공지능 AI Agent 과제

디지털 취약계층 어르신이 자신에게 맞는 노인복지 혜택을 음성·이미지·텍스트로 쉽게 찾도록 돕는 멀티모달 AI 에이전트입니다.

- **두뇌 모델**: `qwen3:14b` (대화·추론·도구 호출)
- **비전 모델**: `gemma3:12b` (서류/이미지 OCR — Phase 3)
- **데이터**: data.go.kr 공공데이터 4종
- **런타임**: 로컬 Ollama (`http://localhost:11434`)

## 사전 준비

```bash
# 1) Ollama 모델 받기
ollama pull qwen3:14b
ollama pull gemma3:12b

# 2) 파이썬 의존성
pip install -r requirements.txt

# 3) 환경변수
copy .env.example .env   # Windows
# .env 의 DATA_GO_KR_KEY 에 발급키 입력
#   USE_MOCK=true  → 가짜 데이터(mock)로 동작 (키 없이도 전 기능 흐름 확인)
#   USE_MOCK=false → 실제 데이터: data/ 의 csv·xlsx 파일 + data.go.kr 오픈API
```

## 실행

```bash
python main.py
```

예) `파주 사는데 돌봄 서비스 있어요?` 라고 입력하면, 에이전트가
`search_welfare_services` 도구를 호출해 쉬운 말로 안내합니다.

**서류 사진 해석**: 이미지 파일 경로를 그대로 입력하면(예: `data/sample/안내문_샘플.png`),
`gemma3:12b`가 핵심 정보를 읽어 쉬운 말로 설명합니다. 샘플 안내문은
`python tests/make_sample_doc.py`로 생성할 수 있습니다.

**음성 대화**: `녹음` 이라고 입력하면 5초 동안 마이크로 듣고(STT, faster-whisper),
답변을 한국어 음성으로 들려줍니다(TTS, edge-tts).
- STT는 CPU로 동작(AMD GPU 가속 불가), 첫 실행 시 `small` 모델(약 0.5GB)을 내려받습니다.
- TTS(edge-tts)는 **인터넷 연결이 필요**합니다.
- 음성 라운드트립 점검: `python tests/test_voice.py`

## 진행 현황 (Phase)

- [x] **Phase 1** — 골격 + `search_welfare_services` (mock) + 에이전트 루프
- [x] **Phase 2** — 도구 3종(welfare/facility/jobs, mock) + 대화 히스토리 + 질문별 도구 라우팅
- [x] **Phase 3** — 서류 인식(비전, gemma3:12b): 사진 경로 입력 → 핵심 추출 → 쉬운 설명
- [x] **Phase 4** — 실제 데이터 연결: ③csv·②xlsx 파일 + ①data.go.kr 오픈API (`USE_MOCK=false`)
- [x] **Phase 5** — 음성: STT(faster-whisper small) + TTS(edge-tts 한국어) 한 바퀴

## 구조

```
majung/
├── config.py          # 모델명·상수·키 로딩
├── main.py            # CLI 대화 루프
├── agent/             # core.py(에이전트 루프), prompts.py
├── tools/             # welfare.py, registry.py (Phase 2: facility/jobs 추가)
└── data/mock/         # Phase 1~2 가짜 응답 JSON
```
