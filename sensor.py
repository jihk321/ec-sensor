"""
Taidacent RS485 Soil NPK pH 센서 모듈

온도, 습도, 전도도, 질소, 인, 칼륨, pH를 측정하는 센서 클래스
"""

import time
import struct
import logging
from typing import Dict, Any, Tuple, Optional, Union

from rs485 import RS485Communication

# 로깅 설정
logger = logging.getLogger(__name__)

class TaidacentSoilSensor:
    """
    Taidacent RS485 Soil NPK pH 센서 클래스

    RS-485 통신을 통해 토양의 질소(N), 인(P), 칼륨(K), pH, 전도도(EC)를 측정하는 센서 제어 클래스
    """

    # 명령어 상수 (Modbus-RTU 프로토콜)
    # 질소, 인, 칼륨 명령어 (NPK 센서)
    CMD_READ_N = b'\x01\x03\x00\x1E\x00\x01\xE4\x0C'  # 질소 읽기 명령어
    CMD_READ_P = b'\x01\x03\x00\x1F\x00\x01\xB5\xCC'  # 인 읽기 명령어
    CMD_READ_K = b'\x01\x03\x00\x20\x00\x01\x85\xC0'  # 칼륨 읽기 명령어
    CMD_READ_NPK = b'\x01\x03\x00\x1E\x00\x03\x65\xCD'  # 질소, 인, 칼륨 한 번에 읽기

    # EC, pH 명령어 (EC&PH 센서)
    CMD_READ_EC_PH = b'\x01\x03\x00\x00\x00\x04\x44\x09'  # EC, pH 읽기 명령어
    CMD_READ_EC = b'\x01\x03\x00\x02\x00\x01\x25\xCA'     # EC만 읽기 명령어
    CMD_READ_PH = b'\x01\x03\x00\x03\x00\x01\x74\x0A'     # pH만 읽기 명령어

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600, device_id: int = 1, timeout: float = 1.0):
        """
        Taidacent RS485 Soil NPK pH 센서 초기화

        Args:
            port: 통신 포트 (None인 경우 자동 감지)
            baudrate: 통신 속도 (기본값: 9600)
            device_id: 장치 ID (기본값: 1)
            timeout: 타임아웃 시간 (초) (기본값: 1.0)
        """
        self.device_id = device_id
        self.comm = RS485Communication(port=port, baudrate=baudrate, timeout=timeout)

        # 센서 연결 확인
        if self.comm.is_connected:
            logger.info("Taidacent 토양 센서가 연결되었습니다.")
        else:
            logger.warning("Taidacent 토양 센서 연결에 실패했습니다.")

    def is_connected(self) -> bool:
        """
        센서 연결 상태 확인

        Returns:
            bool: 연결 상태
        """
        return self.comm.is_connected

    def calculate_crc16(self, data: bytes) -> bytes:
        """
        Modbus CRC-16 계산

        Args:
            data: CRC를 계산할 데이터

        Returns:
            bytes: 계산된 CRC-16 (2 바이트)
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        # CRC 바이트 순서 변경 (Little Endian)
        return bytes([crc & 0xFF, crc >> 8])

    def create_command(self, function_code: int, register_address: int, register_count: int) -> bytes:
        """
        Modbus 명령어 생성

        Args:
            function_code: 기능 코드 (일반적으로 3 또는 6)
            register_address: 레지스터 주소
            register_count: 레지스터 개수

        Returns:
            bytes: 생성된 명령어 (CRC 포함)
        """
        # 명령어 구성: 장치ID + 기능코드 + 레지스터주소(2바이트) + 레지스터개수(2바이트)
        cmd = bytes([self.device_id, function_code]) + \
              struct.pack('>H', register_address) + \
              struct.pack('>H', register_count)

        # CRC 계산 및 추가
        crc = self.calculate_crc16(cmd)
        return cmd + crc

    def read_nitrogen(self) -> Optional[int]:
        """
        질소(N) 함량 읽기

        Returns:
            int: 질소 함량 값 (mg/kg) 또는 None (오류 발생 시)
        """
        try:
            # 질소 레지스터 주소는 0x1E (30)
            response = self.comm.send_and_receive(self.CMD_READ_N, 7)

            if response and len(response) >= 7 and response[0] == self.device_id and response[1] == 0x03:
                # 응답 형식: 장치ID(1) + 기능코드(1) + 바이트수(1) + 데이터(2) + CRC(2)
                nitrogen = struct.unpack('>H', response[3:5])[0]
                logger.info(f"질소: {nitrogen} mg/kg")
                return nitrogen
            else:
                logger.error(f"질소 읽기 실패: 잘못된 응답 - {response.hex() if response else 'None'}")
                return None
        except Exception as e:
            logger.error(f"질소 읽기 중 오류 발생: {e}")
            return None

    def read_phosphorus(self) -> Optional[int]:
        """
        인(P) 함량 읽기

        Returns:
            int: 인 함량 값 (mg/kg) 또는 None (오류 발생 시)
        """
        try:
            # 인 레지스터 주소는 0x1F (31)
            response = self.comm.send_and_receive(self.CMD_READ_P, 7)

            if response and len(response) >= 7 and response[0] == self.device_id and response[1] == 0x03:
                # 응답 형식: 장치ID(1) + 기능코드(1) + 바이트수(1) + 데이터(2) + CRC(2)
                phosphorus = struct.unpack('>H', response[3:5])[0]
                logger.info(f"인: {phosphorus} mg/kg")
                return phosphorus
            else:
                logger.error(f"인 읽기 실패: 잘못된 응답 - {response.hex() if response else 'None'}")
                return None
        except Exception as e:
            logger.error(f"인 읽기 중 오류 발생: {e}")
            return None

    def read_potassium(self) -> Optional[int]:
        """
        칼륨(K) 함량 읽기

        Returns:
            int: 칼륨 함량 값 (mg/kg) 또는 None (오류 발생 시)
        """
        try:
            # 칼륨 레지스터 주소는 0x20 (32)
            response = self.comm.send_and_receive(self.CMD_READ_K, 7)

            if response and len(response) >= 7 and response[0] == self.device_id and response[1] == 0x03:
                # 응답 형식: 장치ID(1) + 기능코드(1) + 바이트수(1) + 데이터(2) + CRC(2)
                potassium = struct.unpack('>H', response[3:5])[0]
                logger.info(f"칼륨: {potassium} mg/kg")
                return potassium
            else:
                logger.error(f"칼륨 읽기 실패: 잘못된 응답 - {response.hex() if response else 'None'}")
                return None
        except Exception as e:
            logger.error(f"칼륨 읽기 중 오류 발생: {e}")
            return None

    def read_ec(self) -> Optional[int]:
        """
        전도도(EC) 읽기

        Returns:
            int: 전도도 값 (μS/cm) 또는 None (오류 발생 시)
        """
        try:
            # EC&PH 센서에서는 EC 레지스터 주소가 0x02 (2)
            response = self.comm.send_and_receive(self.CMD_READ_EC, 7)

            if response and len(response) >= 7 and response[0] == self.device_id and response[1] == 0x03:
                # 응답 형식: 장치ID(1) + 기능코드(1) + 바이트수(1) + 데이터(2) + CRC(2)
                ec = struct.unpack('>H', response[3:5])[0]
                logger.info(f"전도도: {ec} μS/cm")
                return ec
            else:
                logger.error(f"전도도 읽기 실패: 잘못된 응답 - {response.hex() if response else 'None'}")
                return None
        except Exception as e:
            logger.error(f"전도도 읽기 중 오류 발생: {e}")
            return None

    def read_ph(self) -> Optional[float]:
        """
        pH 읽기

        Returns:
            float: pH 값 또는 None (오류 발생 시)
        """
        try:
            # EC&PH 센서에서는 pH 레지스터 주소가 0x03 (3)
            response = self.comm.send_and_receive(self.CMD_READ_PH, 7)

            if response and len(response) >= 7 and response[0] == self.device_id and response[1] == 0x03:
                # 응답 형식: 장치ID(1) + 기능코드(1) + 바이트수(1) + 데이터(2) + CRC(2)
                ph_raw = struct.unpack('>H', response[3:5])[0]
                # pH 값은 10배로 확장되어 있으므로 10으로 나눔
                ph = ph_raw / 10.0
                logger.info(f"pH: {ph}")
                return ph
            else:
                logger.error(f"pH 읽기 실패: 잘못된 응답 - {response.hex() if response else 'None'}")
                return None
        except Exception as e:
            logger.error(f"pH 읽기 중 오류 발생: {e}")
            return None

    def read_ec_ph(self) -> Dict[str, Optional[Union[int, float]]]:
        """
        전도도(EC)와 pH 함께 읽기

        Returns:
            Dict: 센서 데이터 딕셔너리 {'ec': int, 'ph': float}
        """
        try:
            # EC&PH 센서에서 모든 데이터를 한 번에 읽기
            response = self.comm.send_and_receive(self.CMD_READ_EC_PH, 13)

            result = {
                'ec': None,
                'ph': None
            }

            if response and len(response) >= 13 and response[0] == self.device_id and response[1] == 0x03:
                # 응답 형식: 장치ID(1) + 기능코드(1) + 바이트수(1) + 데이터(8) + CRC(2)
                # 응답 데이터: 습도(2) + 온도(2) + EC(2) + pH(2)

                # EC는 7-8번째 바이트
                ec = struct.unpack('>H', response[7:9])[0]

                # pH는 9-10번째 바이트, 10으로 나눠야 함
                ph_raw = struct.unpack('>H', response[9:11])[0]
                ph = ph_raw / 10.0

                result['ec'] = ec
                result['ph'] = ph

                logger.info(f"전도도: {ec} μS/cm, pH: {ph}")
            else:
                logger.error(f"EC/pH 읽기 실패: 잘못된 응답 - {response.hex() if response else 'None'}")

            return result
        except Exception as e:
            logger.error(f"EC/pH 읽기 중 오류 발생: {e}")
            return {'ec': None, 'ph': None}

    def read_npk(self) -> Dict[str, Optional[int]]:
        """
        질소(N), 인(P), 칼륨(K) 함께 읽기

        Returns:
            Dict: 센서 데이터 딕셔너리 {'nitrogen': int, 'phosphorus': int, 'potassium': int}
        """
        try:
            # NPK 센서에서 모든 데이터를 한 번에 읽기
            response = self.comm.send_and_receive(self.CMD_READ_NPK, 11)

            result = {
                'nitrogen': None,
                'phosphorus': None,
                'potassium': None
            }

            if response and len(response) >= 11 and response[0] == self.device_id and response[1] == 0x03:
                # 응답 형식: 장치ID(1) + 기능코드(1) + 바이트수(1) + 데이터(6) + CRC(2)
                # 응답 데이터: 질소(2) + 인(2) + 칼륨(2)

                nitrogen = struct.unpack('>H', response[3:5])[0]
                phosphorus = struct.unpack('>H', response[5:7])[0]
                potassium = struct.unpack('>H', response[7:9])[0]

                result['nitrogen'] = nitrogen
                result['phosphorus'] = phosphorus
                result['potassium'] = potassium

                logger.info(f"질소: {nitrogen} mg/kg, 인: {phosphorus} mg/kg, 칼륨: {potassium} mg/kg")
            else:
                logger.error(f"NPK 읽기 실패: 잘못된 응답 - {response.hex() if response else 'None'}")

            return result
        except Exception as e:
            logger.error(f"NPK 읽기 중 오류 발생: {e}")
            return {'nitrogen': None, 'phosphorus': None, 'potassium': None}

    def read_all(self) -> Dict[str, Optional[Union[int, float]]]:
        """
        모든 센서 데이터 읽기 (NPK, EC, pH)

        Returns:
            Dict: 센서 데이터 딕셔너리 {'nitrogen': int, 'phosphorus': int, 'potassium': int, 'ec': int, 'ph': float}
        """
        # NPK 데이터 읽기
        npk_data = self.read_npk()

        # EC, pH 데이터 읽기
        ec_ph_data = self.read_ec_ph()

        # 결과 합치기
        result = {**npk_data, **ec_ph_data}

        return result

    def close(self) -> None:
        """
        센서 연결 종료
        """
        self.comm.disconnect()
        logger.info("Taidacent 토양 센서 연결이 종료되었습니다.")

    def __del__(self):
        """
        객체 소멸 시 연결 종료
        """
        self.close()
