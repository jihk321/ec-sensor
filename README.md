# EC-Sensor

Taidacent RS485 Soil NPK pH 센서를 위한 Python 라이브러리

## 개요

이 라이브러리는 Taidacent RS485 Soil NPK pH 센서를 사용하여 토양의 질소(N), 인(P), 칼륨(K), pH, 전도도(EC)를 측정하는 기능을 제공합니다. RS-485 통신을 통해 센서와 통신하며, Windows와 라즈베리파이를 포함한 다양한 플랫폼에서 작동합니다.

## 특징

- RS-485 통신을 통한 센서 데이터 읽기
- 질소(N), 인(P), 칼륨(K) 함량 측정
- pH 측정
- 전도도(EC) 측정
- 자동 포트 감지
- 윈도우 및 라즈베리파이 환경 지원
- 명령줄 인터페이스 제공

## 설치

### 요구 사항

- Python 3.6 이상
- pyserial 라이브러리

### 설치 방법

```bash
# 저장소 클론
git clone https://github.com/jihk321/ec-sensor.git
cd ec-sensor

# 필요한 라이브러리 설치
pip install pyserial
```

## 사용 방법

### 센서 연결

1. RS-485 to USB 컨버터를 컴퓨터에 연결합니다.
2. Taidacent RS485 Soil NPK pH 센서를 RS-485 컨버터에 연결합니다:
   - 센서의 노란색 선(485-A)을 컨버터의 A 단자에 연결
   - 센서의 파란색 선(485-B)을 컨버터의 B 단자에 연결
   - 센서의 갈색 선(VCC)을 전원 공급 장치의 양극(+)에 연결
   - 센서의 검은색 선(GND)을 전원 공급 장치의 음극(-)에 연결
3. 전원 공급 장치를 5-30V DC로 설정합니다.

### 명령줄 인터페이스 사용

```bash
# 모든 센서 데이터 읽기 (기본 모드)
python main.py

# 특정 포트 지정
python main.py -p COM3  # Windows
python main.py -p /dev/ttyUSB0  # Linux/라즈베리파이

# NPK 데이터만 읽기
python main.py -m npk

# EC 및 pH 데이터만 읽기
python main.py -m ec_ph

# 특정 값만 읽기 (n, p, k, ec, ph 중 선택)
python main.py -m n  # 질소만 읽기
python main.py -m ph  # pH만 읽기

# 측정 간격 및 횟수 설정
python main.py -i 10 -c 5  # 10초 간격으로 5회 측정
```

### 프로그래밍 API 사용

```python
from sensor import TaidacentSoilSensor

# 센서 초기화 (포트 자동 감지)
sensor = TaidacentSoilSensor()

# 또는 포트 직접 지정
# sensor = TaidacentSoilSensor(port='COM3', baudrate=9600)

# 연결 확인
if sensor.is_connected():
    # 모든 데이터 읽기
    data = sensor.read_all()
    print(f"질소: {data.get('nitrogen')} mg/kg")
    print(f"인: {data.get('phosphorus')} mg/kg")
    print(f"칼륨: {data.get('potassium')} mg/kg")
    print(f"전도도: {data.get('ec')} μS/cm")
    print(f"pH: {data.get('ph')}")

    # 개별 데이터 읽기
    nitrogen = sensor.read_nitrogen()
    phosphorus = sensor.read_phosphorus()
    potassium = sensor.read_potassium()
    ec = sensor.read_ec()
    ph = sensor.read_ph()

    # 센서 연결 종료
    sensor.close()
else:
    print("센서에 연결할 수 없습니다.")
```

## 센서 사양

### Taidacent RS485 Soil NPK pH 센서

- **전원 공급**: DC 5-30V
- **통신 방식**: RS-485 (Modbus-RTU)
- **측정 항목**:
  - 질소(N): 0-2999 mg/kg
  - 인(P): 0-2999 mg/kg
  - 칼륨(K): 0-2999 mg/kg
  - pH: 3-9 pH
  - 전도도(EC): 0-20000 μS/cm
- **정확도**:
  - NPK: ≤5% (실제 측정 장비에 따라 다름)
  - EC: 0-10000 μS/cm@±3%FS, 10000-20000 μS/cm@±5%FS
- **보호 등급**: IP68
- **작동 온도**: -40°C~+60°C
- **프로브 재질**: 내부식성 특수 전극 (316 스테인리스 스틸)
- **밀봉 재질**: 흑색 난연성 에폭시 수지

## 문제 해결

1. **센서가 감지되지 않는 경우**:
   - RS-485 컨버터가 올바르게 연결되어 있는지 확인
   - A와 B 선이 올바르게 연결되어 있는지 확인
   - 센서에 전원이 공급되고 있는지 확인
   - 다른 USB 포트 시도

2. **데이터 읽기 오류**:
   - 통신 속도(baudrate) 확인 (기본값: 9600)
   - 센서 주소 확인 (기본값: 0x01)
   - 케이블 길이가 너무 길면 신호 감쇠 가능성 있음

3. **이상한 측정값**:
   - 센서가 토양에 완전히 삽입되었는지 확인
   - 센서 프로브가 손상되지 않았는지 확인
   - 토양이 너무 건조하거나 젖지 않았는지 확인

## 라이선스

MIT 라이선스

## 기여

버그 리포트, 기능 요청, 풀 리퀘스트는 언제나 환영합니다!
