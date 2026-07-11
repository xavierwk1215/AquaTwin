"""Validation for daily biofilter oxidation capacity."""

from math import isfinite

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext
from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)
from aquatwin.validation.validation_result import ValidationResult


class BiofilterCapacityValidator:
    """Validate TAN and nitrite oxidation against daily limits."""

    _TOLERANCE = 1e-9

    @classmethod
    def validate(
        cls,
        context: StepContext,
    ) -> ValidationResult:
        """Return validation findings for biofilter oxidation metrics."""
        findings: list[ValidationError] = []

        cls._validate_oxidation_path(
            context=context,
            substance_name="TAN",
            actual_metric_name="tan_n_oxidized_mg",
            potential_metric_name="potential_tan_n_oxidized_mg",
            capacity_metric_name="biofilter_tan_capacity_mg_day",
            findings=findings,
        )

        cls._validate_oxidation_path(
            context=context,
            substance_name="nitrite",
            actual_metric_name="nitrite_n_oxidized_mg",
            potential_metric_name=(
                "potential_nitrite_n_oxidized_mg"
            ),
            capacity_metric_name=(
                "biofilter_nitrite_capacity_mg_day"
            ),
            findings=findings,
        )

        return ValidationResult(findings=tuple(findings))

    @classmethod
    def _validate_oxidation_path(
        cls,
        *,
        context: StepContext,
        substance_name: str,
        actual_metric_name: str,
        potential_metric_name: str,
        capacity_metric_name: str,
        findings: list[ValidationError],
    ) -> None:
        actual_metric = cls._find_latest_metric(
            context=context,
            metric_name=actual_metric_name,
        )
        potential_metric = cls._find_latest_metric(
            context=context,
            metric_name=potential_metric_name,
        )
        capacity_metric = cls._find_latest_metric(
            context=context,
            metric_name=capacity_metric_name,
        )

        cls._validate_metric_value(
            metric=actual_metric,
            findings=findings,
        )
        cls._validate_metric_value(
            metric=potential_metric,
            findings=findings,
        )
        cls._validate_metric_value(
            metric=capacity_metric,
            findings=findings,
        )

        if actual_metric is None:
            return

        if not cls._is_valid_non_negative_value(actual_metric.value):
            return

        if (
            potential_metric is not None
            and cls._is_valid_non_negative_value(
                potential_metric.value
            )
            and actual_metric.value
            > potential_metric.value + cls._TOLERANCE
        ):
            findings.append(
                ValidationError(
                    code="OXIDATION_EXCEEDS_POTENTIAL",
                    field=actual_metric_name,
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"Actual {substance_name} oxidation must not "
                        "exceed potential oxidation."
                    ),
                )
            )

        if (
            capacity_metric is not None
            and cls._is_valid_non_negative_value(
                capacity_metric.value
            )
            and actual_metric.value
            > capacity_metric.value + cls._TOLERANCE
        ):
            findings.append(
                ValidationError(
                    code="OXIDATION_EXCEEDS_BIOFILTER_CAPACITY",
                    field=actual_metric_name,
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"Actual {substance_name} oxidation must not "
                        "exceed biofilter capacity."
                    ),
                )
            )

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
                    code="NON_FINITE_BIOFILTER_METRIC",
                    field=metric.name,
                    severity=ValidationSeverity.ERROR,
                    message=f"{metric.name} must be a finite number.",
                )
            )
        elif metric.value < 0.0:
            findings.append(
                ValidationError(
                    code="NEGATIVE_BIOFILTER_METRIC",
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