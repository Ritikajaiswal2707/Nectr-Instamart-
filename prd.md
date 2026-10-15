# Instamart × Nectr — Product Requirements Document

**Project type:** Product Management + Applied ML  
**Status:** Discovery and experiment design  
**Data status:** Synthetic portfolio dataset; findings require real-world validation.

## 1. Objective

Design and validate a low-effort product experience that increases first-time Nectr purchases among eligible Instamart users.

The initial hypothesis is to use a personalized "Premium for You" rail rather than immediately investing in a dedicated tab or standalone app.

The product decision has two parts:

1. Can historical shopping behaviour help prioritize users for Nectr discovery?
2. Does showing those users a personalized rail generate incremental first-time Nectr purchases without harming the core Instamart experience?

The first question is explored using synthetic data. The second requires a randomized experiment.

## 2. Background and problem framing

Nectr represents a premium grocery discovery proposition within a fast-delivery shopping experience. A broad launch could increase discovery, but it could also introduce visual clutter, fail to reach relevant users, or shift purchases away from existing products.

The product opportunity is to test a targeted discovery experience before committing to a larger surface.

### Synthetic analysis baseline

| Measure | Result |
|---|---:|
| Synthetic users | 6,000 |
| Cleaned orders | 24,834 |
| Eligible first-purchase cohort | 5,793 |
| Future first-time Nectr buyers | 172 |
| Future-window conversion | 2.97% |
| Held-out test users | 1,449 |
| Held-out top-decile users | 145 |
| Top-decile conversion | 6.90% |
| Held-out test-set baseline | 2.97% |
| Top-decile concentration vs. baseline | 2.32× |

The cohort excludes users with a prior Nectr purchase. Historical shopping behaviour is used to predict first-time Nectr purchase during a subsequent 30-day window.

The highest-scored decile shows a higher observed purchase rate than the overall held-out test cohort. This supports further investigation of targeted discovery, but does not prove that targeting or a personalized rail will cause additional purchases.

**Important:** All numbers above are simulated. They are not actual Instamart or Nectr business metrics.

## 3. Product options

| Option | Description | Main advantage | Main trade-off |
|---|---|---|---|
| A. Personalized rail | Surface Nectr to a selected audience in the existing home feed | Low initial commitment; testable | May not provide a sufficiently differentiated premium experience |
| B. Dedicated tab | Create a dedicated Nectr destination | Stronger discovery and brand separation | Greater implementation and adoption risk |
| C. Standalone app | Build a separate premium shopping experience | Maximum control over the experience | Highest cost, complexity, and customer-acquisition burden |

### Recommendation

Start by testing Option A, subject to engineering feasibility and experiment readiness.

This is a sequencing decision, not a conclusion that the personalized rail is already proven superior. It allows the team to test purchase incrementality before committing to a more expensive destination.

A dedicated tab should remain an option if real customer evidence demonstrates sufficient demand and a distinct premium experience is strategically valuable. A standalone app should require substantially stronger evidence of a differentiated use case.

## 4. RICE prioritization

The following scores reproduce the initial planning assumptions. Reach, impact, confidence, and effort are illustrative inputs—not validated market estimates.

Formula:

**RICE = Reach × Impact × Confidence ÷ Effort**

| Option | Assumed reach | Impact | Confidence | Effort | Illustrative score |
|---|---:|---:|---:|---:|---:|
| A. Personalized rail | 574 | 2 | 80% | 1.5 months | 612 |
| B. Dedicated tab | 5,731 | 1 | 50% | 4 months | 716 |
| C. Standalone app | 859 | 3 | 30% | 9 months | 86 |

The illustrative scores favour Option B, while the recommended sequence starts with Option A.

The reach values are illustrative planning inputs, not observed eligible-user counts or validated forecasts. The scoring horizon and reach definition should be standardized across options before using these scores to make an investment decision.

This is a deliberate difference between prioritization and execution. RICE helps compare options under stated assumptions; it does not establish which option will deliver the highest incremental revenue. The initial confidence inputs are hypotheses and should not be interpreted as statistically measured confidence.

Option A is preferred for initial validation because it is a smaller, more reversible test. Its actual effort and reach must be confirmed with engineering and product stakeholders before implementation.

## 5. Target audience and eligibility

The intended audience is users who have not previously purchased Nectr.

For a production pilot:

- Exclude users with a recorded prior Nectr purchase.
- Calculate behavioural features using only data available before the scoring date.
- Rank eligible users using a model trained on historical data.
- Before production use, compare model-based ranking with a simple baseline targeting strategy and validate performance on appropriately governed real data. Do not deploy the synthetic-data model directly to target actual customers.
- Evaluate whether the model provides sufficient targeting value to justify personalization.
- Define eligibility, exposure, and exclusion rules before randomization.

The synthetic analysis evaluates 1,449 held-out users, of whom 145 fall in the highest-scored decile. These figures describe the model evaluation split; they are **not the final production pilot size**.

The real pilot audience must be determined from actual eligible traffic, model readiness, and the sample size required for the experiment. New users without sufficient behavioural history need an explicit fallback experience rather than an unsupported assumption that they can be scored reliably.

## 6. User stories and acceptance criteria

### Story 1: Relevant premium discovery

*As an eligible Instamart user, I want to discover relevant premium grocery options without having to search extensively for them.*

Acceptance criteria:

- The rail appears only when the user meets the defined eligibility and experiment-assignment rules.
- The rail uses the existing home-feed infrastructure where feasible.
- Users can dismiss the rail.
- Dismissal does not cause repeated or intrusive reappearance during the pilot.
- The experience works for users with insufficient history through a defined fallback.
- Assignment and exposure events are logged for experiment analysis.

### Story 2: Preserve the core shopping experience

*As an Instamart user, I want the existing shopping experience to remain convenient even if I am not interested in premium products.*

Acceptance criteria:

- Core browse, cart, and checkout flows remain functional.
- The rail does not block access to essential shopping controls.
- The team monitors overall order conversion, cancellations, latency, and other relevant guardrails.
- Push notifications are outside the initial experiment unless separately approved and tested.

### Story 3: Measure incremental impact

*As a Product Manager, I want to understand whether the rail generates additional first-time Nectr purchases rather than merely changing browsing behaviour.*

Acceptance criteria:

- Treatment and control assignments are recorded.
- The primary outcome is defined before launch.
- Purchase events can be linked to eligible users and the experiment window.
- The dashboard displays treatment and control results, absolute lift, relative lift, sample size, and uncertainty.
- Guardrail metrics are available alongside the primary outcome.
- Results are not presented as causal unless the experimental design and execution support that interpretation.

## 7. Experiment design

### Hypothesis

Showing a personalized Nectr discovery rail to eligible users will increase the proportion who make a first-time Nectr purchase within 30 days compared with the existing experience.

### Experiment population

Users who have never purchased Nectr and satisfy the pre-defined eligibility criteria.

Randomize eligible users into two groups:

- **Treatment:** Existing experience plus the personalized Nectr rail.
- **Control:** Existing experience without the new rail.

Randomization should be at the user level, with stable assignment throughout the experiment. Both groups should be drawn from the same eligible population.

The primary analysis will follow an **intention-to-treat approach**: users are analyzed in the group to which they were originally assigned, regardless of rail exposure or engagement. Eligibility and exclusions must be defined before randomization, and any post-assignment exclusions must be documented in advance.

### Metrics

**Primary metric**

First-time Nectr purchase rate within the predefined 30-day outcome window:

Number of eligible users making their first Nectr purchase ÷ number of eligible users assigned to the group.

Analyze users according to their original assignment, regardless of whether they engage with the rail.

**Secondary metrics**

- Nectr product-page visit rate.
- Nectr add-to-cart rate.
- Checkout completion rate.
- Time from experiment assignment to first Nectr purchase.

**Guardrail metrics**

- Overall Instamart order conversion.
- Core non-Nectr order conversion.
- Cancellation and refund rates.
- Average order value.
- App performance and relevant customer-experience indicators.

Session time and engagement can help diagnose behaviour, but should not automatically be treated as positive outcomes. Longer sessions may indicate interest or friction.

### Sample size and duration

Do not assume the synthetic top-decile count of 145 or the earlier 574-user estimate is sufficient for a real experiment.

Before launch:

1. Obtain the real baseline first-time Nectr purchase rate.
2. Define the minimum commercially meaningful absolute lift.
3. Set the significance level and desired statistical power.
4. Calculate the required sample size per arm.
5. Estimate the recruitment period from eligible traffic.
6. Choose an outcome window and monitoring plan.

A 30-day outcome window is the proposed initial measurement period, not a claim that the experiment will necessarily be adequately powered within three weeks. Recruitment time and outcome observation time must be planned separately.

### Analysis and decision rule

Report:

- Treatment and control purchase rates.
- Absolute percentage-point difference.
- Relative lift.
- Confidence interval for the treatment-control difference.
- Sample size and missing-data or instrumentation issues.
- Guardrail differences.

Roll out further only if the result provides credible evidence of incremental improvement and guardrails remain within pre-agreed tolerances. If the result is inconclusive, determine whether to gather more data, refine eligibility, or test a different discovery experience rather than declaring success based on clicks or add-to-cart alone.

## 8. Instrumentation and dashboard requirements

The experiment should record the following events with user-level experiment assignment and timestamps:

- `experiment_assigned`
- `premium_rail_viewed`
- `premium_item_viewed`
- `premium_item_added_to_cart`
- `checkout_started`
- `payment_success`
- `order_cancelled`
- `premium_rail_dismissed`

The purchase event must distinguish a first-time Nectr purchase from repeat purchases using reliable purchase history.

The dashboard should show:

1. Eligible users and assigned users by arm.
2. Rail exposure and engagement.
3. First-time Nectr purchase rate by arm.
4. Absolute and relative treatment-control lift.
5. Confidence intervals and progress toward the planned sample size.
6. Core order conversion, cancellations, average order value, and performance guardrails.
7. Data-quality and instrumentation alerts.

Metrics should be segmented only where pre-specified and where sample sizes support meaningful interpretation. Avoid repeatedly checking significance and stopping early without an appropriate sequential-testing plan.

## 9. Stakeholder considerations

**Engineering:** Prefer reuse of the existing home feed where feasible. Confirm the effort required for eligibility, stable randomization, event instrumentation, and rollback.

**Design and Brand:** Give Nectr a recognizable visual identity within the rail. Validate whether the treatment communicates a premium proposition without disrupting core shopping.

**Finance:** Measure incremental purchases and, where data is available, incremental contribution margin. Monitor whether Nectr purchases displace standard purchases rather than expanding total value.

**Analytics/Data Science:** Validate label construction, historical feature cut-offs, model calibration and ranking quality, and experiment power. Ensure training and scoring data are separated correctly.

**Product:** Own the hypothesis, prioritization assumptions, primary metric, guardrails, decision rule, and final rollout decision.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Targeting model has weak predictive value | Treat it as an exploratory baseline; compare against simpler targeting approaches |
| Rail does not cause incremental purchases | Use a randomized control group |
| Standard purchases are cannibalized | Monitor core conversion and contribution-related outcomes |
| Premium brand proposition is unclear | Test visual treatment and gather qualitative feedback |
| Experiment is underpowered | Calculate sample size using real baseline data before launch |
| New users lack behavioural history | Define a fallback experience and measure coverage |
| Synthetic results are mistaken for real business evidence | Clearly label all portfolio data and conclusions as synthetic |

## 11. Execution plan

### Phase 1: Validate the analysis and feasibility

- Reproduce the synthetic pipeline and document assumptions.
- Confirm the model's modest performance and limitations.
- Review the proposed rail with product, design, and engineering.
- Define the real-data requirements for an experiment.

### Phase 2: Prepare the experiment

- Instrument events and validate purchase attribution.
- Confirm eligibility and assignment logic.
- Calculate sample size and recruitment duration.
- Finalize guardrail thresholds, dashboard, and rollback conditions.

### Phase 3: Run and evaluate

- Launch treatment and control after instrumentation checks.
- Monitor data quality and safety guardrails.
- Evaluate the primary outcome after the pre-defined observation window and analysis plan.
- Decide whether to iterate, stop, or expand.

### Phase 4: Revisit the product surface

If the rail shows credible incremental value, assess whether broader reach justifies a dedicated tab. Consider a standalone app only if evidence supports a distinct customer need and viable business case.

These phases are milestones, not guaranteed calendar deadlines. Actual timing depends on engineering capacity, traffic, and experiment power.

## 12. Limitations of the current analysis

- All users, orders, and outcomes are synthetic.
- The eligible cohort has a simulated 2.97% first-time purchase rate.
- The held-out top-decile conversion is 6.90%, versus a 2.97% test-set baseline; this is 2.32× concentration in one synthetic split, not causal lift.
- Logistic Regression has a ROC-AUC of approximately 0.617 and average precision of approximately 0.048. Predictive discrimination is modest.
- Logistic Regression slightly outperforms Random Forest in the reported test metrics; the difference is small.
- Clusters describe simulated historical behaviour and do not validate customer personas.
- The analysis cannot establish whether a rail, dedicated tab, promotion, or standalone app will improve actual conversion.

## 13. Why this is a PM + Applied ML project

The project connects a product decision to a measurable hypothesis:

1. Define a first-time purchase outcome.
2. Build a temporally separated synthetic dataset.
3. Compare predictive models using held-out evaluation.
4. Explore whether a ranked cohort could support targeted discovery.
5. Translate the analysis into a product experiment with a control group, primary metric, guardrails, and decision criteria.

The model informs a targeting hypothesis; it does not replace product judgment or experimentation.

## Status

- [x] Synthetic first-time purchase cohort defined
- [x] Historical features and held-out model evaluation implemented
- [x] Targeting hypothesis quantified and limitations documented
- [x] PRD updated to use first-time Nectr purchase as the primary outcome
- [x] Experiment and guardrail framework specified
- [x] Generate and validate dashboard from the current held-out model scores
- [x] Review and finalize executive summary
- [ ] Validate product assumptions against real data, if available
- [ ] Confirm feasibility and calculate experiment sample size
