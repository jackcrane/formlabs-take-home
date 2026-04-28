# mock_printers.py

from dataclasses import dataclass
from typing import List


@dataclass
class MockPrinter:
    id: str
    product_name: str
    status: str
    is_connected: bool
    connection_type: str
    ip_address: str
    firmware_version: str


@dataclass
class MockPrintersResponse:
    count: int
    devices: List[MockPrinter]


MOCK_PRINTERS = MockPrintersResponse(
    count=2,
    devices=[
        MockPrinter(
            id="mock-printer-1",
            product_name="Form 4BL",
            status="IDLE",
            is_connected=True,
            connection_type="LAN",
            ip_address="192.168.1.101",
            firmware_version="1.2.3",
        ),
        MockPrinter(
            id="mock-printer-2",
            product_name="Form 4BL",
            status="PRINTING",
            is_connected=True,
            connection_type="LAN",
            ip_address="192.168.1.102",
            firmware_version="1.1.8",
        ),
    ],
)