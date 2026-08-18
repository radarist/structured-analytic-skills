# Delphi variants and the evidence on whether Delphi works

## Variants

| Variant | Use it when | What changes |
| --- | --- | --- |
| **Classic Delphi** | A forecast is wanted and convergence is plausible | Median + interquartile range fed back each round until stability (Dalkey & Helmer, 1963) |
| **Policy Delphi** | The point is to *map* disagreement on policy options, not erase it | Panel generates and rates the strongest arguments for and against options; consensus is explicitly not the goal (Turoff, in Linstone & Turoff, 1975) |
| **Real-time (round-less) Delphi** | Experts cannot be assembled into discrete rounds | Continuous re-estimation on a platform; each panelist sees the live distribution (Gordon & Pease, 2006) |
| **Argument Delphi** | The reasoning matters more than the number | Rounds are structured around surfacing and refining arguments rather than converging estimates |
| **Ranking Delphi** | Items must be prioritised rather than dated | Panelists rank items; agreement is measured with Kendall's W rather than an IQR |

## Why the method works

1. **Anonymity** removes the dominant personality, the halo effect and deference to
   seniority: the argument carries, not the speaker.
2. **Iterated controlled feedback** shows each panelist where the group sits, so outliers
   learn what others see and either revise or defend their position explicitly.
3. **Statistical aggregation** of independent judgments is usually more accurate than the
   typical individual judgment, because idiosyncratic errors partly cancel.

## Where it fails

- A misinformed panel aggregates its ignorance and returns it with added confidence. The
  method cannot rescue a bad panel or a badly worded question.
- Forced consensus manufactures agreement that no panelist actually holds, particularly on
  contested policy questions — the reason the Policy Delphi exists.
- Rowe & Wright's review of the experimental literature (1999; 2001) finds Delphi generally
  outperforms unstructured interacting groups and simple first-round averages, but the
  advantage is modest and inconsistent across studies. Treat a Delphi median as a
  structured estimate, not as evidence.
- Panels attrit. Rounds beyond three or four usually lose more panelists than they gain in
  precision.

## Stopping rules

Stability, not unanimity, ends a Delphi. Scheibe, Skutsch & Schofer (in Linstone & Turoff,
1975, pp. 262–287) proposed comparing the response *distribution* between rounds and
treating marginal changes below 15 % as an equilibrium: "any two distributions that show
marginal changes of less than 15% may be said to have reached 'stability'". The companion
script `scripts/delphi.py` implements a simpler, panel-level version of that idea — the
share of panelists who change their estimate between rounds, with the same 15 % level — so
its STABLE / MOVING verdict is an operational approximation of the published criterion, not
the identical statistic. Report which one was used.

## References

- N. Dalkey and O. Helmer, "An Experimental Application of the Delphi Method to the Use of Experts," *Management Science*, vol. 9, no. 3, pp. 458–467, 1963. doi:10.1287/mnsc.9.3.458
- H. A. Linstone and M. Turoff (eds.), *The Delphi Method: Techniques and Applications*. Reading, MA: Addison-Wesley, 1975. ISBN 978-0-201-04294-8
- M. Scheibe, M. Skutsch and J. Schofer, "Experiments in Delphi Methodology," in Linstone & Turoff (1975), pp. 262–287.
- G. Rowe and G. Wright, "The Delphi technique as a forecasting tool: issues and analysis," *International Journal of Forecasting*, vol. 15, no. 4, pp. 353–375, 1999. doi:10.1016/S0169-2070(99)00018-7
- G. Rowe and G. Wright, "Expert Opinions in Forecasting: The Role of the Delphi Technique," in J. S. Armstrong (ed.), *Principles of Forecasting*. Boston: Springer, 2001, pp. 125–144. doi:10.1007/978-0-306-47630-3_7
- T. J. Gordon and A. Pease, "RT Delphi: An efficient, 'round-less' almost real time Delphi method," *Technological Forecasting and Social Change*, vol. 73, no. 4, pp. 321–333, 2006. doi:10.1016/j.techfore.2005.09.005
