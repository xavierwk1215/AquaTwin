"""Validation for daily nitrogen mass balance."""

from math import isfinite

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext
from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)
from aquatwin.validation.validation_result import ValidationResult


class NitrogenMassBalanceValidator:
    """Validate conservation of total nitrogen across one simulation day."""

    _ABSOLUTE_TOLERANCE_MG = 1e-9
    _RELATIVE_TOLERANCE = 1e-9

    _INPUT_METRIC_NAMES = (
        "source_water_n_input_mg",
        "feed_organic_n_input_mg",
        "metabolic_tan_input_mg",
    )

    _REMOVAL_METRIC_NAMES = (
        "water_change_n_removal_mg",
        "maintenance_n_removal_mg",
    )

    @classmethod
    def validate(
        cls,
        context: StepContext,
    ) -> ValidationResult:
        """Return validation findings for daily nitrogen conservation."""
        findings: list[ValidationError] = []

        opening_total_n_mg = cls._total_state_nitrogen_mg(
            organic_n_mass_mg=(
                context.previous_state.organic_n_mass_mg
            ),
            tan_mass_mg=context.previous_state.tan_mass_mg,
            nitrite_mass_mg=(
                context.previous_state.nitrite_mass_mg
            ),
            nitrate_mass_mg=(
                context.previous_state.nitrate_mass_mg
            ),
        )

        closing_total_n_mg = cls._total_state_nitrogen_mg(
            organic_n_mass_mg=(
                context.working_state.organic_n_mass_mg
            ),
            tan_mass_mg=context.working_state.tan_mass_mg,
            nitrite_mass_mg=(
                context.working_state.nitrite_mass_mg
            ),
            nitrate_mass_mg=(
                context.working_state.nitrate_mass_mg
            ),
        )

        cls._validate_total(
            field="opening_total_n_mg",
            value=opening_total_n_mg,
            findings=findings,
        )
        cls._validate_total(
            field="closing_total_n_mg",
            value=closing_total_n_mg,
            findings=findings,
        )

        external_input_n_mg = cls._sum_latest_metrics(
            context=context,
            metric_names=cls._INPUT_METRIC_NAMES,
            findings=findings,
        )

        external_removal_n_mg = cls._sum_latest_metrics(
            context=context,
            metric_names=cls._REMOVAL_METRIC_NAMES,
            findings=findings,
        )

        values = (
            opening_total_n_mg,
            closing_total_n_mg,
            external_input_n_mg,
            external_removal_n_mg,
        )

        if not all(isfinite(value) and value >= 0.0 for value in values):
            return ValidationResult(findings=tuple(findings))

        expected_closing_total_n_mg = (
            opening_total_n_mg
            + external_input_n_mg
            - external_removal_n_mg
        )

        balance_error_mg = (
            closing_total_n_mg
            - expected_closing_total_n_mg
        )

        tolerance_mg = max(
            cls._ABSOLUTE_TOLERANCE_MG,
            abs(expected_closing_total_n_mg)
            * cls._RELATIVE_TOLERANCE,
        )

        if abs(balance_error_mg) > tolerance_mg:
            findings.append(
                ValidationError(
                    code="NITROGEN_MASS_BALANCE_VIOLATION",
                    field="closing_total_n_mg",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        "Closing total nitrogen must equal opening "
                        "nitrogen plus external inputs minus external "
                        "removals within the configured tolerance."
                    ),
                )
            )

        return ValidationResult(findings=tuple(findings))

    @staticmethod
    def _total_state_nitrogen_mg(
        *,
        organic_n_mass_mg: float,
        tan_mass_mg: float,
        nitrite_mass_mg: float,
        nitrate_mass_mg: float,
    ) -> float:
        return (
            organic_n_mass_mg
            + tan_mass_mg
            + nitrite_mass_mg
            + nitrate_mass_mg
        )

    @classmethod
    def _sum_latest_metrics(
        cls,
        *,
        context: StepContext,
        metric_names: tuple[str, ...],
        findings: list[ValidationError],
    ) -> float:
        total_mg = 0.0

        for metric_name in metric_names:
            metric = cls._find_latest_metric(
                context=context,
                metric_name=metric_name,
            )

            if metric is None:
                continue

            cls._validate_metric(
                metric=metric,
                findings=findings,
            )

            total_mg += metric.value

        return total_mg

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
    def _validate_metric(
        *,
        metric: DailyMetric,
        findings: list[ValidationError],
    ) -> None:
        if not isfinite(metric.value):
            findings.append(
                ValidationError(
                    code="NON_FINITE_MASS_BALANCE_METRIC",
                    field=metric.name,
                    severity=ValidationSeverity.ERROR,
                    message=f"{metric.name} must be a finite number.",
                )
            )
        elif metric.value < 0.0:
            findings.append(
                ValidationError(
                    code="NEGATIVE_MASS_BALANCE_METRIC",
                    field=metric.name,
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"{metric.name} must be greater than or "
                        "equal to zero."
                    ),
                )
            )

    @staticmethod
    def _validate_total(
        *,
        field: str,
        value: float,
        findings: list[ValidationError],
    ) -> None:
        if not isfinite(value):
            findings.append(
                ValidationError(
                    code="NON_FINITE_TOTAL_NITROGEN",
                    field=field,
                    severity=ValidationSeverity.ERROR,
                    message=f"{field} must be a finite number.",
                )
            )
        elif value < 0.0:
            findings.append(
                ValidationError(
                    code="NEGATIVE_TOTAL_NITROGEN",
                    field=field,
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"{field} must be greater than or equal to zero."
                    ),
                )
            )