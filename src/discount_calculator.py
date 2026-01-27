"""
Discount Calculator module (feat-005).

Calculates order discounts based on:
- Order amount tiers (>1000 RUB: 5%, >5000 RUB: 10%)
- Promo codes (fixed or percentage)
- VIP status (+5%)

Maximum discount is capped at 30%.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

# Discount tier thresholds (RUB)
TIER_THRESHOLD_HIGH = Decimal("5000")
TIER_THRESHOLD_LOW = Decimal("1000")

# Discount percentages
TIER_DISCOUNT_HIGH = Decimal("10")
TIER_DISCOUNT_LOW = Decimal("5")
VIP_DISCOUNT = Decimal("5")
MAX_DISCOUNT = Decimal("30")
ZERO_DISCOUNT = Decimal("0")

# Promo code types
PromoType = Literal["fixed", "percent"]


@dataclass(frozen=True)
class PromoCode:
    """Promo code for order discount."""

    code: str
    discount_type: PromoType
    value: Decimal  # amount or percentage


@dataclass(frozen=True)
class DiscountResult:
    """Result of discount calculation."""

    original_amount: Decimal
    final_amount: Decimal
    discount_percent: Decimal
    discount_amount: Decimal


def _validate_order_amount(order_amount: Decimal) -> None:
    """Validate order amount (dec-001, dec-002)."""
    if order_amount is None:
        raise TypeError("order_amount cannot be None")
    if order_amount < 0:
        raise ValueError("order_amount cannot be negative")


def _calculate_tier_discount(order_amount: Decimal) -> Decimal:
    """Calculate tier-based discount percentage (AC-001, AC-002, AC-003)."""
    if order_amount > TIER_THRESHOLD_HIGH:
        return TIER_DISCOUNT_HIGH
    if order_amount > TIER_THRESHOLD_LOW:
        return TIER_DISCOUNT_LOW
    return ZERO_DISCOUNT


def _calculate_promo_discount(
    order_amount: Decimal, promo: PromoCode | None
) -> Decimal:
    """Calculate promo code discount percentage (AC-004, AC-005)."""
    if promo is None:
        return ZERO_DISCOUNT

    if promo.discount_type == "fixed":
        if order_amount > 0:
            return (promo.value / order_amount) * 100
        return ZERO_DISCOUNT

    # percent type
    return promo.value


def calculate_discount(
    order_amount: Decimal,
    promo: PromoCode | None = None,
    is_vip: bool = False,
) -> DiscountResult:
    """Calculate discount for an order.

    Args:
        order_amount: Original order amount in RUB
        promo: Optional promo code to apply
        is_vip: Whether customer has VIP status

    Returns:
        DiscountResult with original amount, final amount, and discount details

    Raises:
        TypeError: If order_amount is None
        ValueError: If order_amount is negative
    """
    _validate_order_amount(order_amount)

    # Calculate component discounts
    tier_percent = _calculate_tier_discount(order_amount)
    promo_percent = _calculate_promo_discount(order_amount, promo)
    vip_percent = VIP_DISCOUNT if is_vip else ZERO_DISCOUNT

    # Sum and cap at maximum (AC-008, AC-009)
    total_percent = min(tier_percent + promo_percent + vip_percent, MAX_DISCOUNT)

    # Calculate amounts (AC-010)
    discount_amount = order_amount * total_percent / 100
    final_amount = order_amount - discount_amount

    # Round final_amount to 2 decimal places (AC-011)
    final_amount = final_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return DiscountResult(
        original_amount=order_amount,
        final_amount=final_amount,
        discount_percent=total_percent,
        discount_amount=discount_amount,
    )
