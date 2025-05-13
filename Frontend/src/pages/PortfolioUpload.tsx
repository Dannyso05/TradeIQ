import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const PortfolioUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    success: boolean;
    message: string;
    data?: any;
  } | null>(null);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      
      // Create a preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreview(event.target?.result as string);
      };
      reader.readAsDataURL(selectedFile);
      
      // Reset status
      setUploadStatus(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setIsUploading(true);
    setUploadStatus(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(
        'http://localhost:3000/portfolio/upload-portfolio',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      setUploadStatus({
        success: true,
        message: 'Portfolio uploaded successfully!',
        data: response.data,
      });
      
      // Wait a moment before redirecting
      setTimeout(() => {
        navigate('/analysis');
      }, 2000);
      
    } catch (error: any) {
      setUploadStatus({
        success: false,
        message: `Upload failed: ${error.response?.data?.detail || error.message || 'Unknown error'}`,
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Upload Portfolio</h1>
        <p className="text-gray-400">
          Upload an image of your portfolio statement to extract your stock holdings.
          Our OCR technology will automatically detect stocks and quantities.
        </p>
      </div>

      <div className="card">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Portfolio Image Upload</h2>
          <p className="text-gray-400 text-sm">
            Supported file types: JPG, PNG, PDF
          </p>
        </div>

        <div className="space-y-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
              <div 
                className="border-2 border-dashed border-zinc-600 rounded-lg p-8 text-center hover:border-indigo-500 transition-colors"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    const droppedFile = e.dataTransfer.files[0];
                    setFile(droppedFile);
                    
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      setPreview(event.target?.result as string);
                    };
                    reader.readAsDataURL(droppedFile);
                    
                    setUploadStatus(null);
                  }
                }}
              >
                <input
                  type="file"
                  id="portfolio-upload"
                  accept="image/*,.pdf"
                  className="hidden"
                  onChange={handleFileChange}
                />
                
                <label htmlFor="portfolio-upload" className="cursor-pointer">
                  <div className="flex flex-col items-center">
                    <svg className="w-12 h-12 text-zinc-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                    <span className="font-medium mb-1">
                      {file ? file.name : "Drag & drop or click to upload"}
                    </span>
                    <span className="text-sm text-gray-400">
                      {file 
                        ? `${(file.size / 1024 / 1024).toFixed(2)} MB` 
                        : "Max file size: 10MB"}
                    </span>
                  </div>
                </label>
              </div>
              
              <div className="mt-4 flex justify-center">
                <button
                  onClick={handleUpload}
                  disabled={!file || isUploading}
                  className={`btn-primary w-full ${!file || isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {isUploading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    'Upload & Extract Data'
                  )}
                </button>
              </div>
            </div>
            
            <div className="flex-1">
              <div className="h-full min-h-[200px] bg-zinc-800 rounded-lg overflow-hidden flex items-center justify-center">
                {preview ? (
                  <img src={preview} alt="Portfolio Preview" className="max-w-full max-h-[300px] object-contain" />
                ) : (
                  <p className="text-zinc-500">Preview will appear here</p>
                )}
              </div>
            </div>
          </div>
          
          {uploadStatus && (
            <div className={`p-4 rounded-md ${uploadStatus.success ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
              <p className="font-medium">{uploadStatus.message}</p>
              {uploadStatus.success && uploadStatus.data && (
                <div className="mt-2 text-sm">
                  <p>Found {uploadStatus.data.assets.length} assets in your portfolio.</p>
                  {uploadStatus.data.assets.length > 0 && (
                    <div className="mt-2">
                      <p className="font-medium mb-1">Extracted Assets:</p>
                      <ul className="list-disc list-inside">
                        {uploadStatus.data.assets.slice(0, 5).map((asset: any, index: number) => (
                          <li key={index}>
                            {asset.ticker}: {asset.quantity}
                          </li>
                        ))}
                        {uploadStatus.data.assets.length > 5 && (
                          <li>...and {uploadStatus.data.assets.length - 5} more</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Tips for Best Results</h2>
        <ul className="list-disc list-inside space-y-2 text-gray-300">
          <li>Ensure the image is well-lit and clearly shows your portfolio holdings</li>
          <li>Make sure stock symbols and quantities are visible and not cut off</li>
          <li>For best results, crop the image to show only the relevant portfolio section</li>
          <li>If OCR fails, you can manually create a portfolio in the analysis section</li>
        </ul>
      </div>
    </div>
  );
};

export default PortfolioUpload; 