"""Tests for system information module."""

import pytest
from unittest.mock import Mock, patch
from morchaos.core.system import (
    get_cpu_info,
    get_memory_info,
    get_disk_info,
    get_battery_info,
    get_network_info,
    get_system_info,
)


@patch("morchaos.core.system.psutil")
def test_get_cpu_info(mock_psutil):
    """Test CPU information collection."""
    # Setup mock
    mock_psutil.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
    mock_psutil.cpu_percent.side_effect = (
        lambda interval=1, percpu=False: [25.0, 30.0] if percpu else 27.5
    )

    mock_freq = Mock()
    mock_freq.max = 3000.0
    mock_freq.min = 800.0
    mock_freq.current = 2400.0
    mock_psutil.cpu_freq.return_value = mock_freq

    # Test
    cpu_info = get_cpu_info()

    assert cpu_info["physical_cores"] == 4
    assert cpu_info["logical_cores"] == 8
    assert cpu_info["max_frequency"] == 3000.0
    assert cpu_info["current_frequency"] == 2400.0
    assert cpu_info["usage_percent"] == 27.5


@patch("morchaos.core.system.psutil")
def test_get_memory_info(mock_psutil):
    """Test memory information collection."""
    # Setup mock
    mock_memory = Mock()
    mock_memory.total = 16 * 1024**3  # 16GB
    mock_memory.available = 8 * 1024**3  # 8GB
    mock_memory.used = 8 * 1024**3  # 8GB
    mock_memory.free = 8 * 1024**3  # 8GB
    mock_memory.percent = 50.0
    mock_psutil.virtual_memory.return_value = mock_memory

    mock_swap = Mock()
    mock_swap.total = 4 * 1024**3  # 4GB
    mock_swap.used = 1 * 1024**3  # 1GB
    mock_swap.free = 3 * 1024**3  # 3GB
    mock_swap.percent = 25.0
    mock_psutil.swap_memory.return_value = mock_swap

    # Test
    memory_info = get_memory_info()

    assert memory_info["total"] == 16 * 1024**3
    assert memory_info["available"] == 8 * 1024**3
    assert memory_info["percent"] == 50.0
    assert memory_info["swap_total"] == 4 * 1024**3
    assert memory_info["swap_percent"] == 25.0


@patch("morchaos.core.system.psutil")
def test_get_disk_info(mock_psutil):
    """Test disk information collection."""
    # Setup mock
    mock_partition = Mock()
    mock_partition.device = "/dev/sda1"
    mock_partition.mountpoint = "/"
    mock_partition.fstype = "ext4"
    mock_psutil.disk_partitions.return_value = [mock_partition]

    mock_usage = Mock()
    mock_usage.total = 1000 * 1024**3  # 1TB
    mock_usage.used = 500 * 1024**3  # 500GB
    mock_usage.free = 500 * 1024**3  # 500GB
    mock_psutil.disk_usage.return_value = mock_usage

    # Test
    disk_info = get_disk_info()

    assert "/dev/sda1" in disk_info
    partition_info = disk_info["/dev/sda1"]
    assert partition_info["mountpoint"] == "/"
    assert partition_info["filesystem"] == "ext4"
    assert partition_info["total"] == 1000 * 1024**3
    assert partition_info["percent"] == 50.0


@patch("morchaos.core.system.psutil")
def test_get_battery_info_present(mock_psutil):
    """Test battery information when battery is present."""
    # Setup mock
    mock_battery = Mock()
    mock_battery.percent = 85.0
    mock_battery.power_plugged = True
    mock_battery.secsleft = 3600  # 1 hour
    mock_psutil.sensors_battery.return_value = mock_battery

    # Test
    battery_info = get_battery_info()

    assert battery_info["present"] is True
    assert battery_info["percent"] == 85.0
    assert battery_info["power_plugged"] is True
    assert battery_info["seconds_left"] == 3600


@patch("morchaos.core.system.psutil")
def test_get_battery_info_not_present(mock_psutil):
    """Test battery information when no battery is present."""
    mock_psutil.sensors_battery.return_value = None

    battery_info = get_battery_info()

    assert battery_info["present"] is False


@patch("morchaos.core.system.psutil")
def test_get_network_info(mock_psutil):
    """Test network information collection."""
    # Setup mock
    mock_addr = Mock()
    mock_addr.family = 2  # AF_INET
    mock_addr.address = "192.168.1.100"
    mock_addr.netmask = "255.255.255.0"
    mock_addr.broadcast = "192.168.1.255"

    mock_psutil.net_if_addrs.return_value = {"eth0": [mock_addr]}

    mock_stat = Mock()
    mock_stat.isup = True
    mock_stat.duplex = 2  # Full duplex
    mock_stat.speed = 1000  # 1Gbps
    mock_stat.mtu = 1500

    mock_psutil.net_if_stats.return_value = {"eth0": mock_stat}

    # Test
    network_info = get_network_info()

    assert "eth0" in network_info
    interface_info = network_info["eth0"]
    assert interface_info["is_up"] is True
    assert interface_info["speed"] == 1000
    assert interface_info["mtu"] == 1500
    assert len(interface_info["addresses"]) == 1
    assert interface_info["addresses"][0]["address"] == "192.168.1.100"


@patch("morchaos.core.system.psutil")
def test_get_system_info(mock_psutil):
    """Test comprehensive system information collection."""
    # Setup basic mocks
    mock_psutil.cpu_count.return_value = 4
    mock_psutil.cpu_percent.return_value = 25.0
    mock_psutil.virtual_memory.return_value = Mock(total=8 * 1024**3, percent=50.0)
    mock_psutil.swap_memory.return_value = Mock(total=4 * 1024**3, percent=25.0)
    mock_psutil.disk_partitions.return_value = []
    mock_psutil.sensors_battery.return_value = None
    mock_psutil.net_if_addrs.return_value = {}
    mock_psutil.net_if_stats.return_value = {}

    # Test
    system_info = get_system_info()

    assert "cpu" in system_info
    assert "memory" in system_info
    assert "disk" in system_info
    assert "battery" in system_info
    assert "network" in system_info
