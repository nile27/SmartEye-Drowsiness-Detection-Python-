# SmartEye: Real-Time Drowsiness & Focus Detection System

실시간 웹캠 분석을 바탕으로 사용자의 얼굴 및 눈 상태를 실시간 분석하여 졸음 및 집중력 저하 상태를 감지하고 경고를 알리는 Python 기반 컴퓨터 비전 어플리케이션입니다.

본 프로젝트는 소프트웨어 공학적 완성도를 위해 **계층형 모듈러 아키텍처(Layered Modular Architecture)**를 채택하여 설계되었으며, 높은 동작 안정성과 손쉬운 확장성을 가집니다.

---

## 1. 주요 기능
- **실시간 눈 랜드마크 트래킹**: MediaPipe Face Mesh 솔루션을 사용하여 얼굴 및 눈 주변부의 468개(또는 478개) 랜드마크 포인트를 실시간으로 정교하게 추적합니다.
- **EAR(Eye Aspect Ratio) 정량적 측정**: 눈 주변 6개 좌표 간의 유클리드 거리를 바탕으로 실시간 눈 상태 비율을 완벽히 수치화합니다. (가로 길이 대비 세로 두 차례의 비율 연산)
- **개인화 임계값 자동 보정 (Calibration)**: 시작 시 5초 동안 사용자의 기본 안구 구조 및 카메라 거리 등을 분석하여 개인용 EAR 경계 기준선(Threshold)을 실시간 자동 튜닝합니다.
- **단계별 실시간 피로 분류 및 경보**:
  - `Awake`: 정상 눈 뜸 상태
  - `Drowsy`: 졸음 진입 의심 상태 (1초 연속 EAR 저하 시, 노란색 화면 가이드 및 알림음)
  - `Sleeping`: 매우 위험한 취침 상태 (3초 연속 EAR 저하 시, 화면이 적색으로 깜빡이며 긴급 사이렌 재생)
- **비차단식 비동기 오디오 경고**: 오디오 버퍼 재생이 비전 메인 루프를 방해하지 않도록 백그라운드 스레드에서 경고 알림음이 작동하여 FPS 프레임 드랍을 원천 차단합니다.
- **주요 로그 저장**: 세션 구동 도중 발생한 모든 상태 전환(`Awake` -> `Drowsy` 등)과 해당 지속 시간, 이전 상태에서의 평균 EAR 수치를 CSV 포맷 파일(`logs/session_*.csv`)로 자동 영구 보관합니다.

---

## 2. 기술 스택
- **언어**: Python 3.10+
- **라이브러리**:
  - `OpenCV` (비디오 프레임 처리, 이미지 프로세싱 및 UI 렌더링)
  - `MediaPipe` (고성능 실시간 Face Mesh / Landmark 검출)
  - `NumPy` (안구 거리 계산 등 수치 해석 연산)
  - `Unittest` (핵심 연산 모듈 및 상태 상태 전이 로직 검증)

---

## 3. 디렉토리 구조 및 시스템 아키텍처
```
py_ai_project/
├── .gitignore                  # Git 추적 제외 설정
├── README.md                   # 프로젝트 전체 소개 및 가이드 문서
├── requirements.txt            # 프로젝트 설치 라이브러리 목록
├── main.py                     # 프로그램 진입점 (오케스트레이터)
├── config.py                   # EAR 임계값, 카메라 해상도 등 설정 변수 모음
├── Plan/
│   ├── implementation_plan.md  # SmartEye 상세 개발 및 설계 계획서
│   └── task.md                 # 진행 상황을 트래킹하는 태스크 목록
├── src/
│   ├── __init__.py
│   ├── camera.py               # CameraManager: 프레임 캡처 라이프사이클 관리
│   ├── detector.py             # FaceDetector: MediaPipe 얼굴 랜드마크 추출
│   ├── analyzer.py             # EyeAnalyzer: EAR 공식 연산
│   ├── classifier.py           # DrowsinessClassifier: 시계열 스무딩 및 상태 감지
│   ├── alert.py                # AlertManager: 시청각 경보 수준 상태 동기화
│   ├── renderer.py             # OverlayRenderer: 랜드마크 가시화 및 HUD 렌더링
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # SessionLogger: 상태 전이 기록 CSV 파일 출력
│       └── audio_player.py     # AudioPlayer: 백그라운드 비차단 경고음 재생
└── tests/
    ├── __init__.py
    ├── test_analyzer.py        # EAR 수학 공식 검증 단위 테스트
    └── test_classifier.py      # 상태 전환 조건 검증 단위 테스트
```

### 데이터 파이프라인
```
[ Camera Frame ] (RGB Image)
       │ (src/camera.py)
[ Preprocessing ] (Resize & Format Conversion)
       │ (src/detector.py)
[ Face Mesh Detection ] (Output: Landmarks)
       │ (src/detector.py)
[ Eye Landmarks Extraction ] (Output: Eye coordinates)
       │ (src/analyzer.py)
[ EAR Calculation ] (Output: Average EAR: float)
       │ (src/classifier.py)
[ Drowsiness Classification ] (Output: Awake | Drowsy | Sleeping)
       │ (src/alert.py)
[ Alert Decision ] (Output: Async Sound Trigger)
       │ (src/renderer.py)
[ Overlay Rendering ] (Drawing contours & status bar)
       │ (main.py)
[ Screen Display ] & [ Logging ] (src/utils/logger.py)
```

---

## 4. 시작하기

### 4.1 의존성 설치
사용자 환경에 맞는 Python 3.10+ 가상환경을 생성하고 패키지를 설치합니다.

```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# pip 업그레이드 및 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.2 실행 및 사용 방법
```bash
python main.py
```
- **초기 캘리브레이션 (5초)**: 시작 직후 화면 상단에 `STATE: CALIBRATING` 메시지와 진행률(%)이 표시됩니다. 편안하게 정면을 약 5초 동안 응시해주시면 됩니다. 수집된 평소 눈 크기의 75% 수준이 사용자의 임계치로 자동 저장됩니다.
- **수동 재캘리브레이션 (`c` 키)**: 사용자가 카메라와 멀어지거나 밝기가 변해 임계값 재설정이 필요할 때, `c` 키를 누르면 즉시 5초간 재캘리브레이션 세션이 실행됩니다.
- **종료 (`q` 키)**: 구동 화면에서 `q` 키를 누르면 모든 카메라 리소스와 스레드가 깔끔히 자원 반환되며 프로그램이 정상 종료됩니다.

### 4.3 단위 테스트 수행
```bash
python -m unittest discover -s tests
```

---

## 5. 프로젝트 한계점 및 개선 방향
- **저조도 검출 제한**: 어두운 야간이나 조명이 약한 환경에서 웹캠의 노이즈와 밝기 저하로 MediaPipe 얼굴 감지율이 하락할 수 있습니다. 이는 추후 적외선(IR) 카메라 연계 지원 및 히스토그램 평활화 등 전처리 강화로 해결 가능합니다.
- **복합 생체 지표의 결합 (v5 로드맵)**: 안구 깜빡임 빈도(Blink rate)나 시선 이탈(Gaze detection) 등을 추가 확보하여 더욱 정교한 종합 주의력 집중 점수 산정 모델로 발전시킬 예정입니다.
