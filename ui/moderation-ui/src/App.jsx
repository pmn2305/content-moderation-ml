import { useState, useEffect } from 'react';

function App() {
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!image) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(image);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [image]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('text', text);
    if (image) formData.append('image', image);

    try {
      const res = await fetch('http://localhost:8000/moderate', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Moderation failed');
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Error checking content');
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setText('');
    setImage(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col">
      {/* Header Section - Full Width */}
      <div className="w-full px-6 py-16 text-center border-b border-gray-700/30">
        <h1 className="text-8xl font-black mb-4 text-white drop-shadow-lg tracking-tight">
          Content Guard
        </h1>
        <p className="text-2xl text-gray-300 font-light mb-2">AI-Powered Content Moderation</p>
        <p className="text-sm text-gray-400">Real-time analysis. Enterprise-grade accuracy. Instant results.</p>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-5 py-12">
        <div className="w-full mx-auto" style={{ maxWidth: '550px' }}>

        {/* Main Form Card */}
        <div className="card mb-6 bg-gray-800/80 border-gray-700/60 backdrop-blur-sm w-full">
          <form onSubmit={handleSubmit} className="space-y-10">
            {/* Text Input */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3 uppercase tracking-widest">Text Content</label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter text to analyze..."
                className="input-field min-h-[240px] text-base bg-gray-900/80 text-white border-gray-700/50 placeholder-gray-500 resize-none"
                style={{ maxWidth: '100%', boxSizing: 'border-box' }}
              />
            </div>

            {/* Image Upload */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3 uppercase tracking-widest">Image (Optional)</label>
              <div className="flex items-center gap-3">
                <label className="flex items-center justify-center gap-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg cursor-pointer hover:shadow-lg hover:shadow-gray-900/50 transition text-white font-bold text-sm hover:scale-105 active:scale-95 whitespace-nowrap border-2 border-gray-600 shadow-md">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M4.5 3A2.5 2.5 0 002 5.5v9A2.5 2.5 0 004.5 17h11a2.5 2.5 0 002.5-2.5v-9A2.5 2.5 0 0015.5 3h-11zM5 6.5a1.5 1.5 0 110 3 1.5 1.5 0 010-3zm6.5-.5a.5.5 0 100 1 .5.5 0 000-1zM6.3 13.957A1 1 0 018 13h4a1 1 0 01.757.347l.754-.754A2 2 0 0012 11H8a2 2 0 00-1.461.633l-.571.571z"/>
                  </svg>
                  <span>Upload Image</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setImage(e.target.files?.[0] || null)}
                    className="hidden"
                  />
                </label>
                {image && (
                  <div className="flex items-center gap-2 text-xs text-emerald-400 font-semibold">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="truncate">{image.name}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Buttons */}
            <div className="flex flex-col gap-5 pt-10">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full text-base py-3 font-bold tracking-wide"
              >
                {loading ? '🔍 Analyzing...' : '🔍 Analyze Now'}
              </button>
              <button
                type="button"
                onClick={clearAll}
                className="btn-ghost w-full text-white py-3 px-4 font-semibold"
              >
                Clear
              </button>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/40 border border-red-700/60 rounded-lg backdrop-blur-sm w-full">
            <p className="text-sm text-red-200 font-semibold">⚠️ {error}</p>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="space-y-4 w-full">
            {/* Image Preview */}
            {preview && (
              <div className="card bg-slate-800/50 border-purple-600/40 w-full">
                <h3 className="text-xs font-bold text-purple-200 mb-3 uppercase tracking-widest">Image Preview</h3>
                <img src={preview} alt="preview" className="w-full max-h-56 object-contain rounded-lg" />
              </div>
            )}

            {/* Result Card */}
            <div className="card bg-gray-800/60 border-gray-700/60 backdrop-blur-sm w-full">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-black text-white">Analysis Results</h2>
                <span className={`px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wider ${
                  result.decision === 'allow'
                    ? 'bg-green-900/40 text-green-200 border border-green-700/60'
                    : 'bg-red-900/40 text-red-200 border border-red-700/60'
                }`}>
                  {result.decision === 'allow' ? '✓ Allow' : '✗ Reject'}
                </span>
              </div>

              <div className="space-y-4">
                {/* Text Score */}
                {result.scores?.text !== undefined && (
                  <div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-bold text-gray-300">Text: Toxicity Level</span>
                      <span className="text-sm font-semibold text-white">{result.scores.text.toFixed(4)}</span>
                    </div>
                  </div>
                )}

                {/* Image Score */}
                {result.scores?.image !== undefined && (
                  <div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-bold text-gray-300">Image: Violation Risk</span>
                      <span className="text-sm font-semibold text-white">{result.scores.image.toFixed(4)}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        </div>
      </div>

      {/* Footer - Full Width */}
      <div className="w-full px-6 py-8 border-t border-gray-700/30 text-center">
        <p className="text-gray-400 text-sm">Enterprise-grade AI moderation • Powered by machine learning</p>
      </div>
    </div>
  );
}

export default App;

