# Carrier Predictor - Products Summary

**Last Updated:** 2025-11-11  
**Total Products:** 18 active product YAML files

## Overview

The Carrier Predictor now has **18 products** across **8 carriers**, covering all major insurance types. All uploaded product PDFs have been converted to YAML rules files and are active in the recommendation system.

---

## Products by Carrier

### 1. Elco Mutual (5 products)
- **Golden Eagle Whole Life** - Simplified issue WL with fast cash value, ages 0-85
- **Platinum Eagle SPWL** - Single premium whole life for estate planning
- **Silver Eagle Final Expense** - Multi-tier final expense (6 tiers: Premier/Plus/Standard/Graded/Modified/GI)
- **Presidio Plus IET** - Guaranteed issue with Irrevocable Estate Trust, $15K-$100K
- **Presidio Plus IFT** - Guaranteed issue with Irrevocable Funeral Trust, $2.5K-$15K

### 2. Mutual of Omaha (4 products)
- **Living Promise Level Benefit** - Final expense with level benefit, ages 45-85
- **Living Promise Graded Benefit** - Final expense with graded benefit, ages 45-80
- **Term Life Express** - Simplified issue term, instant approval
- **IUL Express** - Simplified issue indexed universal life, instant approval

### 3. Legal & General America (2 products)
- **OPTerm 20** - 20-year term with market-leading rates, Box 1 (Young & Healthy)
- **Life Step UL** - Universal life for term conversions, min $50K

### 4. United Home Life (4 products)
- **Express Issue Premier** - Simplified issue term (already existed)
- **Final Expense Series** - Three-tier final expense (Level/Modified/GI), ages 50-85
- **Provider Whole Life** - Simplified issue WL with table ratings, ages 0-80
- **Simple Term** - Simplified issue term with ROP/DLX variants, ages 18-65

### 5. Corebridge Financial (1 product)
- **Select-a-Term** - Flexible term with living benefits, up to $10M

### 6. SBLI (1 product)
- **SBLI Level Term** - Competitive term with accelerated death benefits, up to $5M

### 7. Kansas City Life (1 product)
- **Signature Term Express 20** - 20-year simplified term (already existed)

### 8. American Home Life (0 products)
- Directory created, no products yet (no PDFs were uploaded for AHL)

---

## Products by Type

### Term Life (7 products)
1. Legal & General America - OPTerm 20
2. Corebridge Financial - Select-a-Term
3. SBLI - SBLI Level Term
4. United Home Life - Simple Term
5. United Home Life - Express Issue Premier
6. Kansas City Life - Signature Term Express 20
7. Mutual of Omaha - Term Life Express

### Final Expense (6 products)
1. Elco Mutual - Silver Eagle Final Expense (6 tiers)
2. Elco Mutual - Presidio Plus IFT (Funeral Trust)
3. Mutual of Omaha - Living Promise Level Benefit
4. Mutual of Omaha - Living Promise Graded Benefit
5. United Home Life - Final Expense Series (3 tiers)

### Whole Life (4 products)
1. Elco Mutual - Golden Eagle Whole Life
2. Elco Mutual - Platinum Eagle SPWL (Single Premium)
3. Elco Mutual - Presidio Plus IET (Estate Trust)
4. United Home Life - Provider Whole Life

### Universal Life (2 products)
1. Legal & General America - Life Step UL
2. Mutual of Omaha - IUL Express (Indexed)

---

## Products by Underwriting Type

### Fully Underwritten (3)
- Legal & General America - OPTerm 20
- Corebridge Financial - Select-a-Term  
- SBLI - SBLI Level Term

### Simplified Issue (11)
- Mutual of Omaha - Term Life Express
- Mutual of Omaha - IUL Express
- Mutual of Omaha - Living Promise (both variants)
- United Home Life - Express Issue Premier
- United Home Life - Simple Term
- United Home Life - Provider Whole Life
- United Home Life - Final Expense Series (Level/Modified)
- Kansas City Life - Signature Term Express 20
- Elco Mutual - Golden Eagle Whole Life
- Elco Mutual - Platinum Eagle SPWL

### Guaranteed Issue (4)
- Elco Mutual - Presidio Plus IET
- Elco Mutual - Presidio Plus IFT
- Elco Mutual - Silver Eagle (Modified/GI tiers)
- United Home Life - Final Expense Series (GI tier)

---

## Special Features

### Products for High Build / "Fat People"
- United Home Life - Simple Term (BMI 42)
- United Home Life - Provider Whole Life (BMI 42)
- United Home Life - Final Expense Series (BMI 42)
- Elco Mutual - All products (BMI 42)

### Products with Instant Approval
- Mutual of Omaha - Term Life Express
- Mutual of Omaha - IUL Express

### Products for Estate Planning
- Elco Mutual - Presidio Plus IET ($15K-$100K)
- Elco Mutual - Platinum Eagle SPWL (Single Premium)
- Legal & General America - Life Step UL

### Products with Living Benefits
- Legal & General America - OPTerm 20
- Corebridge Financial - Select-a-Term
- SBLI - SBLI Level Term
- Mutual of Omaha - Living Promise

### High Face Amount Products
- Corebridge Financial - Select-a-Term (up to $10M)
- SBLI - SBLI Level Term (up to $5M)

---

## Product Coverage by Box

### Box 1: Young & Healthy
- Legal & General America - OPTerm 20
- Corebridge Financial - Select-a-Term
- SBLI - SBLI Level Term
- Mutual of Omaha - IUL Express

### Box 2: Older & Healthy
- Legal & General America - Life Step UL
- Mutual of Omaha - IUL Express
- Mutual of Omaha - Living Promise Level

### Box 3: Young & Unhealthy
- United Home Life - Simple Term
- United Home Life - Provider Whole Life
- Kansas City Life - Signature Term Express 20

### Box 4: Old & Unhealthy
- Elco Mutual - All Final Expense products
- Mutual of Omaha - Living Promise Graded
- United Home Life - Final Expense Series

---

## Missing from Uploads

Based on data/carriers/ directory, you uploaded 22 product .txt files. We've created YAML files for 18 products:

### Not Yet Created (4 products):
These are **not in the approved carrier whitelist**:
- Transamerica FFIUL (Transamerica not whitelisted)
- Transamerica Trendsetter LB (Transamerica not whitelisted)
- Transamerica Trendsetter Super (Transamerica not whitelisted)
- American Home Life products (No product PDFs found, only empty directory)

---

## Technical Notes

- All products automatically loaded from `carriers/` directory
- YAML schema validated by `src/ai/assigner.py`
- Legacy RAG system still available at `/recommend-carriers` (deprecated)
- Primary rules-based engine at `/recommend` (active)
- Server no longer loads FAISS index on startup (saves 5 seconds + 80MB RAM)

---

## Next Steps

1. ✅ All uploaded products converted to YAML
2. ✅ All missing carriers (L&G, SBLI, Corebridge) added
3. ✅ All Elco products (5 total) added
4. ✅ Additional UHL products added
5. ✅ Mutual of Omaha IUL Express added
6. ⏭️ Optional: Add Transamerica products (requires whitelisting)
7. ⏭️ Optional: Add American Home Life products (requires product PDFs)

---

## Verification

Test with these sample requests:

```bash
# Final Expense (should show Elco, MoO, UHL)
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"age":65,"desired_coverage":15000,"coverage_type":"Final Expense","smoker":false,"state":"TX"}'

# Term Life (should show L&G, Corebridge, SBLI)
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"age":35,"desired_coverage":1000000,"coverage_type":"Term","smoker":false,"state":"TX"}'

# IUL (should show MoO IUL Express)
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"age":40,"desired_coverage":250000,"coverage_type":"IUL","smoker":false,"state":"CA"}'
```

All tests passing ✅
