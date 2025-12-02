Workflow Visualization (LangGraph / State Diagram)

The core optimization is the **parallel execution** step inside the loop, where the **next question is prepared while the current answer is scored**.

```` mermaid
stateDiagram-v2
    direction TB

    state "Initialization Phase (Sequential)" as Init {
        [*] --> Start
        state "START: User Sends Job Role/JD" as Start
        state "1. Onboarding Agent: Setup RAG" as Onboarding
        Start --> Onboarding
    }

    state "Interview Phase (Adaptive Loop)" as Interview {
        state "2. Interview Agent: Ask Question N" as AskQ
        state "Wait for User Response (ASR)" as WaitASR

        state "3. Process Answer Node (Parallel)" as ParallelProc {
            state "3A. Scoring Agent: Score Answer" as Scoring
            --
            state "3B. Next Question Agent: Generate Q N+1" as NextGen
        }

        state "4. Score Synthesis & Routing" as Routing
        state "5A. Case Agent: Ask Work Sample (+ Gen Rubric)" as CaseAsk

        AskQ --> WaitASR
        WaitASR --> ParallelProc
        ParallelProc --> Routing

        Routing --> AskQ : Loop (ASK_Q)
        Routing --> CaseAsk : Transition (WORK_SAMPLE)
    }

    state "Final Phase (Sequential)" as Final {
        state "Wait for Work Sample Submission" as WaitSample
        state "5B. Case Agent: Score vs Rubric" as CaseScore
        state "6. Review Agent: Generate Report" as Review
        state "END: Deliver Final Score" as EndState

        WaitSample --> CaseScore
        CaseScore --> Review
        Review --> EndState
        EndState --> [*]
    }

    [*] --> Init
    Init --> Interview
    CaseAsk --> Final
````
