

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceAdapter(ABC):
    """Base adapter for all microgrid devices"""
    
    def __init__(self, device_id: str, config: Dict[str, Any]):
        self.device_id = device_id
        self.config = config
        self.connected = False
        self.last_reading = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the device"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the device"""
        pass
    
    @abstractmethod
    async def read_data(self) -> Dict[str, Any]:
        """Read current data from device"""
        pass
    
    @abstractmethod
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Send command to device"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status"""
        return {
            'device_id': self.device_id,
            'connected': self.connected,
            'last_reading': self.last_reading,
            'adapter_type': self.__class__.__name__
        }


class SolarInverterAdapter(DeviceAdapter):
    """Adapter for solar inverters (Modbus/TCP)"""
    
    async def connect(self) -> bool:
        """Connect to solar inverter via Modbus"""
        try:
            # Simulated connection
            logger.info(f"Connecting to solar inverter {self.device_id}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self) -> bool:
        self.connected = False
        return True
    
    async def read_data(self) -> Dict[str, Any]:
        """Read solar generation data"""
        # Simulated data
        data = {
            'power_output': 45.2,  # kW
            'voltage': 415.5,
            'current': 68.9,
            'energy_today': 234.5,  # kWh
            'efficiency': 98.3,
            'temperature': 42.1
        }
        self.last_reading = data
        return data
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Send command to inverter"""
        logger.info(f"Sending command {command} to {self.device_id}")
        return True


class BatteryAdapter(DeviceAdapter):
    """Adapter for battery energy storage systems"""
    
    async def connect(self) -> bool:
        logger.info(f"Connecting to battery system {self.device_id}")
        self.connected = True
        return True
    
    async def disconnect(self) -> bool:
        self.connected = False
        return True
    
    async def read_data(self) -> Dict[str, Any]:
        """Read battery status"""
        data = {
            'state_of_charge': 75.5,  # %
            'voltage': 380.2,
            'current': -15.3,  # Negative = discharging
            'power': -5.8,  # kW
            'temperature': 28.5,
            'health': 98.0,  # %
            'cycles': 450
        }
        self.last_reading = data
        return data
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Control battery (charge/discharge)"""
        if command == 'set_power':
            power = params.get('power', 0)
            logger.info(f"Setting battery power to {power} kW")
        return True


class SmartMeterAdapter(DeviceAdapter):
    """Adapter for smart electricity meters"""
    
    async def connect(self) -> bool:
        logger.info(f"Connecting to smart meter {self.device_id}")
        self.connected = True
        return True
    
    async def disconnect(self) -> bool:
        self.connected = False
        return True
    
    async def read_data(self) -> Dict[str, Any]:
        """Read consumption data"""
        data = {
            'active_power': 125.8,  # kW
            'reactive_power': 23.4,  # kVAR
            'power_factor': 0.95,
            'voltage_l1': 230.2,
            'voltage_l2': 229.8,
            'voltage_l3': 231.1,
            'current_l1': 180.5,
            'current_l2': 178.2,
            'current_l3': 182.1,
            'frequency': 50.02,
            'energy_consumed': 1234.5  # kWh
        }
        self.last_reading = data
        return data
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Smart meter commands"""
        logger.info(f"Command {command} sent to meter")
        return True


class AdapterFactory:
    """Factory for creating device adapters"""
    
    _adapters = {
        'solar_inverter': SolarInverterAdapter,
        'battery': BatteryAdapter,
        'smart_meter': SmartMeterAdapter
    }
    
    @classmethod
    def create_adapter(
        cls,
        device_type: str,
        device_id: str,
        config: Dict[str, Any]
    ) -> Optional[DeviceAdapter]:
        """Create appropriate adapter for device type"""
        adapter_class = cls._adapters.get(device_type)
        if adapter_class:
            return adapter_class(device_id, config)
        else:
            logger.error(f"Unknown device type: {device_type}")
            return None
    
    @classmethod
    def register_adapter(cls, device_type: str, adapter_class):
        """Register new adapter type"""
        cls._adapters[device_type] = adapter_class
        logger.info(f"Registered adapter: {device_type}")


# Benchmark example
async def run_adapter_benchmark():
    """Test adapter system"""
    # Create adapters
    solar = AdapterFactory.create_adapter(
        'solar_inverter',
        'solar_001',
        {'ip': '192.168.1.100', 'port': 502}
    )
    
    battery = AdapterFactory.create_adapter(
        'battery',
        'bess_001',
        {'ip': '192.168.1.101'}
    )
    
    # Connect and read data
    await solar.connect()
    solar_data = await solar.read_data()
    logger.info(f"Solar data: {solar_data}")
    
    await battery.connect()
    battery_data = await battery.read_data()
    logger.info(f"Battery data: {battery_data}")
    
    return {'solar': solar_data, 'battery': battery_data}


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_adapter_benchmark())
