from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from typing import Any

from core_domain.errors import ValidationError
from core_domain.pipeline.pipeline_behavior import PipelineBehavior
from core_domain.validation import Validatable, Validator, ValidationRule


class ValidationBehavior(PipelineBehavior[Any]):
    def __init__(
        self,
        validators: dict[type[Any], Iterable[Validator | ValidationRule]] | None = None,
    ) -> None:
        self._validators = validators or {}

    async def handle(self, request: Any, next_handler: Callable[[], Awaitable[Any]]) -> Any:
        self._validate_request(request)
        return await next_handler()

    def _validate_request(self, request: Any) -> None:
        if isinstance(request, Validatable):
            request.validate()

        for validator in self._validators_for(request):
            self._invoke_validator(validator, request)

    def _validators_for(self, request: Any) -> Iterable[Validator | ValidationRule]:
        request_type = type(request)
        validators = list(self._validators.get(request_type, []))

        for known_type, known_validators in self._validators.items():
            if known_type is request_type:
                continue
            if isinstance(request, known_type):
                validators.extend(known_validators)

        return validators

    def _invoke_validator(self, validator: Validator | ValidationRule, request: Any) -> None:
        try:
            if hasattr(validator, "validate"):
                validator.validate(request)
            else:
                validator(request)
        except ValidationError:
            raise
        except Exception as ex:
            raise ValidationError(str(ex)) from ex