import { useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { CloudArrowUp, File, X, CheckCircle } from '@phosphor-icons/react';

export const UploadDropzone = ({ onUpload }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFiles = (files) => {
    const validFiles = files.filter(file => 
      file.type === 'application/pdf' || 
      file.type === 'text/plain' ||
      file.type === 'application/msword' ||
      file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );

    if (validFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...validFiles.map(f => ({
        name: f.name,
        size: f.size,
        file: f
      }))]);
      
      if (onUpload) {
        onUpload(validFiles);
      }
    }
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-3">
      <span className="label-text flex items-center gap-2">
        <CloudArrowUp size={14} />
        Upload Documents
      </span>
      
      <motion.label
        className={`upload-dropzone ${isDragging ? 'border-[#002FA7] bg-[#002FA7]/5' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        data-testid="upload-dropzone"
      >
        <input
          type="file"
          className="hidden"
          accept=".pdf,.txt,.doc,.docx"
          multiple
          onChange={handleFileInput}
          data-testid="file-input"
        />
        <CloudArrowUp 
          size={28} 
          weight="duotone" 
          className={isDragging ? 'text-[#002FA7]' : 'text-[#52525B]'} 
        />
        <span className="text-sm font-medium text-[#52525B]">
          {isDragging ? 'Drop files here' : 'Drop files or click to upload'}
        </span>
        <span className="text-xs text-[#52525B]/60">
          PDF, TXT, DOC up to 10MB
        </span>
      </motion.label>

      {/* Uploaded files list */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {uploadedFiles.map((file, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 p-2 bg-white rounded-lg border border-black/10"
            >
              <File size={18} weight="duotone" className="text-[#002FA7] flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium truncate">{file.name}</p>
                <p className="text-xs text-[#52525B]">{formatFileSize(file.size)}</p>
              </div>
              <CheckCircle size={16} weight="fill" className="text-green-500 flex-shrink-0" />
              <button
                onClick={() => removeFile(index)}
                className="p-1 hover:bg-black/5 rounded"
                data-testid={`remove-file-${index}`}
              >
                <X size={14} />
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};
