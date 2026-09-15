"""
Cliente HTTP reutilizable para llamadas a APIs.
Maneja autenticación, rate limiting y reintentos.
"""

import time
import requests
from typing import Optional, Dict, Any
from .logger import setup_logger


class APIClient:
    """Cliente HTTP para llamadas a APIs con manejo de errores y rate limiting."""
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Inicializa el cliente API.
        
        Args:
            base_url: URL base de la API
            headers: Headers HTTP personalizados
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.logger = setup_logger()
        
        if headers:
            self.session.headers.update(headers)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Realiza una petición HTTP con reintentos.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API
            params: Parámetros de query
            data: Datos para el body
            max_retries: Número máximo de reintentos
            retry_delay: Segundos entre reintentos
            
        Returns:
            Respuesta JSON o None si falla
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Intento {attempt + 1}/{max_retries}: {method} {url}")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=30
                )
                
                # Manejar rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', retry_delay))
                    self.logger.warning(f"Rate limit alcanzado. Esperando {retry_after} segundos...")
                    time.sleep(retry_after)
                    continue
                
                # Manejar errores HTTP
                response.raise_for_status()
                
                # Parsear respuesta JSON
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"Error HTTP: {e}")
                if attempt < max_retries - 1:
                    self.logger.info(f"Reintentando en {retry_delay} segundos...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Fallo después de {max_retries} intentos")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error de conexión: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return None
        
        return None
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Realiza una petición GET."""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Realiza una petición POST."""
        return self._make_request("POST", endpoint, data=data, **kwargs)
    
    def close(self):
        """Cierra la sesión HTTP."""
        self.session.close()
        self.logger.debug("Sesión HTTP cerrada")