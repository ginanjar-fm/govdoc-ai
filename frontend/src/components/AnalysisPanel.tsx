import { AlertTriangle, CheckCircle, FileText, Tag } from "lucide-react";
import type { DocumentAnalysis } from "../types/document";

interface AnalysisPanelProps {
  analysis: DocumentAnalysis;
}

const severityColors = {
  high: "bg-red-100 text-red-800 border-red-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  low: "bg-blue-100 text-blue-800 border-blue-200",
};

const classificationLabels: Record<string, string> = {
  policy: "Policy",
  regulation: "Regulation",
  report: "Report",
  memo: "Memo",
  legislation: "Legislation",
  executive_order: "Executive Order",
  guidance: "Guidance",
  correspondence: "Correspondence",
  other: "Other",
};

export function AnalysisPanel({ analysis }: AnalysisPanelProps) {
  return (
    <div className="space-y-6">
      {/* Classification */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex items-center gap-2 mb-2">
          <Tag className="h-4 w-4 text-blue-600" />
          <h3 className="font-semibold text-sm text-gray-700 uppercase tracking-wide">
            Classification
          </h3>
        </div>
        <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
          {classificationLabels[analysis.classification] || analysis.classification}
        </span>
      </div>

      {/* Summary */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex items-center gap-2 mb-2">
          <FileText className="h-4 w-4 text-green-600" />
          <h3 className="font-semibold text-sm text-gray-700 uppercase tracking-wide">
            Summary
          </h3>
        </div>
        <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
      </div>

      {/* Entities */}
      {analysis.entities.length > 0 && (
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="h-4 w-4 text-purple-600" />
            <h3 className="font-semibold text-sm text-gray-700 uppercase tracking-wide">
              Extracted Entities ({analysis.entities.length})
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.entities.map((entity, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 bg-gray-100 text-gray-700 px-2.5 py-1 rounded text-sm"
              >
                <span className="text-xs text-gray-500 uppercase font-medium">
                  {entity.type}:
                </span>
                {entity.value}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Compliance Flags */}
      {analysis.compliance_flags.length > 0 && (
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="h-4 w-4 text-orange-600" />
            <h3 className="font-semibold text-sm text-gray-700 uppercase tracking-wide">
              Compliance Flags ({analysis.compliance_flags.length})
            </h3>
          </div>
          <div className="space-y-2">
            {analysis.compliance_flags.map((flag, i) => (
              <div
                key={i}
                className={`border rounded-lg px-3 py-2 text-sm ${severityColors[flag.severity]}`}
              >
                <span className="font-medium uppercase text-xs mr-2">
                  {flag.severity}
                </span>
                {flag.description}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
