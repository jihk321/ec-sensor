"""
EC 센서 테스트 모듈
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 상위 디렉토리의 src를 import 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensor import TaidacentSoilSensor
from rs485 import RS485Communication

class TestRS485Communication(unittest.TestCase):
    """
    RS485Communication 클래스 테스트
    """

    @patch('src.ec_sensor.rs485.serial')
    def test_connect(self, mock_serial):
        """
        연결 테스트
        """
        # 시리얼 연결 모의 객체 설정
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial.Serial.return_value = mock_serial_instance

        # RS485Communication 인스턴스 생성 (자동 연결 비활성화)
        comm = RS485Communication(port="COM1")

        # 연결 상태 확인
        self.assertTrue(comm.is_connected)
        self.assertEqual(comm.port, "COM1")
        self.assertEqual(comm.baudrate, 9600)

        # 시리얼 연결이 올바른 매개변수로 호출되었는지 확인
        mock_serial.Serial.assert_called_once_with(
            port="COM1",
            baudrate=9600,
            bytesize=mock_serial.EIGHTBITS,
            parity=mock_serial.PARITY_NONE,
            stopbits=mock_serial.STOPBITS_ONE,
            timeout=1.0
        )

    @patch('src.ec_sensor.rs485.serial')
    def test_send_command(self, mock_serial):
        """
        명령어 전송 테스트
        """
        # 시리얼 연결 모의 객체 설정
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial.Serial.return_value = mock_serial_instance

        # RS485Communication 인스턴스 생성
        comm = RS485Communication(port="COM1")

        # 명령어 전송
        result = comm.send_command(b'\x01\x03\x00\x00\x00\x01\x84\x0A')

        # 결과 확인
        self.assertTrue(result)
        mock_serial_instance.write.assert_called_once_with(b'\x01\x03\x00\x00\x00\x01\x84\x0A')

    @patch('src.ec_sensor.rs485.serial')
    def test_read_response(self, mock_serial):
        """
        응답 읽기 테스트
        """
        # 시리얼 연결 모의 객체 설정
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_instance.read.return_value = b'\x01\x03\x02\x00\x64\xB9\xAF'
        mock_serial.Serial.return_value = mock_serial_instance

        # RS485Communication 인스턴스 생성
        comm = RS485Communication(port="COM1")

        # 응답 읽기
        response = comm.read_response(7)

        # 결과 확인
        self.assertEqual(response, b'\x01\x03\x02\x00\x64\xB9\xAF')
        mock_serial_instance.read.assert_called_once_with(7)


class TestTaidacentSoilSensor(unittest.TestCase):
    """
    TaidacentSoilSensor 클래스 테스트
    """

    @patch('src.ec_sensor.sensor.RS485Communication')
    def test_init(self, mock_rs485):
        """
        초기화 테스트
        """
        # RS485Communication 모의 객체 설정
        mock_rs485_instance = MagicMock()
        mock_rs485_instance.is_connected = True
        mock_rs485.return_value = mock_rs485_instance

        # TaidacentSoilSensor 인스턴스 생성
        sensor = TaidacentSoilSensor(port="COM1")

        # 초기화 확인
        self.assertEqual(sensor.device_id, 1)
        self.assertEqual(sensor.comm, mock_rs485_instance)

        # RS485Communication이 올바른 매개변수로 호출되었는지 확인
        mock_rs485.assert_called_once_with(port="COM1", baudrate=9600, timeout=1.0)

    # @patch('src.ec_sensor.sensor.RS485Communication')
    # def test_read_temperature(self, mock_rs485):
    #     """
    #     온도 읽기 테스트
    #     """
    #     # RS485Communication 모의 객체 설정
    #     mock_rs485_instance = MagicMock()
    #     mock_rs485_instance.is_connected = True
    #     # 온도 10.0°C (0x0064 = 100, 100/10 = 10.0)를 반환하는 응답 설정
    #     mock_rs485_instance.send_and_receive.return_value = b'\x01\x03\x02\x00\x64\xB9\xAF'
    #     mock_rs485.return_value = mock_rs485_instance

    #     # TaidacentSoilSensor 인스턴스 생성
    #     sensor = TaidacentSoilSensor(port="COM1")

    #     # 온도 읽기
    #     temperature = sensor.read_temperature()

    #     # 결과 확인
    #     self.assertEqual(temperature, 10.0)
    #     mock_rs485_instance.send_and_receive.assert_called_once_with(
    #         TaidacentSoilSensor.CMD_READ_TEMPERATURE, 7
    #     )

    # @patch('src.ec_sensor.sensor.RS485Communication')
    # def test_read_humidity(self, mock_rs485):
    #     """
    #     습도 읽기 테스트
    #     """
    #     # RS485Communication 모의 객체 설정
    #     mock_rs485_instance = MagicMock()
    #     mock_rs485_instance.is_connected = True
    #     # 습도 50.0% (0x01F4 = 500, 500/10 = 50.0)를 반환하는 응답 설정
    #     mock_rs485_instance.send_and_receive.return_value = b'\x01\x03\x02\x01\xF4\xB8\x38'
    #     mock_rs485.return_value = mock_rs485_instance

    #     # TaidacentSoilSensor 인스턴스 생성
    #     sensor = TaidacentSoilSensor(port="COM1")

    #     # 습도 읽기
    #     humidity = sensor.read_humidity()

    #     # 결과 확인
    #     self.assertEqual(humidity, 50.0)
    #     mock_rs485_instance.send_and_receive.assert_called_once_with(
    #         TaidacentSoilSensor.CMD_READ_HUMIDITY, 7
    #     )

    @patch('src.ec_sensor.sensor.RS485Communication')
    def test_read_ec(self, mock_rs485):
        """
        전도도 읽기 테스트
        """
        # RS485Communication 모의 객체 설정
        mock_rs485_instance = MagicMock()
        mock_rs485_instance.is_connected = True
        # 전도도 1000 μS/cm를 반환하는 응답 설정
        mock_rs485_instance.send_and_receive.return_value = b'\x01\x03\x02\x03\xE8\xB8\xFA'
        mock_rs485.return_value = mock_rs485_instance

        # TaidacentSoilSensor 인스턴스 생성
        sensor = TaidacentSoilSensor(port="COM1")

        # 전도도 읽기
        ec = sensor.read_ec()

        # 결과 확인
        self.assertEqual(ec, 1000)
        mock_rs485_instance.send_and_receive.assert_called_once_with(
            TaidacentSoilSensor.CMD_READ_EC, 7
        )

    # @patch('src.ec_sensor.sensor.RS485Communication')
    # def test_read_all(self, mock_rs485):
    #     """
    #     모든 센서 데이터 읽기 테스트
    #     """
    #     # RS485Communication 모의 객체 설정
    #     mock_rs485_instance = MagicMock()
    #     mock_rs485_instance.is_connected = True
    #     # 온도 10.0°C, 습도 50.0%, 전도도 1000 μS/cm를 반환하는 응답 설정
    #     mock_rs485_instance.send_and_receive.return_value = b'\x01\x03\x06\x00\x64\x01\xF4\x03\xE8\x97\x66'
    #     mock_rs485.return_value = mock_rs485_instance

    #     # TaidacentSoilSensor 인스턴스 생성
    #     sensor = TaidacentSoilSensor(port="COM1")

    #     # 모든 센서 데이터 읽기
    #     data = sensor.read_all()

    #     # 결과 확인
    #     self.assertEqual(data['temperature'], 10.0)
    #     self.assertEqual(data['humidity'], 50.0)
    #     self.assertEqual(data['ec'], 1000)
    #     mock_rs485_instance.send_and_receive.assert_called_once_with(
    #         TaidacentSoilSensor., 11
    #     )


if __name__ == '__main__':
    unittest.main()
