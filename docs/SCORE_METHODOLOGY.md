# Scoring Methodology v1.0.0

## Overall Score (0-100)
Weighted average of 4 sub-scores:
- Privacy: 40%
- Transparency: 30%
- Resources: 15%
- Design: 15%

## Privacy Score (0-100)
Base: 100 points

Deductions:
- Trackers: -5 per tracker (max -40)
- Dangerous permissions: -3 per permission (max -20)
- Sells data: -20
- Cross-app tracking: -15
- Cannot delete account: -10

Bonuses:
- Open source: +10
- End-to-end encryption: +10

## Transparency Score (0-100)
Base: 50 points

Bonuses:
- Has privacy policy: +15
- Policy clarity (0-10): +15
- Open source: +15
- Published security audit: +10
- Can delete account: +10

Deductions:
- No privacy policy: -20
- Vague policy: -10

## Resource Score (0-100)
Base: 75 points

Deductions based on review sentiment:
- Battery drain mentions: -2 per 1% of reviews
- Crash mentions: -2 per 1% of reviews
- Slow/lag mentions: -1 per 1% of reviews

## Design Score (0-100)
[To be implemented - dark patterns]
Default: 50 points for now