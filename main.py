"""
Taidacent RS485 Soil NPK pH 센서 메인 모듈

이 모듈은 Taidacent RS485 Soil NPK pH 센서를 사용하여 토양의 질소, 인, 칼륨, pH, 전도도를 측정하는
명령줄 인터페이스를 제공합니다.
"""

import sys
import time
import logging
import argparse
from typing import Optional, Dict, Any, Union

from sensor import TaidacentSoilSensor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argument_parser() -> argparse.ArgumentParser:
    """
    명령줄 인자 파서 설정

    Returns:
        argparse.ArgumentParser: 설정된 인자 파서
    """
    parser = argparse.ArgumentParser(
        description='Taidacent RS485 Soil NPK pH 센서 측정 도구'
    )

    parser.add_argument(
        '-p', '--port',
        help='RS-485 통신 포트 (예: COM1, /dev/ttyUSB0). 지정하지 않으면 자동 감지합니다.',
        type=str,
        default=None
    )

    parser.add_argument(
        '-b', '--baudrate',
        help='통신 속도 (기본값: 9600)',
        type=int,
        default=9600
    )

    parser.add_argument(
        '-i', '--interval',
        help='측정 간격 (초) (기본값: 5)',
        type=float,
        default=5
    )

    parser.add_argument(
        '-c', '--count',
        help='측정 횟수 (기본값: 1, 0은 무한 반복)',
        type=int,
        default=1
    )

    parser.add_argument(
        '-m', '--mode',
        help='측정 모드 (all: 모든 데이터, npk: NPK만, ec_ph: EC/pH만)',
        choices=['all', 'npk', 'ec_ph', 'n', 'p', 'k', 'ec', 'ph'],
        default='all'
    )

    return parser

def measure_and_display(sensor: TaidacentSoilSensor, mode: str) -> Dict[str, Any]:
    """
    센서 측정 및 결과 표시

    Args:
        sensor: Taidacent 토양 센서 객체
        mode: 측정 모드

    Returns:
        Dict[str, Any]: 측정 결과
    """
    result = {}

    try:
        if mode == 'all':
            result = sensor.read_all()
            print("\n===== Taidacent 토양 센서 측정 결과 =====")
            print(f"질소(N): {result.get('nitrogen', 'N/A')} mg/kg")
            print(f"인(P): {result.get('phosphorus', 'N/A')} mg/kg")
            print(f"칼륨(K): {result.get('potassium', 'N/A')} mg/kg")
            print(f"전도도(EC): {result.get('ec', 'N/A')} μS/cm")
            print(f"pH: {result.get('ph', 'N/A')}")
            print("=====================================")

        elif mode == 'npk':
            result = sensor.read_npk()
            print("\n===== NPK 측정 결과 =====")
            print(f"질소(N): {result.get('nitrogen', 'N/A')} mg/kg")
            print(f"인(P): {result.get('phosphorus', 'N/A')} mg/kg")
            print(f"칼륨(K): {result.get('potassium', 'N/A')} mg/kg")
            print("======================")

        elif mode == 'ec_ph':
            result = sensor.read_ec_ph()
            print("\n===== EC/pH 측정 결과 =====")
            print(f"전도도(EC): {result.get('ec', 'N/A')} μS/cm")
            print(f"pH: {result.get('ph', 'N/A')}")
            print("========================")

        elif mode == 'n':
            nitrogen = sensor.read_nitrogen()
            result = {'nitrogen': nitrogen}
            print(f"\n질소(N): {nitrogen if nitrogen is not None else 'N/A'} mg/kg")

        elif mode == 'p':
            phosphorus = sensor.read_phosphorus()
            result = {'phosphorus': phosphorus}
            print(f"\n인(P): {phosphorus if phosphorus is not None else 'N/A'} mg/kg")

        elif mode == 'k':
            potassium = sensor.read_potassium()
            result = {'potassium': potassium}
            print(f"\n칼륨(K): {potassium if potassium is not None else 'N/A'} mg/kg")

        elif mode == 'ec':
            ec = sensor.read_ec()
            result = {'ec': ec}
            print(f"\n전도도(EC): {ec if ec is not None else 'N/A'} μS/cm")

        elif mode == 'ph':
            ph = sensor.read_ph()
            result = {'ph': ph}
            print(f"\npH: {ph if ph is not None else 'N/A'}")

    except Exception as e:
        logger.error(f"측정 중 오류 발생: {e}")

    return result

def main():
    """
    메인 함수
    """
    # 인자 파서 설정 및 인자 파싱
    parser = setup_argument_parser()
    args = parser.parse_args()

    # 센서 초기화
    try:
        sensor = TaidacentSoilSensor(port=args.port, baudrate=args.baudrate)

        if not sensor.is_connected():
            logger.error("센서에 연결할 수 없습니다. 포트와 연결을 확인하세요.")
            return 1

        # 측정 모드에 따라 측정 및 결과 표시
        count = 0
        while args.count == 0 or count < args.count:
            measure_and_display(sensor, args.mode)
            count += 1

            # 마지막 측정이 아니면 대기
            if args.count == 0 or count < args.count:
                time.sleep(args.interval)

        # 센서 연결 종료
        sensor.close()

    except KeyboardInterrupt:
        logger.info("사용자에 의해 프로그램이 종료되었습니다.")
        if 'sensor' in locals():
            sensor.close()
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")
        if 'sensor' in locals():
            sensor.close()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
