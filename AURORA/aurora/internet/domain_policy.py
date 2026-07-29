from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse


PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


@dataclass(slots=True)
class UrlDecision:
    allowed: bool
    reason: str
    domain: str = ""
    requires_confirmation: bool = False


class DomainPolicy:
    def __init__(self, allowed: list[str], trusted: list[str], blocked: list[str], allow_private_networks: bool = False) -> None:
        self.allowed = {item.lower() for item in allowed}
        self.trusted = {item.lower() for item in trusted}
        self.blocked = {item.lower() for item in blocked}
        self.allow_private_networks = allow_private_networks

    def validate_url(self, url: str, resolve_dns: bool = True) -> UrlDecision:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return UrlDecision(False, f"Esquema bloqueado: {parsed.scheme}")
        if parsed.username or parsed.password:
            return UrlDecision(False, "URL com credenciais embutidas bloqueada")
        host = (parsed.hostname or "").lower()
        if not host:
            return UrlDecision(False, "URL sem dominio")
        if self._matches(host, self.blocked):
            return UrlDecision(False, "Dominio bloqueado", host)
        if parsed.port and parsed.port not in {80, 443}:
            return UrlDecision(False, "Porta nao autorizada", host)
        try:
            ip = ipaddress.ip_address(host)
            if self._private_ip(ip):
                return UrlDecision(self.allow_private_networks, "Endereco privado requer autorizacao explicita", host, not self.allow_private_networks)
        except ValueError:
            pass
        if resolve_dns and not self.allow_private_networks:
            for info in socket.getaddrinfo(host, None):
                ip = ipaddress.ip_address(info[4][0])
                if self._private_ip(ip):
                    return UrlDecision(False, "DNS resolve para rede privada", host)
        if self.allowed and not self._matches(host, self.allowed) and not self._matches(host, self.trusted):
            return UrlDecision(False, "Dominio fora da lista permitida", host, True)
        return UrlDecision(True, "Dominio permitido", host)

    def _matches(self, host: str, domains: set[str]) -> bool:
        return any(host == domain or host.endswith("." + domain) for domain in domains)

    def _private_ip(self, ip: ipaddress._BaseAddress) -> bool:
        return any(ip in network for network in PRIVATE_NETWORKS)
