import axios from "axios";
import type { Document } from "../types/document";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: {
    "X-API-Key": import.meta.env.VITE_API_KEY || "dev-api-key-change-me",
  },
});

export async function uploadDocument(file: File): Promise<{ id: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/documents/upload", formData);
  return data;
}

export async function analyzeDocument(
  documentId: string
): Promise<Document["analysis"]> {
  const { data } = await api.post(`/documents/${documentId}/analyze`);
  return data;
}

export async function getDocument(documentId: string): Promise<Document> {
  const { data } = await api.get(`/documents/${documentId}`);
  return data;
}

export async function listDocuments(
  search?: string
): Promise<{ documents: Document[]; count: number }> {
  const { data } = await api.get("/documents", { params: { search } });
  return data;
}

export async function getDocumentText(
  documentId: string
): Promise<{ text_content: string }> {
  const { data } = await api.get(`/documents/${documentId}/text`);
  return data;
}
