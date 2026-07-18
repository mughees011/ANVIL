export interface TraceStep {
  step_id: string;
  tool_calls: {
    tool: string;
    input: Record<string, any>;
    output: Record<string, any>;
  }[];
  quality_check: {
    rule_check: "pass" | "fail";
    llm_rubric_check: "pass" | "fail" | null;
  };
  retries: number;
}

export interface TracePlanStep {
  step_id: string;
  description: string;
  status: "pending" | "success" | "failed" | "retried";
}

export interface TraceData {
  run_id: string;
  agent_name: string;
  task: string;
  plan: TracePlanStep[];
  steps: TraceStep[];
  final_status: "success" | "failed";
  started_at: string;
  ended_at: string;
}

export interface MemoryEntry {
  id: string;
  document: string;
  metadata: Record<string, any>;
}
