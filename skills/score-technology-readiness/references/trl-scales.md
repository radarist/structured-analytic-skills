# TRL scales — verbatim definitions used by `score-technology-readiness`

Reference material for the skill's evidence checklist. The nine-level scale is NASA's; the DoD and EU
tables show how the same levels are worded elsewhere so that a claim quoted from one framework can be
read against another. Everything below is quoted or closely abridged from the primary sources named in
each section (see the SKILL.md `## Reference` list for full citations). The NASA, EU and DoD-2011 tables
are also printed by `python3 scripts/trl.py levels --scale nasa|eu|dod|all`.

## 1. NASA — NPR 7123.1D, Appendix E, Table E-1 (effective 5 July 2023)

Definitions, software descriptions and success criteria per level. The definition wording is unchanged
from NPR 7123.1C Appendix E (2020; w/Change 2, 2022), which the companion tool prints; §5.1.6 of the NPR
requires programs to use TRLs "and/or other measures of technology maturity" throughout the life cycle.
Where J. C. Mankins' 1995 white paper worded a level differently, that wording is shown.

```
NASA TRL definitions -- NPR 7123.1C Appendix E (2020; w/Change 2, 2022); Mankins (1995) wording where it differs
TRL 1  Basic principles observed and reported.
       software:     Scientific knowledge generated underpinning basic properties of software
                     architecture and mathematical formulation.
       success:      Peer reviewed documentation of research underlying the proposed
                     concept/application.
TRL 2  Technology concept and/or application formulated.
       software:     Practical application is identified but is speculative; no experimental
                     proof or detailed analysis is available to support the conjecture. Basic
                     properties of algorithms, representations, and concepts defined. Basic
                     principles coded. Experiments performed with synthetic data.
       success:      Documented description of the application/concept that addresses
                     feasibility and benefit.
TRL 3  Analytical and experimental proof-of-concept of critical function and/or characteristics.
       Mankins 1995: Analytical and experimental critical function and/or characteristic proof-
                     of-concept
       software:     Development of limited functionality to validate critical properties and
                     predictions using non-integrated software components.
       success:      Documented analytical/experimental results validating predictions of key
                     parameters.
TRL 4  Component and/or breadboard validation in a laboratory environment.
       software:     Key, functionality critical software components are integrated and
                     functionally validated to establish interoperability and begin architecture
                     development. Relevant environments defined and performance in the
                     environment predicted.
       success:      Documented test performance demonstrating agreement with analytical
                     predictions. Documented definition of potentially relevant environment.
TRL 5  Component and/or brassboard validated in a relevant environment.
       Mankins 1995: Component and/or breadboard validation in relevant environment
       software:     End-to-end software elements implemented and interfaced with existing
                     systems/simulations conforming to target environment. End-to-end software
                     system tested in relevant environment, meeting predicted performance.
                     Operational environment performance predicted. Prototype implementations
                     developed.
       success:      Documented test performance demonstrating agreement with analytical
                     predictions. Documented definition of scaling requirements. Performance
                     predictions are made for subsequent development phases.
TRL 6  System/sub-system model or prototype demonstration in a relevant environment.
       Mankins 1995: System/subsystem model or prototype demonstration in a relevant environment
                     (ground or space)
       software:     Prototype implementations of the software demonstrated on full-scale,
                     realistic problems. Partially integrated with existing hardware/software
                     systems. Limited documentation available. Engineering feasibility fully
                     demonstrated.
       success:      Documented test performance demonstrating agreement with analytical
                     predictions.
TRL 7  System prototype demonstration in an operational environment.
       Mankins 1995: System prototype demonstration in a space environment
       software:     Prototype software exists having all key functionality available for
                     demonstration and test. Well integrated with operational hardware/software
                     systems demonstrating operational feasibility. Most software bugs removed.
                     Limited documentation available.
       success:      Documented test performance demonstrating agreement with analytical
                     predictions.
TRL 8  Actual system completed and "flight qualified" through test and demonstration.
       Mankins 1995: Actual system completed and "flight qualified" through test and
                     demonstration (ground or space)
       software:     All software has been thoroughly debugged and fully integrated with all
                     operational hardware and software systems. All user documentation, training
                     documentation, and maintenance documentation completed. All functionality
                     successfully demonstrated in simulated operational scenarios. Verification
                     and Validation completed.
       success:      Documented test performance verifying analytical predictions.
TRL 9  Actual system flight proven through successful mission operations.
       Mankins 1995: Actual system "flight proven" through successful mission operations
       software:     All software has been thoroughly debugged and fully integrated with all
                     operational hardware and software systems. All documentation has been
                     completed. Sustaining software support is in place. System has been
                     successfully operated in the operational environment.
       success:      Documented mission operational results.
```

## 2. European Union — Horizon 2020 General Annex G

```
EU TRL definitions -- Horizon 2020 General Annex G (Commission Decision C(2014)4995)
TRL 1  basic principles observed
TRL 2  technology concept formulated
TRL 3  experimental proof of concept
TRL 4  technology validated in lab
TRL 5  technology validated in relevant environment (industrially relevant environment in the
       case of key enabling technologies)
TRL 6  technology demonstrated in relevant environment (industrially relevant environment in the
       case of key enabling technologies)
TRL 7  system prototype demonstration in operational environment
TRL 8  system complete and qualified
TRL 9  actual system proven in operational environment (competitive manufacturing in the case of
       key enabling technologies; or in space)
```

## 3. U.S. Department of Defense — TRA Guidance (2011), hardware wording

Section 2.5 of the ASD(R&E) *Technology Readiness Assessment (TRA) Guidance*, April 2011, with the
"supporting information" a TRA is expected to produce per level. (The February 2025 *Technology
Readiness Assessment Guidebook* keeps the same hardware definitions in its Table 2-1.)

```
DoD TRL definitions -- Technology Readiness Assessment (TRA) Guidance, ASD(R&E), April 2011, section 2.5
TRL 1  Basic principles observed and reported.
       supporting information: Published research that identifies the principles that underlie
                               this technology. References to who, where, when.
TRL 2  Technology concept and/or application formulated.
       supporting information: Publications or other references that outline the application
                               being considered and that provide analysis to support the
                               concept.
TRL 3  Analytical and experimental critical function and/or characteristic proof of concept.
       supporting information: Results of laboratory tests performed to measure parameters of
                               interest and comparison to analytical predictions for critical
                               subsystems. References to who, where, and when these tests and
                               comparisons were performed.
TRL 4  Component and/or breadboard validation in a laboratory environment.
       supporting information: System concepts that have been considered and results from
                               testing laboratory-scale breadboard(s). References to who did
                               this work and when. Provide an estimate of how breadboard
                               hardware and test results differ from the expected system goals.
TRL 5  Component and/or breadboard validation in a relevant environment.
       supporting information: Results from testing laboratory breadboard system are integrated
                               with other supporting elements in a simulated operational
                               environment. How does the "relevant environment" differ from the
                               expected operational environment? How do the test results compare
                               with expectations? What problems, if any, were encountered?
TRL 6  System/subsystem model or prototype demonstration in a relevant environment.
       supporting information: Results from laboratory testing of a prototype system that is
                               near the desired configuration in terms of performance, weight,
                               and volume. How did the test environment differ from the
                               operational environment? Who performed the tests? How did the
                               test compare with expectations?
TRL 7  System prototype demonstration in an operational environment.
       supporting information: Results from testing a prototype system in an operational
                               environment. Who performed the tests? How did the test compare
                               with expectations? What problems, if any, were encountered?
TRL 8  Actual system completed and qualified through test and demonstration.
       supporting information: Results of testing the system in its final configuration under
                               the expected range of environmental conditions in which it will
                               be expected to operate. Assessment of whether it will meet its
                               operational requirements.
TRL 9  Actual system proven through successful mission operations.
       supporting information: OT&E reports.
```

## 4. U.S. Department of Defense — TRA Guidebook (February 2025), Table 2-2 "DoD Software TRL Definitions, Descriptions, and Supporting Information"

The software scale the DoD uses when software is the critical technology element. Note the differences
from the hardware wording: TRL 4–6 speak of *module and/or subsystem validation* (TRL 6 in a "relevant
end-to-end environment"), TRL 7 of an "operational, high-fidelity environment", TRL 8 of "mission
qualified" and TRL 9 of "mission-proven operational capabilities". Abridged from the source table.

| TRL | Definition | Description (abridged) | Supporting information (abridged) |
|---|---|---|---|
| 1 | Basic principles observed and reported. | Lowest level of software technology readiness. A new software domain is being investigated by the basic research community; extends to basic properties of software architecture, mathematical formulations and general algorithms. | Basic research activities, research articles, peer-reviewed white papers, point papers, early lab model of basic concept. |
| 2 | Technology concept and/or application formulated. | Practical applications invented; applications speculative, with no proof or detailed analysis; examples limited to analytic studies using synthetic data. | Applied research activities, analytic studies, small code units, papers comparing competing technologies. |
| 3 | Analytical and experimental critical function and/or characteristic proof of concept. | Active R&D initiated; scientific feasibility demonstrated through analytical and laboratory studies; limited-functionality environments validate critical properties (including cybersecurity) using non-integrated software components and partially representative data. | Algorithms run on a surrogate processor in a laboratory environment; instrumented components in a laboratory environment; laboratory results validating critical properties. |
| 4 | Module and/or subsystem validation in a laboratory environment (i.e., software prototype development environment). | Basic software components integrated to establish that they work together; relatively primitive in efficiency and robustness; architecture development initiated (interoperability, reliability, maintainability, extensibility, scalability, security); emulation with current/legacy elements. | Advanced technology development; stand-alone prototype solving a synthetic full-scale problem or processing fully representative data sets. |
| 5 | Module and/or subsystem validation in a relevant environment. | Software technology ready to start integration with existing systems; prototype implementations conform to target environment/interfaces; experiments with realistic problems; simulated interfaces to existing systems; system software architecture established; algorithms run on processor(s) with characteristics expected in the operational environment. | System architecture diagram around the technology element with critical performance requirements defined; processor selection analysis; Sim/Stim laboratory build-up plan; software under configuration management; COTS/GOTS components identified. |
| 6 | Module and/or subsystem validation in a relevant end-to-end environment. | Engineering feasibility of a software technology demonstrated; laboratory prototype implementations on full-scale realistic problems, partially integrated with existing hardware/software systems; cybersecurity verification included in testing. | Results from laboratory testing of a prototype package near the desired configuration (performance incl. physical, logical, data and security interfaces); tested-vs-operational environment differences analytically understood; measurements of contribution to system-wide requirements (throughput, scalability, reliability); human-computer analysis begun. |
| 7 | System prototype demonstration in an operational, high-fidelity environment. | Program feasibility of a software technology demonstrated; operational-environment prototype implementations where critical technical risk functionality is available for demonstration and test, well integrated with operational hardware/software systems. | Critical technological properties, including cybersecurity, measured against requirements in an operational environment. |
| 8 | Actual system completed and mission qualified through test and demonstration in an operational environment. | Software technology fully integrated with operational hardware and software systems; software development documentation complete; all functionality and cybersecurity measures tested in simulated and operational scenarios. | Published documentation and product technology refresh build schedule; software resource reserve measured and tracked; all severity 1 and 2 defects resolved/confirmed and a reasonably low level of severity 3 defects open. |
| 9 | Actual system proven through successful mission-proven operational capabilities. | Software technology readily repeatable and reusable; fully integrated with operational hardware/software systems; all software documentation verified; successful operational experience; sustaining software engineering support in place; actual system. | Production configuration management reports; defect resolution system and process in place for deployed software to address defects discovered in production. |

Source: Office of the Under Secretary of Defense for Research and Engineering, *Technology Readiness
Assessment Guidebook*, February 2025, pp. 8–10 (Table 2-2); Table 2-1 (hardware) pp. 6–7; Table 2-3
(additional TRL descriptive terms) p. 11.

## 5. Wording differences to keep in mind

```
Wording differences:
  - TRL 6 is a RELEVANT environment in NASA (Mankins 1995 adds 'ground or space'), DoD and EU;
    the OPERATIONAL environment starts at TRL 7 (Mankins 1995 wrote 'space environment' for TRL
    7; NPR 7123.1, DoD and EU write 'operational environment').
  - EU TRL 5-6 add 'industrially relevant environment' for key enabling technologies and EU TRL
    9 adds 'competitive manufacturing ... or in space'.
  - NASA TRL 8-9 say 'flight qualified' / 'flight proven'; DoD says 'qualified' / 'proven'; EU
    says 'system complete and qualified' / 'actual system proven in operational environment'.
  - NPR 7123.1C TRL 3 reorders Mankins' wording and TRL 5 says 'brassboard validated' where
    Mankins and DoD say 'breadboard validation'.
```

## 6. Sibling scales (not TRL — do not mix them into a TRL score)

- **MRL — Manufacturing Readiness Level, 1–10.** OSD Manufacturing Technology Program, *MRL Deskbook*
  (2022 edition), summarised in the 2025 TRA Guidebook, Table 6-1: MRL 1 "basic manufacturing implications
  identified" … MRL 8 "pilot line capability demonstrated; ready to begin LRIP" … MRL 10 "full-rate
  production demonstrated and lean production practices in place". Use for *can it be made at rate*, not
  *does it work*.
- **IRL — Integration Readiness Level, 0–9.** Sauser, Gove, Forbes & Ramirez-Marquez (2010): the maturity of
  the *interface* between two components. GAO-20-48G (2020) restated the scale to align with TRL wording.
- **SRL — System Readiness Level, 1–9.** An index computed from the TRLs of a system's technologies and the
  IRLs of their integration points (Sauser et al.; GAO-20-48G).

For a chip, sensor or other hardware item, score the TRL against the NASA *hardware* description and add
an MRL for manufacturability; do not invent a "hardware readiness level".
