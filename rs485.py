"""
RS-485 통신 모듈

윈도우와 라즈베리파이(리눅스) 환경에서 모두 작동하는 RS-485 통신 클래스
"""

import os
import sys
import time
import platform
import logging
from typing import Optional, Union

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RS485Communication:
    """
    RS-485 통신을 위한 클래스
    윈도우와 라즈베리파이(리눅스) 환경에서 모두 작동
    """

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600, timeout: float = 1.0):
        """
        RS-485 통신 초기화

        Args:
            port: 통신 포트 (None인 경우 자동 감지)
            baudrate: 통신 속도 (기본값: 9600)
            timeout: 타임아웃 시간 (초) (기본값: 1.0)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.system = platform.system()
        self.is_connected = False

        # 시스템 환경 확인
        logger.info(f"현재 운영체제: {self.system}")

        # 자동으로 포트 감지 및 연결
        if port is None:
            self.detect_port()
        else:
            self.connect()

    def detect_port(self) -> None:
        """
        시스템에 맞게 RS-485 포트 자동 감지
        """
        try:
            # 필요한 모듈 직접 임포트
            sys.path.append(os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages'))

            # pyserial 라이브러리 임포트
            try:
                import serial.tools.list_ports
            except ImportError:
                logger.error("pyserial 라이브러리를 찾을 수 없습니다. 'pip install pyserial'로 설치하세요.")
                return

            # 사용 가능한 포트 목록 가져오기
            available_ports = list(serial.tools.list_ports.comports())

            if not available_ports:
                logger.warning("사용 가능한 시리얼 포트가 없습니다.")
                return

            logger.info(f"사용 가능한 포트 목록: {[port.device for port in available_ports]}")

            # 윈도우와 라즈베리파이에서 포트 감지 방식이 다름
            if self.system == "Windows":
                # 윈도우에서는 일반적으로 COM 포트 사용
                for port in available_ports:
                    if "COM" in port.device:
                        self.port = port.device
                        logger.info(f"윈도우 환경에서 포트 감지: {self.port}")
                        break
            else:
                # 리눅스(라즈베리파이)에서는 일반적으로 /dev/ttyUSB 또는 /dev/ttyAMA 포트 사용
                for port in available_ports:
                    if "ttyUSB" in port.device or "ttyAMA" in port.device or "ttyS" in port.device:
                        self.port = port.device
                        logger.info(f"라즈베리파이 환경에서 포트 감지: {self.port}")
                        break

            if self.port:
                self.connect()
            else:
                logger.error("RS-485 포트를 찾을 수 없습니다.")
        except Exception as e:
            logger.error(f"포트 감지 중 오류 발생: {e}")

    def connect(self) -> bool:
        """
        RS-485 포트에 연결

        Returns:
            bool: 연결 성공 여부
        """
        try:
            if not self.port:
                logger.error("포트가 지정되지 않았습니다.")
                return False

            # 필요한 모듈 직접 임포트
            sys.path.append(os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages'))

            # pyserial 라이브러리 임포트
            try:
                import serial
            except ImportError:
                logger.error("pyserial 라이브러리를 찾을 수 없습니다. 'pip install pyserial'로 설치하세요.")
                return False

            # 직접 Serial 클래스 사용
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,  # EIGHTBITS
                parity='N',  # PARITY_NONE
                stopbits=1,  # STOPBITS_ONE
                timeout=self.timeout
            )

            if self.serial_conn.is_open:
                self.is_connected = True
                logger.info(f"포트 {self.port}에 성공적으로 연결되었습니다.")
                return True
            else:
                self.is_connected = False
                logger.error(f"포트 {self.port}에 연결할 수 없습니다.")
                return False

        except Exception as e:
            self.is_connected = False
            logger.error(f"연결 중 오류 발생: {e}")
            return False

    def disconnect(self) -> None:
        """
        RS-485 연결 해제
        """
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.is_connected = False
            logger.info("포트 연결이 해제되었습니다.")

    def send_command(self, command: bytes) -> bool:
        """
        RS-485를 통해 명령어 전송

        Args:
            command: 전송할 명령어 (바이트)

        Returns:
            bool: 명령어 전송 성공 여부
        """
        if not self.is_connected or not self.serial_conn:
            logger.error("포트가 연결되어 있지 않습니다.")
            return False

        try:
            self.serial_conn.write(command)
            logger.debug(f"명령어 전송: {command.hex()}")
            return True
        except Exception as e:
            logger.error(f"명령어 전송 중 오류 발생: {e}")
            return False

    def read_response(self, size: Optional[int] = None, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        RS-485로부터 응답 읽기

        Args:
            size: 읽을 바이트 수 (None인 경우 가능한 모든 데이터 읽기)
            timeout: 타임아웃 시간 (초) (None인 경우 기본값 사용)

        Returns:
            bytes: 읽은 데이터 또는 None (오류 발생 시)
        """
        if not self.is_connected or not self.serial_conn:
            logger.error("포트가 연결되어 있지 않습니다.")
            return None

        try:
            # 임시로 타임아웃 변경
            original_timeout = None
            if timeout is not None:
                original_timeout = self.serial_conn.timeout
                self.serial_conn.timeout = timeout

            # 데이터 읽기
            if size is not None:
                response = self.serial_conn.read(size)
            else:
                # 가능한 모든 데이터 읽기
                response = self.serial_conn.read_all()
                if not response:  # 데이터가 없으면 일정 시간 대기 후 다시 시도
                    time.sleep(0.1)
                    response = self.serial_conn.read_all()

            # 타임아웃 복원
            if original_timeout is not None:
                self.serial_conn.timeout = original_timeout

            if response:
                logger.debug(f"응답 수신: {response.hex()}")
            else:
                logger.warning("응답이 없거나 타임아웃 발생")

            return response
        except Exception as e:
            logger.error(f"응답 읽기 중 오류 발생: {e}")
            return None

    def send_and_receive(self, command: bytes, response_size: Optional[int] = None, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        명령어를 전송하고 응답 수신

        Args:
            command: 전송할 명령어 (바이트)
            response_size: 예상되는 응답 크기 (바이트)
            timeout: 응답 대기 타임아웃 (초)

        Returns:
            bytes: 수신된 응답 또는 None (오류 발생 시)
        """
        if self.send_command(command):
            # 명령 전송 후 약간의 지연
            time.sleep(0.05)
            return self.read_response(response_size, timeout)
        return None

    def __del__(self):
        """
        객체 소멸 시 연결 해제
        """
        self.disconnect()
