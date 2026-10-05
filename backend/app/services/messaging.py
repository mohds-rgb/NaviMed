from dataclasses import dataclass

from app.core.errors import DomainError


@dataclass(frozen=True, slots=True)
class ProviderSendResult:
    accepted: bool
    provider_message_id: str | None
    error_code: str | None = None
    evidence: str = "none"


class MessagingProvider:
    def send_template_message(self, *, recipient: str, template_key: str, variables: dict[str, str]) -> ProviderSendResult:
        raise NotImplementedError

    def query_delivery_status(self, *, provider_message_id: str) -> str:
        raise NotImplementedError

    def verify_webhook(self, *, raw_body: bytes, signature: str, timestamp: str | None = None) -> bool:
        raise NotImplementedError


class DisabledMessagingProvider(MessagingProvider):
    def send_template_message(self, *, recipient: str, template_key: str, variables: dict[str, str]) -> ProviderSendResult:
        return ProviderSendResult(False, None, "MESSAGE_PROVIDER_UNAVAILABLE", "disabled")

    def query_delivery_status(self, *, provider_message_id: str) -> str:
        raise DomainError("MESSAGE_PROVIDER_UNAVAILABLE", "Messaging provider is disabled", 503, True)

    def verify_webhook(self, *, raw_body: bytes, signature: str, timestamp: str | None = None) -> bool:
        return False


class DemoMessagingProvider(MessagingProvider):
    """Portfolio-safe adapter: demonstrates the boundary but never claims delivery."""

    def send_template_message(self, *, recipient: str, template_key: str, variables: dict[str, str]) -> ProviderSendResult:
        return ProviderSendResult(True, "demo-message", None, "demo")

    def query_delivery_status(self, *, provider_message_id: str) -> str:
        return "provider_accepted"

    def verify_webhook(self, *, raw_body: bytes, signature: str, timestamp: str | None = None) -> bool:
        return False
