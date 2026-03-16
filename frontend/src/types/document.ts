export interface Entity {
  type: string;
  value: string;
}

export interface ComplianceFlag {
  severity: "high" | "medium" | "low";
  description: string;
}

export interface DocumentAnalysis {
  classification: string;
  summary: string;
  entities: Entity[];
  compliance_flags: ComplianceFlag[];
  analyzed_at: string | null;
}

export interface Document {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  uploaded_by: string;
  created_at: string;
  has_text: boolean;
  analysis?: DocumentAnalysis;
}
