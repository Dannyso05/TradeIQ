import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface Asset {
  ticker: string;
  quantity: number;
}

const Dashboard = () => {
  const [hasStoredPortfolio, setHasStoredPortfolio] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [assets, setAssets] = useState<Asset[]>([]);

  useEffect(() => {
    const checkStoredPortfolio = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get('http://localhost:3000/portfolio/stored-portfolio');
        setHasStoredPortfolio(true);
        setAssets(response.data.assets);
      } catch (error) {
        setHasStoredPortfolio(false);
        // Try to get the sample portfolio instead
        try {
          const sampleResponse = await axios.get('http://localhost:3000/portfolio/sample');
          setAssets(sampleResponse.data.assets);
        } catch (error) {
          console.error('Error fetching sample portfolio:', error);
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkStoredPortfolio();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Portfolio Dashboard</h1>
        <div className="flex space-x-4">
          <Link to="/upload" className="btn-primary">
            Upload Portfolio
          </Link>
          <Link to="/analysis" className="btn-secondary">
            Analyze Portfolio
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Portfolio Status</h2>
          <div className="space-y-2">
            <p className="flex justify-between">
              <span>Status:</span> 
              <span className={hasStoredPortfolio ? "text-green-400" : "text-yellow-400"}>
                {hasStoredPortfolio ? "Portfolio Uploaded" : "Using Sample Portfolio"}
              </span>
            </p>
            <p className="flex justify-between">
              <span>Total Assets:</span> 
              <span>{assets.length}</span>
            </p>
            <div className="mt-4">
              {!hasStoredPortfolio && (
                <p className="text-gray-400 text-sm">
                  You're currently viewing a sample portfolio. Upload your own portfolio for personalized analysis.
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="card md:col-span-2">
          <h2 className="text-xl font-semibold mb-4">Assets</h2>
          {assets.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-zinc-700">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Symbol</th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Quantity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-700">
                  {assets.map((asset, index) => (
                    <tr key={index} className="hover:bg-zinc-700">
                      <td className="px-4 py-2 text-sm font-medium">{asset.ticker}</td>
                      <td className="px-4 py-2 text-sm text-right">{asset.quantity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-400">No assets found in the portfolio</p>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/upload" className="p-4 bg-zinc-700 rounded-lg hover:bg-zinc-600 transition-colors">
            <div className="flex flex-col items-center text-center">
              <svg className="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              <span className="mt-2 font-medium">Upload Portfolio</span>
              <p className="text-xs text-gray-400 mt-1">Import from image</p>
            </div>
          </Link>
          
          <Link to="/analysis" className="p-4 bg-zinc-700 rounded-lg hover:bg-zinc-600 transition-colors">
            <div className="flex flex-col items-center text-center">
              <svg className="w-8 h-8 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              <span className="mt-2 font-medium">Analyze Portfolio</span>
              <p className="text-xs text-gray-400 mt-1">Get insights and recommendations</p>
            </div>
          </Link>
          
          {hasStoredPortfolio && (
            <button 
              onClick={async () => {
                try {
                  await axios.delete('http://localhost:3000/portfolio/clear-portfolio');
                  setHasStoredPortfolio(false);
                  setAssets([]);
                } catch (error) {
                  console.error('Error clearing portfolio:', error);
                }
              }}
              className="p-4 bg-zinc-700 rounded-lg hover:bg-red-900 transition-colors"
            >
              <div className="flex flex-col items-center text-center">
                <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
                <span className="mt-2 font-medium">Clear Portfolio</span>
                <p className="text-xs text-gray-400 mt-1">Remove uploaded data</p>
              </div>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 