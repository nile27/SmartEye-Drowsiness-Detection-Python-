# SmartEye MVP Agent Handoff Document (인수인계서)

이 문서는 데스크톱 환경의 Antigravity 에이전트(혹은 타 개발자)가 본 프로젝트를 이관받아 즉시 빌드, 구동, 테스트 및 디버깅할 수 있도록 작성된 기술 인수인계 가이드라인입니다.

---

## 1. 프로젝트 요약 (Project Overview)
*   **이름**: SmartEye (실시간 졸음 및 집중력 저하 감지 MVP 시스템)
*   **기술 스택**: Python 3.10+, OpenCV, MediaPipe, NumPy
*   **구조**: 계층형 모듈러 아키텍처 (Layered Modular Architecture) - 관심사 분리에 중점을 둔 아키텍처로 독립적인 유닛 테스트 작성이 용이합니다.
*   **호환성**: macOS (Apple Silicon 포함) 및 Windows 크로스 플랫폼 지원 (winsound 내장 모듈 사용으로 윈도우 무설치 오디오 경보 작동)

---

## 2. 퀵 스타트 가이드 (Quick Start Guide)

프로젝트 복제(Clone) 후 실행 환경을 세팅하기 위한 명령어 패스입니다.

### 윈도우 (Windows) 환경 구동
```cmd
# 1. 프로젝트 루트 폴더 진입
cd py_ai_project

# 2. 가상환경 생성
python -m venv .venv

# 3. 가상환경 활성화 (CMD / PowerShell 중 택 1)
.venv\Scripts\activate.bat       :: CMD의 경우
.venv\Scripts\Activate.ps1       :: PowerShell의 경우

# 4. 의존성 설치 및 구동
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

### macOS 환경 구동
```bash
# 1. 프로젝트 루트 폴더 진입
cd py_ai_project

# 2. 가상환경 생성
python3 -m venv .venv

# 3. 가상환경 활성화
source .venv/bin/activate

# 4. 의존성 설치 및 구동
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

---

## 3. 핵심 아키텍처 및 소스 파일 맵
모듈식 설계 구조에 따라 컴포넌트별로 소스가 분할되어 있습니다.

*   `main.py`: 프로그램 진입점이자 비디오 루프 오케스트레이터.
*   `config.py`: 카메라 설정, 캘리브레이션 지속 시간, 민감도 임계치 비율 등을 포함한 환경 설정.
*   `src/camera.py` (`CameraManager`): OpenCV 카메라 장치 캡처 라이프사이클 관리.
*   `src/detector.py` (`FaceDetector`): MediaPipe Face Mesh를 이용해 얼굴 및 양안 랜드마크 추출.
*   `src/analyzer.py` (`EyeAnalyzer`): Euclidean Distance 및 EAR(Eye Aspect Ratio) 연산식 적용.
*   `src/classifier.py` (`DrowsinessClassifier`): 누적 EAR 이동 평균 스무딩 및 졸음 감지(Awake/Drowsy/Sleeping) 상태 머신 관리.
*   `src/alert.py` (`AlertManager`): 경고 수준 조율 및 시청각 플래그 전송.
*   `src/renderer.py` (`OverlayRenderer`): 얼굴 랜드마크 가시화 및 HUD 그래픽 디스플레이 overlay 연산.
*   `src/utils/audio_player.py` (`AudioPlayer`): 비전 처리 병목 방지를 위해 비동기 백그라운드 스레드로 macOS `afplay` 또는 윈도우 `winsound` 구동.
*   `src/utils/logger.py` (`SessionLogger`): 상태 전이 CSV 로그 저장소 관리.

---

## 4. 유닛 테스트 및 검증
수학적 EAR 산출 공식과 상태 전환 임계 타이머가 문제없이 연동되는지 검증하기 위한 테스트 패스입니다.

*   **테스트 실행 명령어 (가상환경 활성화 상태)**:
    ```bash
    python -m unittest discover -s tests
    ```
*   **테스트 커버리지**:
    *   `tests/test_analyzer.py`: 유클리드 거리 검증, 6개 좌표 기반 EAR 공식 테스트, division-by-zero 예외 처리 검증.
    *   `tests/test_classifier.py`: 이동 평균 윈도우 연산, 캘리브레이션 처리, mock 시간 기반 상태 전이 타임아웃 검증.

---

## 5. 튜닝 및 민감도 세부 조율 가이드 (중요 💡)
동작 민감도를 변경하려면 `config.py` 파일의 아래 변수들을 수정해야 합니다.

1.  **눈 감음 감지 민감도 변경**: `config.py` -> `CALIBRATION_THRESHOLD_RATIO` (기본값: `0.89`)
    *   수치가 `1.0`에 가까워질수록 눈이 조금만 작아져도 감지가 발동하여 극도로 예민해집니다.
    *   오작동을 줄이고 확실하게 눈을 질끈 감았을 때만 울리도록 하려면 `0.78` ~ `0.82` 사이로 낮춥니다.
2.  **최소 민감도 하한선 변경**: `config.py` -> `MIN_EAR_THRESHOLD` (기본값: `0.18`)
    *   캘리브레이션 단계에서 눈 깜빡임 등으로 기준 눈 크기(Base EAR)가 과하게 작게 계산되어 감지가 작동하지 않는 현상을 원천 방지하기 위해 클램프(하한선)로 작용합니다.

---

## 6. 주의 사항 및 알려진 이슈
*   **MediaPipe Solutions API 에러 방지**: 최신 `mediapipe` 버전은 `solutions` API가 누락되는 이슈가 있어 `requirements.txt`에 **`mediapipe==0.10.14`**로 버전을 명시해 강제 고정해 두었습니다. 다른 환경에 연동할 때도 반드시 이 지정된 버전을 사용해야 합니다.
*   **한영 입력기 종료 오류 방지**: OpenCV 윈도우 루프 내에 macOS와 윈도우의 가상 키보드 입력을 복합 대응하도록 구현하여 `q` / `Q` / `ㅂ` / `ㅃ` 모두 종료로 작동합니다.
