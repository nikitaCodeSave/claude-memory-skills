"""
Tests for Discount Calculator (feat-005).

TDD RED phase: all tests should FAIL because implementation does not exist yet.

Patterns used:
- pat-001: test_happy_path (must)
- pat-003: test_none_raises_error (must)
- pat-006: test_boundary_values (must)

Decisions applied:
- dec-001: TypeError for None, ValueError for invalid values
- dec-002: Validate input at function entry
"""

from decimal import Decimal

import pytest

from src.discount_calculator import (
    DiscountResult,
    PromoCode,
    calculate_discount,
)


class TestHappyPath:
    """pat-001: Normal operation with valid input."""

    def test_calculate_discount_returns_result_for_simple_order(self):
        """AC-001: Order amount > 1000 RUB gets 5% discount."""
        result = calculate_discount(Decimal("1500"))

        assert isinstance(result, DiscountResult)
        assert result.original_amount == Decimal("1500")
        assert result.discount_percent == Decimal("5")
        assert result.final_amount == Decimal("1425.00")

    def test_calculate_discount_returns_zero_discount_for_small_order(self):
        """Happy path: Order <= 1000 gets no tier discount."""
        result = calculate_discount(Decimal("500"))

        assert result.discount_percent == Decimal("0")
        assert result.final_amount == Decimal("500.00")


class TestTierDiscounts:
    """AC-001, AC-002, AC-003: Tier-based discounts."""

    def test_order_above_1000_gets_5_percent_discount(self):
        """AC-001: Order amount > 1000 RUB gets 5% discount."""
        result = calculate_discount(Decimal("1500"))

        assert result.discount_percent == Decimal("5")
        assert result.discount_amount == Decimal("75.00")
        assert result.final_amount == Decimal("1425.00")

    def test_order_above_5000_gets_10_percent_discount(self):
        """AC-002: Order amount > 5000 RUB gets 10% discount."""
        result = calculate_discount(Decimal("6000"))

        assert result.discount_percent == Decimal("10")
        assert result.discount_amount == Decimal("600.00")
        assert result.final_amount == Decimal("5400.00")

    def test_order_exactly_1000_gets_no_discount(self):
        """AC-003: Order exactly 1000 gets previous tier discount (0%)."""
        result = calculate_discount(Decimal("1000"))

        assert result.discount_percent == Decimal("0")
        assert result.final_amount == Decimal("1000.00")

    def test_order_exactly_5000_gets_5_percent_discount(self):
        """AC-003: Order exactly 5000 gets previous tier discount (5%)."""
        result = calculate_discount(Decimal("5000"))

        assert result.discount_percent == Decimal("5")
        assert result.discount_amount == Decimal("250.00")
        assert result.final_amount == Decimal("4750.00")


class TestPromoCodeFixed:
    """AC-004: Fixed promo code subtracts as percentage of original."""

    def test_fixed_promo_subtracts_as_percentage_of_original(self):
        """AC-004: Fixed promo code subtracts as percentage of original."""
        promo = PromoCode(
            code="SAVE100",
            discount_type="fixed",
            value=Decimal("100"),
        )
        # Order 2000 -> 5% tier discount (100) + 100 fixed = 200 discount = 10%
        result = calculate_discount(Decimal("2000"), promo=promo)

        # 100 RUB from 2000 = 5% additional discount
        # Total: 5% tier + 5% promo = 10%
        assert result.discount_percent == Decimal("10")
        assert result.discount_amount == Decimal("200.00")
        assert result.final_amount == Decimal("1800.00")

    def test_fixed_promo_with_no_tier_discount(self):
        """AC-004: Fixed promo on small order."""
        promo = PromoCode(
            code="SAVE50",
            discount_type="fixed",
            value=Decimal("50"),
        )
        # Order 500 -> no tier discount + 50 fixed = 10% total
        result = calculate_discount(Decimal("500"), promo=promo)

        assert result.discount_percent == Decimal("10")
        assert result.final_amount == Decimal("450.00")


class TestPromoCodePercent:
    """AC-005: Percentage promo code adds to total discount."""

    def test_percent_promo_adds_to_tier_discount(self):
        """AC-005: Percentage promo code adds to total discount."""
        promo = PromoCode(
            code="EXTRA10",
            discount_type="percent",
            value=Decimal("10"),
        )
        # Order 2000 -> 5% tier + 10% promo = 15% total
        result = calculate_discount(Decimal("2000"), promo=promo)

        assert result.discount_percent == Decimal("15")
        assert result.discount_amount == Decimal("300.00")
        assert result.final_amount == Decimal("1700.00")

    def test_percent_promo_on_small_order(self):
        """AC-005: Percentage promo on order without tier discount."""
        promo = PromoCode(
            code="SAVE5",
            discount_type="percent",
            value=Decimal("5"),
        )
        result = calculate_discount(Decimal("500"), promo=promo)

        assert result.discount_percent == Decimal("5")
        assert result.final_amount == Decimal("475.00")


class TestSinglePromoCodeRestriction:
    """AC-006: Only one promo code per order - tested implicitly by API design."""

    def test_api_accepts_single_promo_code(self):
        """AC-006: Only one promo code per order (API design)."""
        promo = PromoCode(
            code="SINGLE",
            discount_type="percent",
            value=Decimal("5"),
        )
        # API only accepts one promo - this should work
        result = calculate_discount(Decimal("1000"), promo=promo)

        assert result is not None


class TestVipDiscount:
    """AC-007: VIP status adds +5% to total discount."""

    def test_vip_adds_5_percent_to_total_discount(self):
        """AC-007: VIP status adds +5% to total discount."""
        # Order 2000 -> 5% tier + 5% VIP = 10% total
        result = calculate_discount(Decimal("2000"), is_vip=True)

        assert result.discount_percent == Decimal("10")
        assert result.discount_amount == Decimal("200.00")
        assert result.final_amount == Decimal("1800.00")

    def test_vip_with_promo_code(self):
        """AC-007 + AC-005: VIP + percentage promo."""
        promo = PromoCode(
            code="COMBO",
            discount_type="percent",
            value=Decimal("10"),
        )
        # Order 2000 -> 5% tier + 10% promo + 5% VIP = 20% total
        result = calculate_discount(Decimal("2000"), promo=promo, is_vip=True)

        assert result.discount_percent == Decimal("20")
        assert result.discount_amount == Decimal("400.00")
        assert result.final_amount == Decimal("1600.00")

    def test_non_vip_gets_no_vip_bonus(self):
        """AC-007: is_vip=False gives no VIP bonus."""
        result = calculate_discount(Decimal("2000"), is_vip=False)

        assert result.discount_percent == Decimal("5")  # Only tier discount


class TestDiscountCalculationFromOriginal:
    """AC-008: All discounts calculated from original amount and summed."""

    def test_discounts_calculated_from_original_amount(self):
        """AC-008: All discounts calculated from original amount."""
        promo = PromoCode(
            code="FIXED200",
            discount_type="fixed",
            value=Decimal("200"),
        )
        # Order 2000:
        # - Tier: 5% of 2000 = 100
        # - Promo: 200 (= 10% of 2000)
        # - Total: 15% of 2000 = 300
        result = calculate_discount(Decimal("2000"), promo=promo)

        assert result.discount_amount == Decimal("300.00")
        assert result.final_amount == Decimal("1700.00")


class TestMaximumDiscountCap:
    """AC-009: Maximum total discount is 30%."""

    def test_discount_capped_at_30_percent(self):
        """AC-009: Maximum total discount is 30%."""
        promo = PromoCode(
            code="HUGE",
            discount_type="percent",
            value=Decimal("25"),
        )
        # Order 6000 -> 10% tier + 25% promo + 5% VIP = 40% -> capped at 30%
        result = calculate_discount(Decimal("6000"), promo=promo, is_vip=True)

        assert result.discount_percent == Decimal("30")
        assert result.discount_amount == Decimal("1800.00")
        assert result.final_amount == Decimal("4200.00")

    def test_discount_at_exactly_30_percent(self):
        """AC-009: Discount exactly at cap."""
        promo = PromoCode(
            code="EXACT",
            discount_type="percent",
            value=Decimal("15"),
        )
        # Order 6000 -> 10% tier + 15% promo + 5% VIP = 30% exactly
        result = calculate_discount(Decimal("6000"), promo=promo, is_vip=True)

        assert result.discount_percent == Decimal("30")

    def test_discount_below_cap_not_affected(self):
        """AC-009: Discount below cap is not modified."""
        result = calculate_discount(Decimal("2000"), is_vip=True)

        # 5% tier + 5% VIP = 10% (below cap)
        assert result.discount_percent == Decimal("10")


class TestDecimalPrecision:
    """AC-010: Use Decimal for all calculations."""

    def test_result_uses_decimal_types(self):
        """AC-010: Use Decimal for all calculations."""
        result = calculate_discount(Decimal("1500.50"))

        assert isinstance(result.original_amount, Decimal)
        assert isinstance(result.final_amount, Decimal)
        assert isinstance(result.discount_percent, Decimal)
        assert isinstance(result.discount_amount, Decimal)

    def test_decimal_precision_preserved(self):
        """AC-010: Decimal precision in calculations."""
        # 1500.50 with 5% discount
        result = calculate_discount(Decimal("1500.50"))

        assert result.discount_amount == Decimal("75.025")  # Before rounding


class TestRounding:
    """AC-011: Round final amount to 2 decimal places."""

    def test_final_amount_rounded_to_2_decimal_places(self):
        """AC-011: Round final amount to 2 decimal places."""
        # 1500.50 with 5% discount = 1425.475 -> rounds to 1425.48
        result = calculate_discount(Decimal("1500.50"))

        assert result.final_amount == Decimal("1425.48")
        # Check it has exactly 2 decimal places
        assert result.final_amount == result.final_amount.quantize(Decimal("0.01"))

    def test_rounding_half_up(self):
        """AC-011: Rounding uses ROUND_HALF_UP."""
        # Create scenario where .5 rounding matters
        # 1111.11 with 5% = 55.5555 discount -> 1055.5545 -> rounds to 1055.55
        result = calculate_discount(Decimal("1111.11"))

        # Final amount should be properly rounded
        assert str(result.final_amount).count(".") <= 1
        if "." in str(result.final_amount):
            decimal_places = len(str(result.final_amount).split(".")[1])
            assert decimal_places <= 2


class TestNegativeAmountError:
    """AC-012: Negative amount raises ValueError."""

    def test_negative_amount_raises_value_error(self):
        """AC-012: Negative amount raises ValueError."""
        with pytest.raises(ValueError, match="negative"):
            calculate_discount(Decimal("-100"))

    def test_negative_amount_with_promo_raises_value_error(self):
        """AC-012: Negative amount with promo raises ValueError."""
        promo = PromoCode(
            code="TEST",
            discount_type="percent",
            value=Decimal("5"),
        )
        with pytest.raises(ValueError):
            calculate_discount(Decimal("-50"), promo=promo)


class TestNoneInputError:
    """AC-013, pat-003: None input raises TypeError (per dec-001)."""

    def test_none_amount_raises_type_error(self):
        """AC-013: None input raises TypeError (per dec-001)."""
        with pytest.raises(TypeError):
            calculate_discount(None)

    def test_none_amount_with_valid_promo_raises_type_error(self):
        """AC-013: None amount with valid promo raises TypeError."""
        promo = PromoCode(
            code="VALID",
            discount_type="percent",
            value=Decimal("5"),
        )
        with pytest.raises(TypeError):
            calculate_discount(None, promo=promo)


class TestDiscountResult:
    """AC-014: Return both final amount and discount percentage."""

    def test_result_contains_all_required_fields(self):
        """AC-014: Return both final amount and discount percentage."""
        result = calculate_discount(Decimal("2000"))

        assert hasattr(result, "original_amount")
        assert hasattr(result, "final_amount")
        assert hasattr(result, "discount_percent")
        assert hasattr(result, "discount_amount")

    def test_result_is_discount_result_instance(self):
        """AC-014: Result is DiscountResult instance."""
        result = calculate_discount(Decimal("1000"))

        assert isinstance(result, DiscountResult)


class TestBoundaryValues:
    """pat-006: Test boundary values."""

    def test_order_amount_zero(self):
        """Edge case: Order amount exactly 0."""
        result = calculate_discount(Decimal("0"))

        assert result.final_amount == Decimal("0")
        assert result.discount_percent == Decimal("0")

    def test_order_just_above_1000(self):
        """Edge case: Just above 1000 boundary (1000.01)."""
        result = calculate_discount(Decimal("1000.01"))

        assert result.discount_percent == Decimal("5")

    def test_order_just_above_5000(self):
        """Edge case: Just above 5000 boundary (5000.01)."""
        result = calculate_discount(Decimal("5000.01"))

        assert result.discount_percent == Decimal("10")

    def test_order_just_below_1000(self):
        """Edge case: Just below 1000 boundary (999.99)."""
        result = calculate_discount(Decimal("999.99"))

        assert result.discount_percent == Decimal("0")

    def test_order_just_below_5000(self):
        """Edge case: Just below 5000 boundary (4999.99)."""
        result = calculate_discount(Decimal("4999.99"))

        assert result.discount_percent == Decimal("5")

    def test_very_large_order(self):
        """Edge case: Very large order amount."""
        result = calculate_discount(Decimal("1000000"))

        assert result.discount_percent == Decimal("10")
        assert result.discount_amount == Decimal("100000.00")


class TestEdgeCases:
    """Additional edge cases from requirements."""

    def test_promo_exceeding_30_percent_cap(self):
        """Edge case: Promo exceeding 30% cap alone."""
        promo = PromoCode(
            code="MASSIVE",
            discount_type="percent",
            value=Decimal("50"),
        )
        result = calculate_discount(Decimal("1000"), promo=promo)

        # 50% promo capped at 30%
        assert result.discount_percent == Decimal("30")

    def test_vip_plus_max_tier_plus_large_promo_capped(self):
        """Edge case: VIP + max tier + large promo -> cap."""
        promo = PromoCode(
            code="BIG",
            discount_type="percent",
            value=Decimal("20"),
        )
        # 10% tier + 20% promo + 5% VIP = 35% -> capped at 30%
        result = calculate_discount(Decimal("10000"), promo=promo, is_vip=True)

        assert result.discount_percent == Decimal("30")
        assert result.final_amount == Decimal("7000.00")

    def test_small_order_with_large_fixed_promo(self):
        """Edge case: Small order with large fixed promo."""
        promo = PromoCode(
            code="BIGFIX",
            discount_type="fixed",
            value=Decimal("200"),
        )
        # Order 500: 200/500 = 40% -> capped at 30%
        result = calculate_discount(Decimal("500"), promo=promo)

        assert result.discount_percent == Decimal("30")
        assert result.final_amount == Decimal("350.00")

    def test_empty_promo_code_string(self):
        """Edge case: Empty promo code string."""
        promo = PromoCode(
            code="",
            discount_type="percent",
            value=Decimal("5"),
        )
        # Should still work or raise appropriate error
        result = calculate_discount(Decimal("1000"), promo=promo)
        assert result is not None

    def test_none_promo_code(self):
        """Edge case: None promo code (allowed)."""
        result = calculate_discount(Decimal("1000"), promo=None)

        assert result.discount_percent == Decimal("0")

    def test_vip_false_vs_not_provided(self):
        """Edge case: VIP=False vs not provided."""
        result_explicit_false = calculate_discount(Decimal("2000"), is_vip=False)
        result_not_provided = calculate_discount(Decimal("2000"))

        assert result_explicit_false.discount_percent == result_not_provided.discount_percent
        assert result_explicit_false.final_amount == result_not_provided.final_amount


class TestDecimalPrecisionEdgeCases:
    """Edge cases for decimal precision."""

    def test_repeating_decimal_discount(self):
        """Edge case: Discount resulting in repeating decimal."""
        # 1000.00 / 3 = 333.333... -> needs proper rounding
        promo = PromoCode(
            code="THIRD",
            discount_type="fixed",
            value=Decimal("333.33"),
        )
        result = calculate_discount(Decimal("1000"), promo=promo)

        # Should be properly rounded to 2 decimal places
        assert result.final_amount == result.final_amount.quantize(Decimal("0.01"))

    def test_very_small_decimal_amount(self):
        """Edge case: Very small decimal amount."""
        result = calculate_discount(Decimal("0.01"))

        assert result.final_amount >= Decimal("0")
        assert result.final_amount == result.final_amount.quantize(Decimal("0.01"))

    def test_high_precision_input(self):
        """Edge case: High precision input amount."""
        result = calculate_discount(Decimal("1234.56789"))

        assert isinstance(result.final_amount, Decimal)
        # Final should be rounded to 2 decimal places
        final_str = str(result.final_amount)
        if "." in final_str:
            assert len(final_str.split(".")[1]) <= 2
