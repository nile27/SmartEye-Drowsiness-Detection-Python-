# SmartEye: Real-Time Drowsiness & Focus Detection System

실시간 웹캠 분석을 바탕으로 사용자의 얼굴 및 눈 상태를 실시간 분석하여 졸음 및 집중력 저하 상태를 감지하고 경고를 알리는 Python 기반 컴퓨터 비전 어플리케이션입니다.

## 기술 스택 요약

| 구성 요소 | 기술 스택 | 주요 역할 |
| :--- | :--- | :--- |
| **언어** | Python 3.10+ | 시스템 핵심 로직 구동 및 런타임 제어 |
| **컴퓨터 비전** | OpenCV | 비디오 프레임 캡처, 가로 반전, 이미지 프로세싱, HUD 및 GUI 렌더링 |
| **얼굴 랜드마크 감지** | MediaPipe (Face Mesh) | CPU 기반 468개(또는 478개) 3D 얼굴 랜드마크 실시간 정밀 감지 및 추적 |
| **수치 해석 및 기하 연산** | NumPy | 유클리드 거리 산출 및 다차원 배열 연산 |
| **품질 보증 및 테스트** | Unittest | EAR 공식 계산 및 유한 상태 기계(FSM) 전이 로직 무결성 검증 |


# 🎯 프로젝트 개요

## 무엇을 만들었나?

실시간 웹캠 영상으로 사용자의 **눈 상태를 분석**하여  
졸음 및 집중력 저하 상태를 감지하고 **즉시 경고**하는 시스템


# 🔬 핵심 기술: EAR 알고리즘

## Eye Aspect Ratio (눈 종횡비)

**EAR(Eye Aspect Ratio, 눈 종횡비)**은 눈 주변에 지정된 6개의 랜드마크 포인트(P1~P6) 간의 거리를 활용하여 **눈의 가로 길이 대비 세로 길이의 비율**을 정량적으로 산출하는 수학적 공식입니다.

*   **눈을 떴을 때**: 세로 거리($P2-P6$, $P3-P5$)가 충분히 멀어지므로 EAR 비율 값이 **증가**합니다.
*   **눈을 감았을 때**: 세로 거리가 거의 0에 가까워지므로 EAR 비율 값이 **0에 수렴**합니다.
*   **핵심 장점**: 얼굴의 실제 크기나 카메라와의 거리에 상관없이 **눈이 열린 비율만 추적**하기 때문에 일관성 있는 졸음 판단이 가능합니다.

```
        P2      P3
         \      /
    P1 ---+----+--- P4
         /      \
        P6      P5
```

$$EAR = \frac{||P2-P6|| + ||P3-P5||}{2 \times ||P1-P4||}$$


## EAR 알고리즘 원리

| 상태 | EAR 값 | 설명 |
|------|--------|------|
| 👁️ 눈 뜸 (Awake) | **0.25 ~ 0.35** | 세로 거리가 충분히 큼 |
| 😪 졸음 (Drowsy) | **0.18 ~ 0.22** | 세로 거리가 줄어듦 |
| 😴 수면 (Sleeping) | **< 0.18** | 눈이 거의 닫힘 |


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


# 📦 객체지향 설계와 모듈별 역할

## 단일 책임 원칙(SRP) 기반의 모듈 세분화

컴퓨터 공학적 설계 원칙인 **단일 책임 원칙 (Single Responsibility Principle)**을 적용하여, 각 모듈이 단 하나의 책임과 역할만 수행하도록 결합도를 낮추고 응집도를 높였습니다.


## 1. 데이터 입력 및 전처리 계층 (Input Layer)

### 📹 `camera.py` : `CameraManager`
*   **설계 방식**: 하드웨어 장치 제어 및 자원 라이프사이클 캡슐화.
*   **주요 기능**: 
    - OpenCV `VideoCapture` 리소스 제어 및 스레드 지연 없는 카메라 버퍼 조회.
    - 예외 상황(장치 미연결 등) 발생 시 안전한 예외 복구 및 애플리케이션 그레이스풀 종료 제어.

### 🗺️ `detector.py` : `FaceDetector`
*   **설계 방식**: 비전 AI 파이프라인의 추상화 인터페이스 구현.
*   **주요 기능**:
    - MediaPipe Face Mesh 모델을 사용해 468차원 얼굴 공간 매핑.
    - 정규화된 3D 이미지 랜드마크 좌표 중 눈 주변 인덱스만 필터링하여 프레임 비율에 맞는 2D 픽셀 좌표계로 역산 변환.


## 2. 수치 분석 및 상태 기계 계층 (Domain Logic Layer)

### 📐 `analyzer.py` : `EyeAnalyzer`
*   **설계 방식**: 수학 연산 로직의 순수 함수(Pure Function) 분리.
*   **주요 기능**:
    - 기하학적 2차원 공간 상의 Euclidean Distance 알고리즘 수행.
    - EAR(Eye Aspect Ratio) 수학적 계산 및 수치 불안정성 차단(분모가 0이 되는 Zero Division 예외 방지).

### 🧠 `classifier.py` : `DrowsinessClassifier`
*   **설계 방식**: 시계열 스무딩 및 유한 상태 기계 (Finite State Machine, FSM) 상태 전이 관리.
*   **주요 기능**:
    - `collections.deque` 자료구조를 이용한 이동 평균(Moving Average) 알고리즘으로 High-frequency 노이즈 제거.
    - 5초간 사용자 기본 눈 EAR을 측정해 동적으로 기준값을 잡는 개인화 자동 보정(Calibration).
    - 시간 누적 평가를 바탕으로 한 `Awake` ↔ `Drowsy` ↔ `Sleeping` FSM 상태 상태 천이 핸들링.


## 3. 출력 및 피드백 계층 (Output Layer)

### 🔔 `alert.py` : `AlertManager`
*   **설계 방식**: 중개자 패턴(Mediator Pattern)을 차용한 출력 동기화 코디네이션.
*   **주요 기능**:
    - 상태 전환 이벤트를 인터셉트하여 시각 플래시 경보와 오디오 엔진 간 동작 수준 조율.
    - 중복 경보 시작 요청을 필터링해 시스템 오버헤드 최적화.

### 🖥️ `renderer.py` : `OverlayRenderer`
*   **설계 방식**: 뷰(View)의 템플릿화 및 HUD 드로잉 최적화.
*   **주요 기능**:
    - 반투명 HUD 탑바, 눈가 윤곽선 다각형 그리기(Polylines), 수치 그래픽 바 오버레이.
    - 졸음 경고 주황색 프레임 테두리 및 4Hz 점멸 붉은색 풀스크린 경고 박스 출력.


## 4. 백그라운드 인프라 계층 (Utility/Infrastructure Layer)

### 🔊 `utils/audio_player.py` : `AudioPlayer`
*   **설계 방식**: 멀티스레딩(Multithreading) 및 크로스 플랫폼 비동기 I/O 설계.
*   **주요 기능**:
    - 비차단식(Non-blocking) 경고음 작동을 위해 백그라운드 스레드 생성 후 독립 구동.
    - 런타임에 운영체제 플랫폼(Win/Mac/Linux)을 감지하여 알맞은 오디오 드라이버 API 선택적 연동.

### 📄 `utils/logger.py` : `SessionLogger`
*   **설계 방식**: 데이터 영속화(Data Persistence) 및 파일 I/O 스트리밍.
*   **주요 기능**:
    - 상태 전이 순간을 이벤트 기반(Event-driven)으로 포착해 발생 시각, 천이 지속 시간, 통계 EAR 수치를 CSV 포맷으로 디스크 파일에 영구 기록.


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


## 이동 평균 스무딩 (Moving Average Smoothing)

```
원본 EAR: [0.28, 0.15, 0.27, 0.26, 0.14]  ← 순간 노이즈 포함
                    ↓ window=5 이동 평균
스무딩 EAR: [0.22, 0.22, 0.22, 0.22, 0.22]  ← 안정화된 값

→ 눈 깜빡임(순간 저하)을 졸음으로 오탐하지 않음
```


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


## 테스트 실행
```bash
python -m unittest discover -s tests
# 결과: OK (모든 테스트 통과)
```


# 🚀 시작하기

## 설치 및 실행 (4단계)

### Step 1. 저장소 복제 및 이동
```bash
git clone <Repository-URL>
cd SmartEye-Drowsiness-Detection-Python-
```

### Step 2. 가상환경 생성 및 활성화
* **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
  *(참고: 권한 에러 발생 시 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` 실행)*
* **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3. 의존성 패키지 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4. 프로그램 실행
```bash
python main.py
```

## ⌨️ 키보드 조작 및 사용법
| 기능 | 입력 키 | 동작 설명 |
|------|:-------:|-----------|
| **자동 보정 (Calibration)** | 시작 후 5초 | 정면을 편안하게 응시하여 개인 기본 EAR 설정 |
| **수동 재보정** | `c` | 카메라 각도/조명 변화 시 임계치 실시간 재보정 |
| **프로그램 종료** | `q` | 카메라 및 비동기 오디오 스레드 안전하게 해제 후 종료 |


# 💡 개발 비하인드 (요약)

*   **초기 시도**: 눈 이미지 데이터셋을 직접 모아 캐글(Kaggle)에서 딥러닝 학습 시도.
*   **실패 원인**: 수집된 **데이터셋의 절대적 부족**으로 딥러닝 모델 판별 정확도 저하.
*   **해결 방안**: 얼굴 점들을 알려주는 MediaPipe를 기반으로, 가로세로 비율(EAR) 계산 수식으로 선회.
*   **최종 결과**: 별도 데이터 학습 없이 일반 웹캠 환경에서 정확히 작동하는 실시간 졸음 감지 구현.


# 🙏 감사합니다

## Q & A

> **SmartEye** — Real-Time Drowsiness & Focus Detection System  
> GitHub: `SmartEye-Drowsiness-Detection-Python-`


*발표자료 작성: SmartEye Project Team*  
*작성일: 2026년 5월*
