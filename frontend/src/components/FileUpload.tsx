import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload } from "lucide-react";

interface FileUploadProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export function FileUpload({ onUpload, isUploading }: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]!);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
        isDragActive
          ? "border-blue-500 bg-blue-50"
          : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
      } ${isUploading ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto h-10 w-10 text-gray-400 mb-3" />
      {isUploading ? (
        <p className="text-gray-500">Uploading...</p>
      ) : isDragActive ? (
        <p className="text-blue-600 font-medium">Drop the file here</p>
      ) : (
        <>
          <p className="text-gray-600 font-medium">
            Drag & drop a document here, or click to select
          </p>
          <p className="text-gray-400 text-sm mt-1">PDF or TXT files up to 10MB</p>
        </>
      )}
    </div>
  );
}
