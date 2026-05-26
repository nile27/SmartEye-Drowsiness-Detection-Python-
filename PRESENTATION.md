# 👁️ SmartEye
## 실시간 졸음 & 집중력 저하 감지 시스템

> **Python 기반 컴퓨터 비전 어플리케이션**  
> MediaPipe · OpenCV · EAR 알고리즘


# 🎯 프로젝트 개요

## 무엇을 만들었나?

실시간 웹캠 영상으로 사용자의 **눈 상태를 분석**하여  
졸음 및 집중력 저하 상태를 감지하고 **즉시 경고**하는 시스템

---

## 왜 필요한가?

| 문제 | 현황 |
|------|------|
| 🚗 졸음운전 사고 | 전체 교통사고 사망의 약 **10~20%** 차지 |
| 💻 집중력 저하 | 장시간 업무/학습 중 인지 능력 급격히 감소 |
| ⚠️ 기존 해결책의 한계 | 고가 장비 / 착용형 센서 / 불편한 설치 필요 |

### ✅ SmartEye의 솔루션
> **일반 웹캠 하나로** 별도 장비 없이 실시간 감지 가능




# 🔬 핵심 기술: EAR 알고리즘

## Eye Aspect Ratio (눈 종횡비)

```
        P2      P3
         \      /
    P1 ---+----+--- P4
         /      \
        P6      P5
```

$$EAR = \frac{||P2-P6|| + ||P3-P5||}{2 \times ||P1-P4||}$$

---

## EAR 알고리즘 원리

| 상태 | EAR 값 | 설명 |
|------|--------|------|
| 👁️ 눈 뜸 (Awake) | **0.25 ~ 0.35** | 세로 거리가 충분히 큼 |
| 😪 졸음 (Drowsy) | **0.18 ~ 0.22** | 세로 거리가 줄어듦 |
| 😴 수면 (Sleeping) | **< 0.18** | 눈이 거의 닫힘 |

### 핵심 장점
- 👤 **얼굴 회전·조명에 강인** — 비율 기반이므로 절대 거리 영향 없음  
- ⚡ **초경량 연산** — 6개 좌표만으로 실시간 판단 가능  
- 📐 **수학적 명확성** — 유클리드 거리 기반의 단순한 공식




# 🧠 개인화 캘리브레이션

## 사람마다 다른 눈 구조를 자동 보정

```
시작 후 5초 동안 정면 응시
        ↓
사용자 기본 EAR 평균값 수집
        ↓
개인 임계값 = 평균 EAR × 0.89
        ↓
맞춤 졸음 감지 기준 자동 적용
```



## 캘리브레이션의 필요성

```
         눈이 큰 사람           눈이 작은 사람
         ┌──────────┐           ┌──────────┐
EAR      │   0.32   │           │   0.24   │
기본값    └──────────┘           └──────────┘
         
고정 임계값 0.22 적용 시:
  → 눈이 작은 사람은 정상 상태도 "졸음"으로 오탐!
  
✅ 개인 캘리브레이션으로 오탐률 최소화
```


# ⚙️ 시스템 아키텍처

## 계층형 모듈러 구조 (Layered Modular Architecture)

```
┌─────────────────────────────────────────────┐
│                   main.py                    │  ← 오케스트레이터
├──────────┬──────────┬────────────┬──────────┤
│ camera.py│detector.py│analyzer.py│classifier│  ← 처리 계층
├──────────┴──────────┴────────────┴──────────┤
│         alert.py  │  renderer.py             │  ← 출력 계층
├───────────────────┴─────────────────────────┤
│       utils/logger.py  │  utils/audio_player │  ← 유틸리티 계층
└─────────────────────────────────────────────┘
```

---

## 데이터 파이프라인

```
📷 Camera Frame (RGB Image)
        │
        ▼
🔄 Preprocessing  ── 리사이즈 & 포맷 변환
        │
        ▼
🗺️ Face Mesh Detection  ── 468개 랜드마크 추출
        │
        ▼
👁️ Eye Landmarks Extraction  ── 눈 6개 좌표 선별
        │
        ▼
📐 EAR Calculation  ── 유클리드 거리 → 비율 계산
        │
        ▼
🧠 Drowsiness Classification  ── Awake / Drowsy / Sleeping
        │
        ▼
🔔 Alert Decision  ── 비동기 경보음 트리거
        │
        ▼
🖥️ Overlay Rendering + 📄 CSV Logging
```


---

# 📦 모듈별 역할

## 핵심 모듈 6개

| 모듈 | 클래스 | 역할 |
|------|--------|------|
| `camera.py` | `CameraManager` | 웹캠 프레임 캡처 및 라이프사이클 관리 |
| `detector.py` | `FaceDetector` | MediaPipe로 468개 얼굴 랜드마크 추출 |
| `analyzer.py` | `EyeAnalyzer` | EAR 공식 연산 (유클리드 거리 기반) |
| `classifier.py` | `DrowsinessClassifier` | 시계열 스무딩 + 상태 전환 판정 |
| `alert.py` | `AlertManager` | 시청각 경보 수준 동기화 관리 |
| `renderer.py` | `OverlayRenderer` | 랜드마크 시각화 및 HUD 렌더링 |

---

## 유틸리티 모듈

| 모듈 | 역할 |
|------|------|
| `utils/logger.py` | 상태 전환 이력을 CSV 파일로 자동 저장 |
| `utils/audio_player.py` | **백그라운드 스레드**로 비차단 경고음 재생 |

---



# 🚦 3단계 졸음 감지 시스템

## 상태 전환 다이어그램

```
                  EAR 정상 회복
         ┌────────────────────────────┐
         ▼                            │
   ┌───────────┐    1초 연속          ┌───────────┐    3초 연속    ┌────────────┐
   │  😀 AWAKE │──  EAR 저하 ──────▶│ 😪 DROWSY │── EAR 저하 ──▶│ 😴 SLEEPING│
   └───────────┘                     └───────────┘                └────────────┘
   화면: 정상 (녹색)               화면: 황색 경고               화면: 적색 점멸
   알림: 없음                       알림: 경고음 1회              알림: 긴급 사이렌
```

---

## 단계별 반응 상세

### 😀 AWAKE (정상)
- EAR ≥ 개인 임계값
- 화면 테두리: **녹색**
- 알림 없음

### 😪 DROWSY (졸음 진입)
- EAR < 임계값 **1초 지속**
- 화면 테두리: **황색 (Yellow)**
- 경고음 1회 재생

### 😴 SLEEPING (위험)
- EAR < 임계값 **3초 지속**
- 화면: **적색 점멸 (Flashing Red)**
- 긴급 사이렌 반복 재생

---


# 🛠️ 기술 스택

## 사용 라이브러리

```
Python 3.10+
    │
    ├── OpenCV          ── 비디오 캡처, 이미지 처리, UI 렌더링
    │
    ├── MediaPipe       ── Face Mesh 실시간 랜드마크 감지
    │                      (468개 포인트, 30FPS 실시간 처리)
    │
    ├── NumPy           ── 유클리드 거리 계산, 배열 연산
    │
    └── Unittest        ── EAR 연산 및 상태 전환 단위 테스트
```

---

## MediaPipe Face Mesh 특징

| 특징 | 내용 |
|------|------|
| 🗺️ 랜드마크 수 | 468개 (정밀 모델: 478개) |
| ⚡ 속도 | **30FPS 이상** 실시간 처리 |
| 🖥️ 구동 환경 | CPU만으로 실시간 동작 (GPU 불필요) |
| 📐 출력 형식 | 정규화된 3D 좌표 (x, y, z) |

---

---

# 🔧 핵심 구현 상세

## 비차단식 비동기 오디오 (Non-Blocking Audio)

### 문제
```python
# ❌ 동기 재생: 경고음 재생 동안 프레임 처리가 멈춤
winsound.PlaySound("alert.wav", winsound.SND_FILENAME)
# → FPS 드랍 발생, 실시간성 훼손
```

### SmartEye의 해결책
```python
# ✅ 비동기 재생: 백그라운드 스레드에서 분리 실행
class AudioPlayer:
    def play_alert(self):
        thread = threading.Thread(target=self._play)
        thread.daemon = True
        thread.start()
# → 메인 루프 FPS 유지, 경고음도 정상 재생
```

---

## 이동 평균 스무딩 (Moving Average Smoothing)

```
원본 EAR: [0.28, 0.15, 0.27, 0.26, 0.14]  ← 순간 노이즈 포함
                    ↓ window=5 이동 평균
스무딩 EAR: [0.22, 0.22, 0.22, 0.22, 0.22]  ← 안정화된 값

→ 눈 깜빡임(순간 저하)을 졸음으로 오탐하지 않음
```

---

---

# 📊 세션 로깅 시스템

## 자동 CSV 기록

모든 상태 전환을 `logs/session_YYYYMMDD_HHMMSS.csv`로 자동 저장

```
timestamp,          from_state, to_state,  duration_sec, avg_ear
2025-05-26 10:00:01, AWAKE,     DROWSY,    0.0,          0.231
2025-05-26 10:00:05, DROWSY,    AWAKE,     4.2,          0.198
2025-05-26 10:00:23, AWAKE,     DROWSY,    18.0,         0.235
2025-05-26 10:00:28, DROWSY,    SLEEPING,  5.1,          0.172
```

### 활용 방안
- 📈 개인 졸음 패턴 분석
- ⏰ 집중 지속 시간 측정
- 📉 피로 누적 추이 모니터링

---

---

# ✅ 품질 보증: 단위 테스트

## 테스트 커버리지

### `test_analyzer.py` — EAR 수학 공식 검증
```python
def test_ear_open_eye(self):
    # 눈이 완전히 열린 상태의 EAR은 0 초과여야 함
    self.assertGreater(ear, 0)

def test_ear_closed_eye(self):
    # 눈이 완전히 닫힌 상태의 EAR은 거의 0이어야 함
    self.assertAlmostEqual(ear, 0.0, places=3)
```

### `test_classifier.py` — 상태 전환 조건 검증
```python
def test_drowsy_state_transition(self):
    # 1초 이상 EAR 저하 시 DROWSY 전환 확인

def test_sleeping_state_transition(self):
    # 3초 이상 EAR 저하 시 SLEEPING 전환 확인
```

---

## 테스트 실행
```bash
python -m unittest discover -s tests
# 결과: OK (모든 테스트 통과)
```



# 🚀 시작하기

## 설치 및 실행 (3단계)

### Step 1. 환경 설정
```bash
python3 -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### Step 2. 실행
```bash
python main.py
```

### Step 3. 사용법
| 키 | 동작 |
|----|------|
| 시작 5초 | 정면 응시 → 자동 캘리브레이션 |
| `c` | 수동 재캘리브레이션 (환경 변화 시) |
| `q` | 프로그램 종료 |

---

---

# ⚠️ 한계점 및 개선 방향

## 현재 한계

| 한계 | 원인 | 영향 |
|------|------|------|
| 저조도 환경 | 카메라 노이즈 증가 | 랜드마크 감지율 저하 |
| 극단적 측면 얼굴 | 랜드마크 일부 가림 | EAR 신뢰도 감소 |
| 안경 반사 | 렌즈 글레어 | 간헐적 오탐 가능 |

---

## v5 로드맵 (개선 방향)

```
현재 v1 (EAR 기반)
        │
        ▼
v2: 눈 깜빡임 빈도(Blink Rate) 추가
        │
        ▼
v3: 시선 이탈(Gaze Detection) 추가
        │
        ▼
v4: 적외선(IR) 카메라 지원 + 히스토그램 평활화
        │
        ▼
v5: 종합 주의력 집중 점수 (Attention Score) 모델
```

---

---

# 📌 프로젝트 요약

## SmartEye 핵심 가치

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   🔑 Key Innovation                                 │
│                                                     │
│   일반 웹캠 + EAR 알고리즘 + 개인화 캘리브레이션    │
│   = 고성능 졸음 감지                               │
│                                                     │
│   💡 Technical Highlights                           │
│                                                     │
│   ✅ 비차단 비동기 오디오 (FPS 손실 없음)          │
│   ✅ 이동 평균 스무딩 (오탐 최소화)                │
│   ✅ 개인화 캘리브레이션 (맞춤 임계값)             │
│   ✅ 계층형 모듈 아키텍처 (높은 확장성)            │
│   ✅ 자동 세션 로깅 (CSV 기록)                     │
│   ✅ 단위 테스트 (품질 보증)                       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 기술 스택 한눈에 보기

```
Python 3.10  +  OpenCV  +  MediaPipe  +  NumPy
     └────────────────────────────────────┘
              실시간 졸음 감지 엔진
```

---

# 🙏 감사합니다

## Q & A

> **SmartEye** — Real-Time Drowsiness & Focus Detection System  
> GitHub: `SmartEye-Drowsiness-Detection-Python-`

---

*발표자료 작성: SmartEye Project Team*  
*작성일: 2026년 5월*
