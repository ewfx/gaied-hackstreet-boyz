"use client"

import { useState, useRef, useEffect } from "react"
import { Bell, User, FileUp, Search, Shield, BookOpen, BarChart2, FileText, X, Eye, Plus } from "lucide-react"

export default function DocumentClassifier() {
  const [emailFile, setEmailFile] = useState(null)
  const [attachmentFiles, setAttachmentFiles] = useState([])
  const [classificationResult, setClassificationResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [previewFile, setPreviewFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState("")
  const [showPreview, setShowPreview] = useState(false)
  const emailInputRef = useRef(null)
  const attachmentInputRef = useRef(null)

  // Clean up object URLs when component unmounts or when previewFile changes
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const handleEmailFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      setEmailFile(file)
    }
  }

  const handleAttachmentFileUpload = (event) => {
    const newFiles = Array.from(event.target.files)
    if (newFiles.length === 0) return

    // Prevent duplicate files
    const uniqueNewFiles = newFiles.filter(
      (newFile) => !attachmentFiles.some((existingFile) => existingFile.name === newFile.name),
    )
    setAttachmentFiles((prev) => [...prev, ...uniqueNewFiles])

    // Reset the file input to allow selecting the same file again if needed
    if (attachmentInputRef.current) {
      attachmentInputRef.current.value = ""
    }
  }

  const addMoreAttachments = () => {
    if (attachmentInputRef.current) {
      attachmentInputRef.current.click()
    }
  }

  const removeEmailFile = () => {
    setEmailFile(null)
    if (emailInputRef.current) {
      emailInputRef.current.value = ""
    }
  }

  const removeAttachmentFile = (fileToRemove) => {
    setAttachmentFiles((prev) => prev.filter((file) => file.name !== fileToRemove.name))
  }

  const handlePredict = async () => {
    if (!emailFile) {
      setError("Please upload an email file")
      return
    }

    setIsLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append("email", emailFile)

    attachmentFiles.forEach((file) => {
      formData.append("attachments", file)
    })

    try {
      const response = await fetch("http://localhost:8000/classify", {
        method: "POST",
        body: formData,
      })
      const result = await response.json()
      
      console.log(response, result)

      if (result.Error) {
        throw new Error(result.Error)
      }
      
      // Check for API limit exceeded error specifically
      if (result.Error === "Rate limit exceeded" && result.retry_after) {
        throw new Error(`API rate limit exceeded. Please try again after ${result.retry_after} seconds.`)
      }

      setClassificationResult(result)
      setAttachmentFiles([])
      setEmailFile(null)
      if (emailInputRef.current) emailInputRef.current.value = ""
      if (attachmentInputRef.current) attachmentInputRef.current.value = ""
    } catch (err) {
      setError(err.message || "An unexpected error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  // Function to handle file preview
  const handlePreview = (file) => {
    if (!file) return

    // Clean up previous preview URL
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }

    const url = URL.createObjectURL(file)
    setPreviewFile(file)
    setPreviewUrl(url)
    setShowPreview(true)
  }

  // Function to close preview modal
  const closePreview = () => {
    setShowPreview(false)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl("")
    }
    setPreviewFile(null)
  }

  // Function to get file type category
  const getFileTypeCategory = (file) => {
    const type = file.type.toLowerCase()

    if (type.includes("image")) return "image"
    if (type.includes("pdf")) return "pdf"
    if (type.includes("text")) return "text"
    if (type.includes("msword") || type.includes("officedocument.wordprocessing")) return "word"
    return "other"
  }

  // Function to render text file content
  const renderTextPreview = async (file, previewElement) => {
    try {
      const text = await file.text()
      if (previewElement) {
        previewElement.textContent = text
      }
    } catch (error) {
      console.error("Error reading text file:", error)
    }
  }

  // Component for single file upload box (email)
  const SingleFileUploadBox = ({
    label,
    file,
    inputRef,
    onFileChange,
    onRemoveFile,
    onPreviewFile,
    accept,
    inputMsg,
    required = false,
  }) => {
    return (
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-4 
                     hover:border-[#D52B1E] transition-all duration-300 group"
        >
          <input type="file" ref={inputRef} onChange={onFileChange} className="hidden" accept={accept} />

          {file ? (
            <div className="p-2 bg-gray-50 rounded">
              <div className="flex items-center justify-between">
                <div className="flex items-center overflow-hidden">
                  <FileText className="h-6 w-6 text-[#D52B1E] mr-3 flex-shrink-0" />
                  <span className="truncate">{file.name}</span>
                </div>
                <div className="flex items-center ml-2">
                  <button
                    type="button"
                    onClick={() => onPreviewFile(file)}
                    className="text-blue-500 hover:text-blue-700 p-1 rounded-full hover:bg-blue-50"
                    title="Preview file"
                  >
                    <Eye className="h-5 w-5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => onRemoveFile(file)}
                    className="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-50 ml-1"
                    title="Remove file"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center cursor-pointer py-8" onClick={() => inputRef.current.click()}>
              <FileUp className="mx-auto mb-2 h-8 w-8 text-gray-400 group-hover:text-[#D52B1E] transition-colors" />
              <p className="text-gray-600 group-hover:text-[#D52B1E] transition-colors">
                {inputMsg || "Click to upload or drag and drop"}
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Component for multiple file upload box (attachments)
  const MultipleFileUploadBox = ({
    label,
    files,
    inputRef,
    onFileChange,
    onRemoveFile,
    onPreviewFile,
    onAddMore,
    accept,
    inputMsg,
    required = false,
  }) => {
    return (
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-4 
                     hover:border-[#D52B1E] transition-all duration-300 group"
        >
          <input type="file" ref={inputRef} onChange={onFileChange} className="hidden" accept={accept} multiple />

          {files.length > 0 ? (
            <div>
              <div className="space-y-2 mb-4">
                {files.map((fileItem, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center overflow-hidden">
                      <FileText className="h-6 w-6 text-[#D52B1E] mr-3 flex-shrink-0" />
                      <span className="truncate">{fileItem.name}</span>
                    </div>
                    <div className="flex items-center ml-2">
                      <button
                        type="button"
                        onClick={() => onPreviewFile(fileItem)}
                        className="text-blue-500 hover:text-blue-700 p-1 rounded-full hover:bg-blue-50"
                        title="Preview file"
                      >
                        <Eye className="h-5 w-5" />
                      </button>
                      <button
                        type="button"
                        onClick={() => onRemoveFile(fileItem)}
                        className="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-50 ml-1"
                        title="Remove file"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Add more files button */}
              <button
                type="button"
                onClick={onAddMore}
                className="flex items-center justify-center w-full py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#D52B1E]"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add more attachments
              </button>
            </div>
          ) : (
            <div className="text-center cursor-pointer py-8" onClick={() => inputRef.current.click()}>
              <FileUp className="mx-auto mb-2 h-8 w-8 text-gray-400 group-hover:text-[#D52B1E] transition-colors" />
              <p className="text-gray-600 group-hover:text-[#D52B1E] transition-colors">
                {inputMsg || "Click to upload or drag and drop"}
              </p>
              <p className="text-xs text-gray-500 mt-1">You can select multiple files</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Top Navigation Bar */}
      <nav className="bg-[#D52B1E] text-white shadow-md">
        <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Main Navigation */}
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <img
                  className="h-12 w-12 rounded-full object-cover border-2 border-white"
                  src="assets/logo.jpeg"
                  alt="W F Logo"
                />
                <span className="ml-3 text-xl font-bold">W F Financial Services</span>
              </div>
              <div className="ml-10 flex items-baseline space-x-4">
                <a href="#" className="hover:bg-red-700 px-3 py-2 rounded-md flex items-center">
                  <BookOpen className="mr-2 h-5 w-5" /> Dashboard
                </a>
                <a href="#" className="hover:bg-red-700 px-3 py-2 rounded-md flex items-center">
                  <FileText className="mr-2 h-5 w-5" /> Documents
                </a>
                <a href="#" className="bg-red-800 text-white px-3 py-2 rounded-md flex items-center">
                  <Shield className="mr-2 h-5 w-5" /> Classification
                </a>
                <a href="#" className="hover:bg-red-700 px-3 py-2 rounded-md flex items-center">
                  <BarChart2 className="mr-2 h-5 w-5" /> Reports
                </a>
              </div>
            </div>

            {/* User and Notification Area */}
            <div className="flex items-center">
              <button className="mr-4 hover:bg-red-700 p-2 rounded-full">
                <Search className="h-5 w-5" />
              </button>
              <button className="mr-4 hover:bg-red-700 p-2 rounded-full">
                <Bell className="h-5 w-5" />
              </button>
              <div className="flex items-center">
                <User className="h-5 w-5 mr-2" />
                <span>Admin User</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-grow container mx-auto px-4 py-8 max-w-4xl">
        <div className="bg-white shadow-xl rounded-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gray-50 border-b px-6 py-4">
            <h1 className="text-2xl font-bold text-gray-800">Document Classification System</h1>
            <p className="text-gray-600 mt-2">Upload email and attachments for AI-powered classification</p>
          </div>

          {/* File Upload Section */}
          <div className="p-6">
            {/* Email File Upload */}
            <SingleFileUploadBox
              label="Email File (Accepts .pdf, .docx, .txt, .eml, .email, .msg)"
              file={emailFile}
              inputRef={emailInputRef}
              onFileChange={handleEmailFileUpload}
              onRemoveFile={removeEmailFile}
              onPreviewFile={handlePreview}
              inputMsg="Click to upload email file"
              accept=".pdf, .docx, .txt, .eml, .email, .msg"
              required={true}
            />

            {/* Attachment Files Upload */}
            <MultipleFileUploadBox
              label="Attachment Files (Optional) (Accepts multiple .pdf, .doc, .docx, .txt)"
              files={attachmentFiles}
              inputRef={attachmentInputRef}
              onFileChange={handleAttachmentFileUpload}
              onRemoveFile={removeAttachmentFile}
              onPreviewFile={handlePreview}
              onAddMore={addMoreAttachments}
              accept=".pdf,.doc,.docx,.txt"
              inputMsg="Click to upload attachment files"
            />

            {/* Predict Button */}
            <button
              onClick={handlePredict}
              disabled={!emailFile || isLoading}
              className={`mt-6 w-full py-3 rounded-lg text-white font-semibold transition ${
                emailFile && !isLoading ? "bg-[#01D1D5] hover:bg-[#00BFC2]" : "bg-gray-400 cursor-not-allowed"
              }`}
            >
              {isLoading ? "Analyzing Document..." : "Predict Document"}
            </button>

            {/* Error Message */}
            {error && (
              <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">{error}</div>
            )}

            {/* Classification Results */}
            {classificationResult && (
              <div className="mt-6 bg-white shadow-md rounded-lg p-6 border-t-4 border-[#D52B1E]">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Classification Results</h2>

                {classificationResult.duplicate_found && (
                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
                    <p className="text-yellow-700">
                      Similar document found in database
                      {classificationResult.similarity &&
                        ` (${(classificationResult.similarity * 100).toFixed(2)}% similar)`}
                    </p>
                  </div>
                )}

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="font-medium text-gray-600">Request Type</p>
                    <p className="text-lg font-bold text-[#D52B1E]">{classificationResult.request_type || "N/A"}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-600">Sub Request Type</p>
                    <p className="text-lg font-bold text-[#D52B1E]">{classificationResult.sub_request_type || "N/A"}</p>
                  </div>
                </div>
                {classificationResult.similarity && (
                  <div>
                    <p className="font-medium text-gray-600">Similar To</p>
                    <p className="text-lg font-bold text-[#D52B1E]">{classificationResult.similar_text || "N/A"}</p>
                  </div>
                )}
                {classificationResult.reasoning && (
                  <div className="mt-4">
                    <p className="font-medium text-gray-600">Reasoning</p>
                    <p className="text-gray-700 italic">{classificationResult.reasoning}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* File Preview Modal */}
      {showPreview && previewFile && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-medium truncate max-w-[80%]">{previewFile?.name}</h3>
              <button
                onClick={closePreview}
                className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="p-4 flex-1 overflow-auto">
              {(() => {
                const fileType = getFileTypeCategory(previewFile)

                switch (fileType) {
                  case "image":
                    return (
                      <div className="flex justify-center">
                        <img
                          src={previewUrl || "/placeholder.svg"}
                          alt={previewFile.name}
                          className="max-w-full max-h-[70vh] object-contain"
                        />
                      </div>
                    )

                  case "pdf":
                    return (
                      <iframe
                        src={previewUrl}
                        title={previewFile.name}
                        className="w-full h-[70vh]"
                        style={{ border: "none" }}
                      ></iframe>
                    )

                  case "text":
                    return (
                      <div className="bg-gray-50 p-4 rounded-lg h-[70vh] overflow-auto">
                        <pre id="text-preview" className="whitespace-pre-wrap font-mono text-sm">
                          Loading text content...
                        </pre>
                        {(() => {
                          // Use an IIFE to read and display text content
                          const previewElement = document.getElementById("text-preview")
                          if (previewElement) {
                            renderTextPreview(previewFile, previewElement)
                          }
                          return null
                        })()}
                      </div>
                    )

                  default:
                    return (
                      <div className="text-center p-8">
                        <FileText className="h-20 w-20 mx-auto text-[#D52B1E] mb-4" />
                        <p className="text-xl font-medium mb-2">{previewFile.name}</p>
                        <p className="text-gray-500 mb-6">
                          {fileType === "word"
                            ? "Word document preview not available"
                            : "Preview not available for this file type"}
                        </p>
                        <a
                          href={previewUrl}
                          download={previewFile.name}
                          className="inline-block bg-[#D52B1E] text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
                        >
                          Download File
                        </a>
                      </div>
                    )
                }
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}