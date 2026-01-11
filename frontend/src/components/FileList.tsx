import type { FileInfo } from '../services/api'

interface FileListProps {
  files: FileInfo[]
  onDelete?: (fileId: string) => void
  readOnly?: boolean
}

export function FileList({ files, onDelete, readOnly = false }: FileListProps) {
  if (files.length === 0) return null

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const getFileIcon = (fileType: string): string => {
    switch (fileType) {
      case 'pdf':
        return '📄'
      case 'txt':
        return '📝'
      case 'md':
        return '📋'
      default:
        return '📎'
    }
  }

  return (
    <div className="flex flex-wrap gap-2 mb-2">
      {files.map((file) => (
        <div
          key={file.id}
          className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg text-sm"
        >
          <span className="text-lg">{getFileIcon(file.file_type)}</span>
          <div className="flex flex-col">
            <span className="font-medium text-gray-900">{file.filename}</span>
            <span className="text-xs text-gray-500">
              {formatFileSize(file.file_size)} · {file.file_type.toUpperCase()}
            </span>
          </div>
          {!readOnly && onDelete && (
            <button
              onClick={() => onDelete(file.id)}
              className="ml-2 text-gray-400 hover:text-red-500 transition-colors"
              title="Delete file"
            >
              ✕
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
