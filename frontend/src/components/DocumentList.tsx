import { FileText, Search } from "lucide-react";
import type { Document } from "../types/document";

interface DocumentListProps {
  documents: Document[];
  selectedId: string | null;
  onSelect: (doc: Document) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function DocumentList({
  documents,
  selectedId,
  onSelect,
  searchQuery,
  onSearchChange,
}: DocumentListProps) {
  return (
    <div className="bg-white rounded-lg border h-full flex flex-col">
      <div className="p-3 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        {documents.length === 0 ? (
          <div className="p-6 text-center text-gray-400 text-sm">
            No documents yet. Upload one to get started.
          </div>
        ) : (
          documents.map((doc) => (
            <button
              key={doc.id}
              onClick={() => onSelect(doc)}
              className={`w-full text-left px-4 py-3 border-b hover:bg-gray-50 transition-colors ${
                selectedId === doc.id ? "bg-blue-50 border-l-2 border-l-blue-500" : ""
              }`}
            >
              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-gray-400 mt-0.5 shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {doc.filename}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {formatFileSize(doc.file_size)} &middot;{" "}
                    {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                  {doc.analysis && (
                    <span className="inline-block mt-1 bg-green-100 text-green-700 text-xs px-1.5 py-0.5 rounded">
                      {doc.analysis.classification}
                    </span>
                  )}
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
