#!/usr/bin/env python3
"""Deterministic arithmetic for early-stage intellectual-property valuation.

Implements transparent calculations used by the WIPO 2025 valuation workflow:
discounted cash flow, probability-adjusted NPV, adjusted market comparables,
and weighted triangulation.  It does not choose assumptions or issue a legal,
tax, accounting, fairness, or transaction opinion. Stdlib only. Python 3.9+.
"""

import argparse
import json
import statistics
import sys


def numbers(value):
    try:
        return [float(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as exc:
        raise ValueError("values must be comma-separated numbers") from exc


def discounted(cashflows, rate, terminal=0.0):
    if rate <= -1:
        raise ValueError("discount rate must be greater than -1")
    pv_flows = [amount / ((1.0 + rate) ** year) for year, amount in enumerate(cashflows, 1)]
    pv_terminal = terminal / ((1.0 + rate) ** len(cashflows)) if cashflows else terminal
    return {
        "present_value": sum(pv_flows) + pv_terminal,
        "pv_cashflows": pv_flows,
        "pv_terminal": pv_terminal,
    }


def risk_adjusted(cashflows, probabilities, rate):
    if len(cashflows) != len(probabilities):
        raise ValueError("cashflows and occurrence probabilities must have equal length")
    if any(p < 0 or p > 1 for p in probabilities):
        raise ValueError("occurrence probabilities must be between 0 and 1")
    adjusted = [amount * probability for amount, probability in zip(cashflows, probabilities)]
    result = discounted(adjusted, rate)
    result["risk_adjusted_cashflows"] = adjusted
    return result


def market_comparables(comparables, factors):
    if len(comparables) != len(factors):
        raise ValueError("comparables and adjustment factors must have equal length")
    if not comparables:
        raise ValueError("at least one comparable is required")
    adjusted = [value * factor for value, factor in zip(comparables, factors)]
    return {
        "adjusted_comparables": adjusted,
        "low": min(adjusted),
        "median": statistics.median(adjusted),
        "high": max(adjusted),
    }


def triangulate(estimates, weights):
    if len(estimates) != len(weights) or not estimates:
        raise ValueError("estimates and weights must be non-empty and have equal length")
    if any(weight < 0 for weight in weights) or sum(weights) <= 0:
        raise ValueError("weights must be non-negative and sum to more than zero")
    normalized = [weight / sum(weights) for weight in weights]
    return {
        "estimate": sum(value * weight for value, weight in zip(estimates, normalized)),
        "low": min(estimates),
        "high": max(estimates),
        "normalized_weights": normalized,
    }


def rounded(value):
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, list):
        return [rounded(item) for item in value]
    if isinstance(value, dict):
        return {key: rounded(item) for key, item in value.items()}
    return value


def render(result, as_json):
    result = rounded(result)
    if as_json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return
    for key, value in result.items():
        if isinstance(value, list):
            print("%s: %s" % (key, ", ".join("%.6g" % item for item in value)))
        elif isinstance(value, float):
            print("%s: %.6f" % (key, value))
        else:
            print("%s: %s" % (key, value))


def selftest():
    dcf = discounted([110, 121], 0.10)
    assert abs(dcf["present_value"] - 200.0) < 1e-9
    risk = risk_adjusted([-10, -20, 100], [1.0, 0.5, 0.25], 0.0)
    assert abs(risk["present_value"] - 5.0) < 1e-9
    market = market_comparables([100, 120, 140], [1.0, 0.9, 0.8])
    assert market["adjusted_comparables"] == [100.0, 108.0, 112.0]
    assert market["median"] == 108.0
    combined = triangulate([50, 100, 150], [0.2, 0.3, 0.5])
    assert abs(combined["estimate"] - 115.0) < 1e-9
    assert combined["low"] == 50 and combined["high"] == 150
    try:
        risk_adjusted([1], [1.2], 0.1)
        raise AssertionError("invalid probability accepted")
    except ValueError:
        pass
    print("OK: IP valuation selftest passed")


def parser():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true", help="run deterministic built-in checks")
    sub = ap.add_subparsers(dest="command")

    income = sub.add_parser("income", help="discount annual cash flows and an optional terminal value")
    income.add_argument("--cashflows", required=True, help="comma-separated annual cash flows, years 1..N")
    income.add_argument("--discount-rate", required=True, type=float, help="decimal rate, for example 0.18")
    income.add_argument("--terminal-value", type=float, default=0.0)
    income.add_argument("--json", action="store_true")

    rnpv = sub.add_parser("rnpv", help="discount cash flows weighted by their unconditional occurrence probabilities")
    rnpv.add_argument("--cashflows", required=True)
    rnpv.add_argument("--probabilities", required=True, help="unconditional probability for each corresponding cash flow")
    rnpv.add_argument("--discount-rate", required=True, type=float)
    rnpv.add_argument("--json", action="store_true")

    market = sub.add_parser("market", help="adjust comparable transaction values and report a range")
    market.add_argument("--comparables", required=True)
    market.add_argument("--factors", required=True, help="multiplicative comparability factors")
    market.add_argument("--json", action="store_true")

    tri = sub.add_parser("triangulate", help="combine approach estimates with explicit normalized weights")
    tri.add_argument("--estimates", required=True)
    tri.add_argument("--weights", required=True)
    tri.add_argument("--json", action="store_true")
    return ap


def main():
    ap = parser()
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0
    try:
        if args.command == "income":
            result = discounted(numbers(args.cashflows), args.discount_rate, args.terminal_value)
        elif args.command == "rnpv":
            result = risk_adjusted(numbers(args.cashflows), numbers(args.probabilities), args.discount_rate)
        elif args.command == "market":
            result = market_comparables(numbers(args.comparables), numbers(args.factors))
        elif args.command == "triangulate":
            result = triangulate(numbers(args.estimates), numbers(args.weights))
        else:
            ap.print_help()
            return 0
        render(result, args.json)
        return 0
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
