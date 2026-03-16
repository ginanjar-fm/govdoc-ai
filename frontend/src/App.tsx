import { useCallback, useEffect, useState } from "react";
import { Brain, Loader2 } from "lucide-react";
import { FileUpload } from "./components/FileUpload";
import { AnalysisPanel } from "./components/AnalysisPanel";
import { DocumentList } from "./components/DocumentList";
import type { Document } from "./types/document";
import {
  uploadDocument,
  analyzeDocument,
  getDocument,
  listDocuments,
} from "./services/api";

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const data = await listDocuments(searchQuery || undefined);
      setDocuments(data.documents);
    } catch {
      // Silently fail on initial load
    }
  }, [searchQuery]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      const result = await uploadDocument(file);
      await fetchDocuments();
      const doc = await getDocument(result.id);
      setSelectedDoc(doc);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedDoc) return;
    setIsAnalyzing(true);
    setError(null);
    try {
      await analyzeDocument(selectedDoc.id);
      const updated = await getDocument(selectedDoc.id);
      setSelectedDoc(updated);
      await fetchDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-3">
          <Brain className="h-7 w-7 text-blue-600" />
          <div>
            <h1 className="text-xl font-bold text-gray-900">GovDoc AI</h1>
            <p className="text-xs text-gray-500">
              Government Document Processor with AI Analysis
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Upload Section */}
        <div className="mb-6">
          <FileUpload onUpload={handleUpload} isUploading={isUploading} />
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document List */}
          <div className="lg:col-span-1">
            <DocumentList
              documents={documents}
              selectedId={selectedDoc?.id ?? null}
              onSelect={setSelectedDoc}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
            />
          </div>

          {/* Document Detail / Analysis */}
          <div className="lg:col-span-2">
            {selectedDoc ? (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 truncate">
                    {selectedDoc.filename}
                  </h2>
                  {!selectedDoc.analysis && (
                    <button
                      onClick={handleAnalyze}
                      disabled={isAnalyzing}
                      className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {isAnalyzing ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Brain className="h-4 w-4" />
                          Analyze with AI
                        </>
                      )}
                    </button>
                  )}
                </div>

                {isAnalyzing && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-3" />
                    <p className="text-blue-700 font-medium">
                      Analyzing document with AI...
                    </p>
                    <p className="text-blue-500 text-sm mt-1">
                      This may take up to 30 seconds
                    </p>
                  </div>
                )}

                {selectedDoc.analysis && !isAnalyzing && (
                  <AnalysisPanel analysis={selectedDoc.analysis} />
                )}

                {!selectedDoc.analysis && !isAnalyzing && (
                  <div className="bg-gray-100 rounded-lg p-8 text-center text-gray-500">
                    <Brain className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p>Click "Analyze with AI" to classify, summarize, and extract entities</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-gray-100 rounded-lg p-12 text-center text-gray-500">
                <p>Select a document or upload a new one to get started</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
