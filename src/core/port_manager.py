# src/core/port_manager.py
import socket

class PortManager:
    def __init__(self, start_port=9000, end_port=9100):
        self.port_range = range(start_port, end_port+1)
        self.used_ports = set()
    
    def is_port_available(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def allocate_port(self):
        for port in self.port_range:
            if port not in self.used_ports and self.is_port_available(port):
                self.used_ports.add(port)
                return port
        return None
    
    def release_port(self, port):
        self.used_ports.discard(port)