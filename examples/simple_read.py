#!/usr/bin/env python
"""
Taidacent RS485 Soil NPK pH 센서 간단 사용 예제

이 예제는 Taidacent RS485 Soil NPK pH 센서를 사용하여 토양의 질소, 인, 칼륨, pH, 전도도를 측정하는
기본적인 방법을 보여줍니다.
"""

import time
import sys
import os

# 상위 디렉토리의 모듈을 import 할 수 있도록 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensor import TaidacentSoilSensor

def main():
    """
    메인 함수
    """
    # 센서 초기화 (포트를 지정하지 않으면 자동 감지)
    sensor = TaidacentSoilSensor()

    if not sensor.is_connected():
        print("센서에 연결할 수 없습니다. 연결을 확인하세요.")
        return 1

    print("Taidacent RS485 Soil NPK pH 센서에 연결되었습니다.")
    print("5초 간격으로 3회 측정을 시작합니다...\n")

    try:
        for i in range(3):
            print(f"[측정 #{i+1}]")

            # NPK 측정
            npk_data = sensor.read_npk()
            print("NPK 측정 결과:")
            print(f"- 질소(N): {npk_data.get('nitrogen', 'N/A')} mg/kg")
            print(f"- 인(P): {npk_data.get('phosphorus', 'N/A')} mg/kg")
            print(f"- 칼륨(K): {npk_data.get('potassium', 'N/A')} mg/kg")

            # EC 및 pH 측정
            ec_ph_data = sensor.read_ec_ph()
            print("\nEC/pH 측정 결과:")
            print(f"- 전도도(EC): {ec_ph_data.get('ec', 'N/A')} μS/cm")
            print(f"- pH: {ec_ph_data.get('ph', 'N/A')}")

            # 마지막 측정이 아니면 대기
            if i < 2:
                print("\n5초 후 다음 측정을 시작합니다...")
                time.sleep(5)
            else:
                print("\n측정이 완료되었습니다.")

    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
    finally:
        # 항상 센서 연결 종료
        sensor.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
