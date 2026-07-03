from __future__ import annotations


class ModelRouterError(Exception):
    pass


class ProviderRequestError(ModelRouterError):
    def __init__(self, provider: str, model: str, message: str, status_code: int | None = None, response_excerpt: str | None = None) -> None:
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.status_code = status_code
        self.response_excerpt = response_excerpt


class ReadinessError(ModelRouterError):
    pass
