"""Validation for daily feed nitrogen conservation."""

from math import isfinite

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext
from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)
from aquatwin.validation.validation_result import ValidationResult


class FeedNitrogenConservationValidator:
    """Validate conservation of nitrogen introduced through feeding."""

    _TOLERANCE = 1e-9

    @classmethod
    def validate(
        cls,
        context: StepContext,
    ) -> ValidationResult:
        """Return validation findings for feed nitrogen metrics."""
        findings: list[ValidationError] = []

        total_feed_nitrogen_metric = cls._find_latest_metric(
            context=context,
            metric_name="total_feed_nitrogen_mg",
        )
        feed_organic_n_input_metric = cls._find_latest_metric(
            context=context,
            metric_name="feed_organic_n_input_mg",
        )

        cls._validate_metric_value(
            metric=total_feed_nitrogen_metric,
            findings=findings,
        )
        cls._validate_metric_value(
            metric=feed_organic_n_input_metric,
            findings=findings,
        )

        if not context.daily_event_plan.feeding:
            return ValidationResult(findings=tuple(findings))

        if total_feed_nitrogen_metric is None:
            findings.append(
                ValidationError(
                    code="MISSING_TOTAL_FEED_NITROGEN",
                    field="total_feed_nitrogen_mg",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        "total_feed_nitrogen_mg is required when "
                        "feeding is scheduled."
                    ),
                )
            )

        if feed_organic_n_input_metric is None:
            findings.append(
                ValidationError(
                    code="MISSING_FEED_NITROGEN_OUTPUT",
                    field="feed_organic_n_input_mg",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        "feed_organic_n_input_mg is required when "
                        "feeding is scheduled."
                    ),
                )
            )

        if (
            total_feed_nitrogen_metric is None
            or feed_organic_n_input_metric is None
        ):
            return ValidationResult(findings=tuple(findings))

        if not cls._is_valid_non_negative_value(
            total_feed_nitrogen_metric.value
        ):
            return ValidationResult(findings=tuple(findings))

        if not cls._is_valid_non_negative_value(
            feed_organic_n_input_metric.value
        ):
            return ValidationResult(findings=tuple(findings))

        difference_mg = abs(
            total_feed_nitrogen_metric.value
            - feed_organic_n_input_metric.value
        )

        if difference_mg > cls._TOLERANCE:
            findings.append(
                ValidationError(
                    code="FEED_NITROGEN_NOT_CONSERVED",
                    field="feed_organic_n_input_mg",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        "Total feed nitrogen must equal the sum of "
                        "all modelled feed nitrogen output paths."
                    ),
                )
            )

        return ValidationResult(findings=tuple(findings))

    @staticmethod
    def _find_latest_metric(
        *,
        context: StepContext,
        metric_name: str,
    ) -> DailyMetric | None:
        return next(
            (
                metric
                for metric in reversed(context.metrics)
                if metric.name == metric_name
            ),
            None,
        )

    @staticmethod
    def _validate_metric_value(
        *,
        metric: DailyMetric | None,
        findings: list[ValidationError],
    ) -> None:
        if metric is None:
            return

        if not isfinite(metric.value):
            findings.append(
                ValidationError(
                    code="NON_FINITE_FEED_NITROGEN_METRIC",
                    field=metric.name,
                    severity=ValidationSeverity.ERROR,
                    message=f"{metric.name} must be a finite number.",
                )
            )
        elif metric.value < 0.0:
            findings.append(
                ValidationError(
                    code="NEGATIVE_FEED_NITROGEN_METRIC",
                    field=metric.name,
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"{metric.name} must be greater than or "
                        "equal to zero."
                    ),
                )
            )

    @staticmethod
    def _is_valid_non_negative_value(value: float) -> bool:
        return isfinite(value) and value >= 0.0