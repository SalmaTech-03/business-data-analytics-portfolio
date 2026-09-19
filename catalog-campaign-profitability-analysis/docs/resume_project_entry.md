# Résumé, LinkedIn and Interview Positioning

Every claim below is supported by something in this repository. Nothing is
exaggerated, and nothing implies employment, production deployment or a realised
business outcome.

---

## 1. Two-line résumé version

> **Catalog Campaign Profitability & Customer Targeting Analysis** — Built an
> end-to-end decision-support analysis evaluating a 250-customer direct-mail
> campaign, combining requirements and KPI definition with predictive modelling
> (R² 0.84) and financial modelling to quantify expected revenue, profit and ROI.
> Delivered a customer prioritisation framework and an 80-scenario sensitivity
> analysis supporting a conditional go/no-go recommendation.

---

## 2. Three-bullet résumé version

> **Catalog Campaign Profitability & Customer Targeting Analysis** | Python, scikit-learn, pandas, Power BI design
>
> - Defined the business problem, 15 business requirements, stakeholder map and KPI framework for a direct-mail campaign decision, translating "should we mail these catalogs" into a testable financial question with pre-stated decision criteria
> - Built a linear regression model predicting customer average sale amount (R² 0.84 held-out, MAE $93) and a campaign profitability model quantifying expected revenue, gross profit, cost, net profit and ROI across 250 prospects
> - Delivered a data-derived customer prioritisation framework identifying the top 25% of prospects carrying 53% of expected profit, plus an 80-scenario sensitivity analysis and risk register supporting a conditional recommendation to management

---

## 3. LinkedIn project description

> **Catalog Campaign Profitability & Customer Targeting Analysis**
>
> A direct-marketing decision-support project: should a company spend $1,625
> mailing catalogs to 250 prospective customers, and if the budget is cut, who
> should be mailed first?
>
> I approached this as a business analysis problem first and a modelling problem
> second. Before writing any code I defined the business case, stakeholder map,
> 15 business requirements with acceptance criteria, a KPI framework and a
> decision rule — so that the criteria for approval were fixed before the results
> were known.
>
> The analytics layer uses 2,375 historical customer records to model average sale
> amount from basket size and customer segment, weights each prediction by the
> customer's probability of responding, and works through the campaign economics
> from revenue to net profit to ROI. An 80-scenario sensitivity analysis tests how
> far the gross-margin, catalog-cost and response assumptions can move before the
> recommendation changes.
>
> Three things I would highlight:
>
> • **The interesting findings were the counter-intuitive ones.** Customers who
> responded to the *previous* catalog actually spend less on average — a
> confounding effect of segment mix that would have led targeting in exactly the
> wrong direction. And tenure, which stakeholders usually assume matters,
> correlates at 0.03 with spend.
>
> • **I chose the less accurate model on purpose.** A random forest scored better
> on held-out data, but the gain was worth less than a five-point change in the
> gross-margin assumption, and the linear model's coefficients are readable in
> dollars by a marketing stakeholder. That trade-off is documented rather than
> hidden.
>
> • **The limitations are stated as prominently as the results.** Response
> probabilities came from a model I could not inspect, and incrementality cannot
> be measured without a control group. Both are carried into the recommendation
> rather than glossed over.
>
> Built with Python, pandas, scikit-learn, Matplotlib and Seaborn, with 77 unit
> tests and a Power BI dashboard specification. Full repository including business
> requirements, risk register, decision framework and implementation plan on
> GitHub.

---

## 4. GitHub project description (repository "About" field)

**Short version (under 160 characters, for the About field):**

> End-to-end BA + analytics project: predictive modelling and financial analysis to decide a $1,625 direct-mail campaign and prioritise 250 customers.

**Longer version (for a pinned-repository blurb or portfolio site):**

> Should a company spend $1,625 mailing catalogs to 250 prospects? This project
> answers that end to end — business requirements, stakeholder analysis, KPI
> framework and decision rule alongside data-quality assessment, EDA, a linear
> regression model (R² 0.84), campaign profitability modelling, a data-derived
> customer prioritisation framework, an 80-scenario sensitivity analysis, a
> 12-risk register and a Power BI dashboard specification. 77 unit tests. Every
> figure computed from the supplied data; every assumption stated.

---

## 5. Sixty-second interview explanation

> A company had a mailing list of 250 prospects and needed to decide whether to
> spend $1,625 sending them catalogs. The cost is committed upfront; the revenue
> is uncertain and only comes from people who actually respond.
>
> I used their 2,375 existing customer records to model what drives spending, then
> applied that to the 250 prospects and weighted each prediction by their
> probability of responding, because a customer with a $1,000 predicted order who
> responds 10% of the time is worth $100 to the campaign, not $1,000.
>
> The answer was a clear yes — about $47,000 in expected revenue, $23,600 in gross
> profit at a 50% margin, $21,987 net after campaign cost. A 13.5x return.
>
> But the number I'd actually lead with in a meeting isn't that one. It's the
> break-even: response would have to collapse to about a 2.3% response rate before
> the campaign stopped paying, against a forecast of 34%. That's what tells
> management the decision is safe — not the point estimate, which is just my best
> guess about an uncertain future.
>
> I also ranked all 250 by expected profit, because the first question after "yes"
> is usually "what if I only have half the budget".

---

## 6. Two-minute interview explanation

> **The problem.** A retailer sells through a direct-mail catalog alongside its
> stores. Marketing had a list of 250 prospects. Each catalog costs $6.50 to print
> and mail, so the campaign commits $1,625 before a single order arrives.
> Historically they'd decided who to mail on segment intuition. They wanted a
> quantified answer.
>
> **How I framed it.** I treated it as a business analysis problem first. Before
> touching the data I wrote the business case, the stakeholder map, fifteen
> business requirements with acceptance criteria, a KPI framework and — this is
> the part I think matters most — a decision rule stated *before* I knew the
> results. Net profit above zero, assumptions validated, ROI above the
> organisation's threshold. That way the analysis couldn't be reverse-engineered
> to justify a conclusion I'd already reached.
>
> **The analysis.** I had 2,375 historical customers with known spending. I built
> a linear regression predicting average sale amount from two things: basket size
> and customer segment. I tested tenure and dropped it — it correlates at 0.03
> with spend, which surprised me. Then I scored the 250 prospects, weighted each
> prediction by their supplied response probability, applied the 50% gross margin
> and subtracted campaign cost.
>
> **The result.** $47,225 expected revenue, $21,987 net profit, 13.5x ROI. Every
> one of the 250 prospects individually clears their own catalog cost, so there's
> no case for trimming the list. The top quarter carries 53% of the profit, which
> is what matters if the budget gets cut.
>
> **What I'd want to be asked about.** Three things.
>
> First, a finding that would have sent targeting the wrong way. Customers who
> responded to the *last* catalog spend *less* on average — $156 against $419. It
> looks like past responders are worse customers. They're not; prior response is
> concentrated in the lowest-spending segment. It's confounding. Anyone filtering
> the mail file to "previous responders" would have systematically selected the
> least valuable names.
>
> Second, I deliberately shipped the less accurate model. A random forest beat
> linear regression on held-out data — R² 0.88 against 0.83. But the improvement
> was worth about $1,875 of gross profit against a $21,987 expected profit, and
> less than the swing from a five-point change in the margin assumption. The
> binding constraint on this forecast was assumption quality, not estimator
> sophistication. And the linear coefficients are readable in dollars by a
> marketing manager. I documented that trade-off rather than quietly picking the
> higher score.
>
> Third, the limitation I couldn't solve. There's no control group, so I can't
> tell how many of these orders would have happened anyway. That's the one thing
> that could genuinely make this recommendation wrong, and I put it in the
> executive summary rather than a footnote. My recommendation for the next
> campaign was to hold back a randomised group so it becomes measurable.

---

## 7. Ten likely interview questions with strong answers

### Q1. Walk me through this project.

> A company needed to decide whether to spend $1,625 mailing catalogs to 250
> prospects. I built the decision end to end: business requirements and a decision
> rule first, then a regression model predicting what each prospect would spend,
> weighted by their probability of responding, then the campaign economics —
> revenue, gross profit, cost, net profit, ROI. The answer was $21,987 expected
> net profit at 13.5x return. I also ranked all 250 by expected profit so
> marketing could cut from the bottom if budget was reduced, and ran 80 scenarios
> to show how wrong the assumptions could be before the answer changed.

### Q2. Why is this a business analyst problem rather than a data science one?

> The modelling is the smallest part. The substance is in defining what decision
> is actually being made, who owns each assumption, what "success" means in
> measurable terms, and what would have to be true for the recommendation to
> reverse.
>
> Concretely: the model took an afternoon. Working out that the gross margin
> assumption matters seven times more than catalog cost — and therefore that
> Finance's sign-off is worth more attention than renegotiating with the printer —
> is a business analysis conclusion, not a modelling one. So is noticing that
> without response attribution in place before mailing, the organisation learns
> nothing regardless of how the campaign performs. I made that a go/no-go gate in
> the implementation plan.

### Q3. Why linear regression? Wouldn't a more sophisticated model be better?

> I tested that. A random forest reached R² 0.88 against linear regression's 0.83
> on held-out data, with about $15 less error per customer.
>
> I kept the linear model anyway, for a reason I can defend with numbers. That
> $15 across 250 customers is roughly $1,875 of gross profit, against an expected
> net profit of $21,987. Moving the gross margin assumption from 50% to 45% changes
> the answer by more than the entire model upgrade. The binding constraint on this
> forecast is assumption quality, not estimator sophistication.
>
> Meanwhile the linear coefficients are directly usable: "a dual-relationship
> customer is worth $282 more per sale" goes straight into a marketing
> conversation about which segments to grow. A feature importance score doesn't.
>
> I'd revisit that if the model moved into automated per-customer targeting at
> scale, where accumulated error starts to matter more than explanation.

### Q4. What does R² = 0.84 mean? And why shouldn't it be called accuracy?

> It means the model explains about 84% of the variation in average sale amount
> across the customers evaluated. It's a comparison: how much better the model's
> errors are than the errors you'd make by predicting the overall average for
> everyone.
>
> It is not an accuracy rate. It doesn't mean predictions are right 84% of the
> time, and it doesn't mean any individual prediction is within 16% of the truth.
> A model can explain most of the variance and still be meaningfully wrong about
> any given customer.
>
> The reason I'm careful about this is practical. If I tell a marketing director
> the model is "84% accurate", they'll plan as though individual predictions are
> reliable to within a sixth. So I always pair R² with mean absolute error — here
> about $93 on a mean predicted sale of $553, roughly 17% either way. That's the
> number that describes individual reliability.
>
> What makes the campaign forecast trustworthy isn't that any prediction is
> precise. It's that it's a sum across 250 customers, and errors in opposite
> directions largely offset.

### Q5. How did you calculate expected revenue and profit?

> Per customer: predicted sale amount times probability of response. That's the
> key step — a prospect with a $1,000 predicted order who responds 10% of the time
> is worth $100 to the campaign, not $1,000.
>
> Then gross profit is expected revenue times the 50% margin, because revenue
> doesn't fund the campaign, only the margin on it does. Using revenue would have
> overstated campaign value by a factor of two.
>
> Campaign cost is 250 catalogs times $6.50, which is $1,625. Net profit is gross
> profit minus that. ROI is net profit over campaign cost.
>
> Across all 250: $47,225 revenue, $23,612 gross profit, $1,625 cost, $21,987 net
> profit, 13.5x return. Every one of those formulas lives in a single module with
> unit tests, so there's no chance of two different versions of the same number
> existing in different parts of the project.

### Q6. What assumptions did you make, and which worried you most?

> Ten registered assumptions. The three that carry real weight:
>
> The 50% gross margin, which came from the source brief. Gross profit scales
> linearly with it, so it's the highest-leverage financial input. That's a phone
> call to Finance — resolvable.
>
> The $6.50 catalog cost. Low impact; sensitivity showed cost would have to reach
> about $94 per catalog to eliminate the profit.
>
> The one that worried me is the response probability. It came supplied with the
> mailing list, produced by a model I don't have and can't inspect. It drives half
> the revenue calculation. I couldn't validate it, so I did the next best thing:
> stress-tested it across 60% to 120% of the supplied values and published the
> break-even. Response would have to collapse to about 6.9% of the modelled
> level — a 2.3% response rate — before the campaign stopped paying. That's a wide
> enough margin that I'm comfortable recommending, but I flagged obtaining
> documentation for that model as a prerequisite for the next campaign.

### Q7. What would change your recommendation?

> Within the model, essentially nothing I could construct from plausible inputs.
> I ran 80 scenarios — margin from 40% to 60%, cost from $5 to $10, response from
> 60% to 120% of modelled — and all 80 are profitable. Even all three adverse at
> once returns $8,834 at 3.5x.
>
> What could actually change it sits outside the grid. The main one is
> incrementality. If a large share of these customers would have ordered anyway,
> the campaign's true incremental profit is much lower than the headline figure,
> and no sensitivity analysis can detect that — it needs a randomised control
> group, which this campaign design doesn't include. I put it in the executive
> summary rather than burying it, and recommended building a holdout into the next
> campaign.
>
> The second is a structural break: if customer behaviour has shifted since the
> training data was collected. The data carries no timestamp, so I can't even check
> how old it is. That's a data request I'd make before reusing this.

### Q8. How did you decide the customer priority thresholds?

> I didn't pick them. Arbitrary cut-offs like "top 50 customers" go stale the
> moment the model or the assumptions change.
>
> The rule has an economic floor and a statistical split. Low priority is anyone
> whose expected net profit is at or below zero — their catalog doesn't pay for
> itself, so mailing them destroys value regardless of how attractive they look on
> other measures. Above that floor, High is the top quartile of profitable
> customers and Medium is the rest.
>
> Because the threshold is a percentile of the current distribution rather than a
> fixed dollar figure, it moves automatically when the model is refreshed.
>
> One honest detail: in this campaign no customer falls into the Low tier —
> everyone is profitable. I kept the tier in the framework anyway, because the rule
> has to work on a future list that does contain value-destroying names. A
> framework that only handles the convenient case isn't a framework.

### Q9. How would you present this to a non-technical marketing director?

> I'd lead with the decision, not the method. "Spend $1,625, expect about $22,000
> back. Every name on the list pays for itself."
>
> Then the thing that actually gives them confidence, which isn't the point
> estimate. It's the break-even: response would have to fall to about one order
> per 43 catalogs, against a forecast of one in three, before this stops paying.
> They're not being asked to bet on my model being right.
>
> Then what it means operationally: if budget gets cut, here's the ranked list, cut
> from the bottom. And one finding they can use beyond this campaign — customers
> with both a loyalty card and a store credit card return 27x against 4x for
> store-list customers. Growing that segment is worth more than optimising this
> mailing.
>
> I'd mention the model once, in a sentence, and I'd never say "84% accurate". I'd
> say a typical prediction is off by about $93 either way, but since we're adding
> up 250 customers, the errors largely cancel. That's honest and it's something
> they can hold in their head.

### Q10. What would you do differently, or improve with more data?

> Four things.
>
> The biggest gap is a control group. Without one I can measure gross performance
> but not causal lift, and that's the single largest open question in the project.
> I'd build a randomised holdout into the next campaign — a small amount of forgone
> profit buys the answer.
>
> Second, I'd want the response model documented rather than supplied as a black
> box, so that assumption could be validated instead of stress-tested.
>
> Third, richer features. I had two predictors. Recency, purchase frequency,
> product category and channel history would all plausibly improve the model, and
> would let me move from a single-campaign view to customer lifetime value — which
> matters, because a campaign that acquires a long-term customer is undervalued by
> a single-campaign profit figure.
>
> Fourth, as a business analyst rather than an analyst: I'd push harder on the
> measurement design earlier. I built a monitoring KPI set and an eight-phase
> implementation plan, but the honest position is that the attribution mechanism
> should be agreed before anyone builds a model, not after. If you can't measure
> the outcome, the forecast is the last thing anyone ever learns from the campaign.

---

## Positioning notes

**For Business Analyst roles** — lead with the requirements framework, the
stakeholder analysis, the decision rule set before results, the risk register and
the implementation plan. The modelling is supporting evidence that you can work
with technical teams, not the headline.

**For Data Analyst / Business Analytics roles** — lead with the modelling,
validation approach, financial modelling and sensitivity analysis. The business
analysis layer is your differentiator: most candidates bring a model, few bring a
decision framework.

**What to emphasise in either case** — the counter-intuitive findings, the
deliberate choice of the less accurate model with the reasoning behind it, and the
limitations stated as prominently as the results. Interviewers remember judgement
more than technique.

**Never claim** — that this ran in production, that it generated actual revenue,
or that any business acted on it. The work stands on its reasoning.
