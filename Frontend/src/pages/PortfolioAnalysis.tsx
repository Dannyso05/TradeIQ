import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

interface Asset {
  ticker: string;
  quantity: number;
}

interface AnalysisResult {
  report: string;
  error: string;
  details: {
    riskScore?: number;
    categories?: Record<string, number>;
    recommendations?: string[];
    forecasts?: Record<string, any>;
    [key: string]: any;
  };
}

const PortfolioAnalysis = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [customGoals, setCustomGoals] = useState<string[]>([]);
  const [newGoal, setNewGoal] = useState('');
  const [hasStoredPortfolio, setHasStoredPortfolio] = useState(false);
  const [editingAssets, setEditingAssets] = useState(false);
  const [newAsset, setNewAsset] = useState({ ticker: '', quantity: '' });

  // Fetch stored portfolio on component mount
  useEffect(() => {
    const fetchPortfolio = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get('http://localhost:3000/portfolio/stored-portfolio');
        setAssets(response.data.assets);
        setHasStoredPortfolio(true);
      } catch (error) {
        console.log('No stored portfolio found, using sample data');
        try {
          const sampleResponse = await axios.get('http://localhost:3000/portfolio/sample');
          setAssets(sampleResponse.data.assets);
        } catch (err) {
          console.error('Error fetching sample portfolio:', err);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchPortfolio();
  }, []);

  const handleAddGoal = () => {
    if (newGoal.trim() && !customGoals.includes(newGoal.trim())) {
      setCustomGoals([...customGoals, newGoal.trim()]);
      setNewGoal('');
    }
  };

  const handleRemoveGoal = (goal: string) => {
    setCustomGoals(customGoals.filter(g => g !== goal));
  };

  const handleAddAsset = () => {
    if (newAsset.ticker.trim() && Number(newAsset.quantity) > 0) {
      setAssets([
        ...assets,
        { 
          ticker: newAsset.ticker.trim().toUpperCase(), 
          quantity: Number(newAsset.quantity) 
        }
      ]);
      setNewAsset({ ticker: '', quantity: '' });
    }
  };

  const handleRemoveAsset = (index: number) => {
    const newAssets = [...assets];
    newAssets.splice(index, 1);
    setAssets(newAssets);
  };

  const analyzePortfolio = async () => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    
    try {
      const response = await axios.post('http://localhost:3000/portfolio/analyze', {
        portfolio: {
          assets: assets
        },
        goals: customGoals.length > 0 ? customGoals : undefined
      });
      
      setAnalysisResult(response.data);
    } catch (error: any) {
      console.error('Analysis error:', error);
      setAnalysisResult({
        report: '',
        error: `Analysis failed: ${error.response?.data?.detail || error.message || 'Unknown error'}`,
        details: {}
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

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
        <div>
          <h1 className="text-3xl font-bold mb-2">Portfolio Analysis</h1>
          <p className="text-gray-400">
            {hasStoredPortfolio 
              ? "Analyze your uploaded portfolio using our advanced AI system" 
              : "You're using sample data. Upload your own portfolio for personalized analysis."}
          </p>
        </div>
        
        {!hasStoredPortfolio && (
          <Link to="/upload" className="btn-primary">
            Upload Portfolio
          </Link>
        )}
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Portfolio Assets</h2>
          <button 
            onClick={() => setEditingAssets(!editingAssets)}
            className="text-sm px-3 py-1 rounded-md bg-zinc-700 hover:bg-zinc-600 transition-colors"
          >
            {editingAssets ? 'Done Editing' : 'Edit Assets'}
          </button>
        </div>

        {assets.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-zinc-700">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Symbol</th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Quantity</th>
                  {editingAssets && (
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-700">
                {assets.map((asset, index) => (
                  <tr key={index} className="hover:bg-zinc-700">
                    <td className="px-4 py-2 text-sm font-medium">{asset.ticker}</td>
                    <td className="px-4 py-2 text-sm text-right">{asset.quantity}</td>
                    {editingAssets && (
                      <td className="px-4 py-2 text-sm text-right">
                        <button 
                          onClick={() => handleRemoveAsset(index)}
                          className="text-red-400 hover:text-red-300"
                        >
                          Remove
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-400">No assets in the portfolio. Add some assets below.</p>
        )}

        {editingAssets && (
          <div className="mt-4 p-4 bg-zinc-800 rounded-md">
            <h3 className="text-sm font-medium mb-2">Add New Asset</h3>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Ticker (e.g. AAPL)"
                value={newAsset.ticker}
                onChange={(e) => setNewAsset({...newAsset, ticker: e.target.value})}
                className="input-field flex-1"
              />
              <input
                type="number"
                placeholder="Quantity"
                value={newAsset.quantity}
                onChange={(e) => setNewAsset({...newAsset, quantity: e.target.value})}
                className="input-field w-24"
                min="0"
                step="any"
              />
              <button 
                onClick={handleAddAsset}
                className="btn-primary whitespace-nowrap"
                disabled={!newAsset.ticker || !newAsset.quantity}
              >
                Add
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Analysis Goals</h2>
        <p className="text-gray-400 mb-4">
          Customize your analysis by adding specific investment goals. If left empty, we'll use default goals (retirement, home purchase, aggressive growth).
        </p>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {customGoals.map((goal, index) => (
            <div key={index} className="bg-zinc-700 rounded-full px-3 py-1 text-sm flex items-center">
              <span>{goal}</span>
              <button 
                onClick={() => handleRemoveGoal(goal)}
                className="ml-2 text-gray-400 hover:text-white"
              >
                ×
              </button>
            </div>
          ))}
          {customGoals.length === 0 && (
            <div className="text-gray-500 text-sm italic">Using default goals</div>
          )}
        </div>
        
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Add a custom goal (e.g. early_retirement)"
            value={newGoal}
            onChange={(e) => setNewGoal(e.target.value)}
            className="input-field flex-1"
          />
          <button 
            onClick={handleAddGoal}
            className="btn-secondary whitespace-nowrap"
            disabled={!newGoal.trim()}
          >
            Add Goal
          </button>
        </div>
      </div>

      <div className="flex justify-center">
        <button
          onClick={analyzePortfolio}
          disabled={isAnalyzing || assets.length === 0}
          className={`btn-primary px-8 py-3 text-lg ${isAnalyzing || assets.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isAnalyzing ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing Portfolio...
            </span>
          ) : (
            'Run AI Analysis'
          )}
        </button>
      </div>

      {analysisResult && (
        <div className="space-y-6">
          {analysisResult.error && (
            <div className="p-4 bg-red-900/30 text-red-400 rounded-md">
              <p className="font-medium">Error</p>
              <p>{analysisResult.error}</p>
            </div>
          )}
          
          {analysisResult.report && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Analysis Report</h2>
              <div className="prose prose-invert max-w-none">
                {analysisResult.report.split('\n').map((paragraph, index) => (
                  <p key={index} className="mb-4">{paragraph}</p>
                ))}
              </div>
            </div>
          )}
          
          {analysisResult.details && Object.keys(analysisResult.details).length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Detailed Insights</h2>
              
              {analysisResult.details.riskScore !== undefined && (
                <div className="mb-6">
                  <h3 className="text-lg font-medium mb-2">Risk Assessment</h3>
                  <div className="w-full bg-zinc-700 rounded-full h-4">
                    <div 
                      className="h-4 rounded-full bg-gradient-to-r from-green-500 to-red-500" 
                      style={{ width: `${analysisResult.details.riskScore}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs mt-1">
                    <span>Low Risk</span>
                    <span>High Risk</span>
                  </div>
                </div>
              )}
              
              {analysisResult.details.categories && (
                <div className="mb-6">
                  <h3 className="text-lg font-medium mb-2">Sector Allocation</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {Object.entries(analysisResult.details.categories).map(([category, percentage]) => (
                      <div key={category} className="flex items-center">
                        <div className="w-32 text-sm">{category}</div>
                        <div className="flex-1 h-6 bg-zinc-700 rounded">
                          <div 
                            className="h-6 bg-indigo-600 rounded"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <div className="w-12 text-right text-sm">{percentage}%</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {analysisResult.details.recommendations && (
                <div className="mb-6">
                  <h3 className="text-lg font-medium mb-2">Recommendations</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {analysisResult.details.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PortfolioAnalysis; 