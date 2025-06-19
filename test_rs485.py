"""
RS485 연결 테스트 스크립트
"""

import logging
from rs485 import RS485Communication

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    RS485 연결 테스트
    """
    # RS485 통신 인스턴스 생성 (자동 포트 감지)
    print("RS485 포트 감지 중...")
    comm = RS485Communication()

    # 연결 상태 확인
    if comm.is_connected:
        print(f"포트 {comm.port}에 성공적으로 연결되었습니다.")

        # 테스트 명령어 전송
        test_cmd = b'\x01\x03\x00\x00\x00\x01\x84\x0A'  # 예시 명령어
        print(f"테스트 명령어 전송: {test_cmd.hex()}")

        if comm.send_command(test_cmd):
            print("명령어 전송 성공")

            # 응답 읽기 시도
            response = comm.read_response(timeout=1.0)
            if response:
                print(f"응답 수신: {response.hex()}")
            else:
                print("응답 없음")
        else:
            print("명령어 전송 실패")

        # 연결 종료
        comm.disconnect()
        print("연결 종료")
    else:
        print("RS485 포트에 연결할 수 없습니다.")
        print("다음을 확인하세요:")
        print("1. RS485 장치가 연결되어 있는지")
        print("2. 올바른 드라이버가 설치되어 있는지")

if __name__ == "__main__":
    main()
