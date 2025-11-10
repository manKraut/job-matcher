import { useState } from "react";

type Preferences = {
  keywords: string[];
  location: string;
  remote: boolean;
};

type Job = {
  title: string;
  location: string;
  company: string;
  url: string | null;
};

export default function App() {
  const [input, setInput] = useState("");
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [advice, setAdvice] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleClarify = async () => {
    setLoading(true);
    setError("");
    setPreferences(null);
    setAdvice(null);
    setJobs([]);
    try {
      const res = await fetch("http://localhost:8000/api/agents/preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input }),
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `Error ${res.status}: ${res.statusText}` }));
        throw new Error(errorData.detail || errorData.message || `Error ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      
      // Check if the response contains an error field (backend returns error in response body even with 200 status)
      // When JSON parsing fails, backend returns {"error": "...", "raw": "..."} where raw contains the actual GPT message
      if (data.error) {
        // Prioritize raw field as it contains the actual GPT output (which might be an error message)
        // Clean up the raw message - remove any "🔍 Raw GPT output:" prefix if present
        let errorMessage = data.raw || data.error || "Failed to process your input. Please try again.";
        if (errorMessage.includes("🔍 Raw GPT output:")) {
          errorMessage = errorMessage.split("🔍 Raw GPT output:")[1].trim();
        }
        throw new Error(errorMessage);
      }
      
      // Check if the response is missing required fields (invalid response structure)
      // This handles cases where GPT returns a plain text error message instead of JSON
      if (!data.keywords || !data.location || typeof data.remote !== 'boolean') {
        // If raw field exists, it contains the actual GPT output (which might be an error message)
        if (data.raw) {
          let errorMessage = data.raw;
          if (errorMessage.includes("🔍 Raw GPT output:")) {
            errorMessage = errorMessage.split("🔍 Raw GPT output:")[1].trim();
          }
          throw new Error(errorMessage);
        }
        throw new Error("The input provided is not clear. Please provide valid job search preferences.");
      }
      
      setPreferences(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to clarify preferences. Please try again.";
      setError(errorMessage);
      console.error("Error clarifying preferences:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchJobs = async () => {
    if (!preferences) return;
    setLoading(true);
    setError("");
    setAdvice(null);
    try {
      const res = await fetch(`http://localhost:8000/api/jobs?location=${encodeURIComponent(preferences.location)}`);
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `Error ${res.status}: ${res.statusText}` }));
        throw new Error(errorData.detail || errorData.message || `Error ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      setJobs(data || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch jobs. Please try again.";
      setError(errorMessage);
      console.error("Error fetching jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGetAdvice = async () => {
    if (!preferences || jobs.length === 0) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/api/agents/match-advice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ preferences, jobs }),
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `Error ${res.status}: ${res.statusText}` }));
        throw new Error(errorData.detail || errorData.message || `Error ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      setAdvice(data.advice || "No advice generated.");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to generate advice. Please try again.";
      setError(errorMessage);
      console.error("Error generating advice:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        {/* Header */}
        <header className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl sm:text-6xl font-extrabold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Job Matcher
          </h1>
          <p className="text-lg sm:text-xl text-slate-600 font-medium">
            AI-powered career discovery platform
          </p>
          <div className="mt-4 flex items-center justify-center gap-2 text-slate-500">
            <div className="h-1 w-1 bg-indigo-400 rounded-full animate-pulse"></div>
            <span className="text-sm">Powered by intelligent matching</span>
            <div className="h-1 w-1 bg-indigo-400 rounded-full animate-pulse"></div>
          </div>
        </header>

        {/* Input Section */}
        <section className="bg-white/80 backdrop-blur-lg p-6 sm:p-8 rounded-2xl shadow-xl border border-white/20 mb-6 animate-slide-up">
          <label className="block text-sm font-semibold text-slate-700 mb-3">
            Describe your ideal job
          </label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={4}
            className="w-full border-2 border-slate-200 rounded-xl px-4 py-3 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
            placeholder="e.g., remote frontend developer job in Europe with flexible hours..."
          />
          <button
            onClick={handleClarify}
            disabled={!input.trim() || loading}
            className="mt-4 w-full sm:w-auto bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-3 px-8 rounded-xl hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg hover:shadow-xl"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ) : (
              "✨ Clarify Preferences"
            )}
          </button>
        </section>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-lg animate-slide-up">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Preferences Section */}
        {preferences && (
          <section className="bg-white/80 backdrop-blur-lg p-6 sm:p-8 rounded-2xl shadow-xl border border-white/20 mb-6 animate-slide-up">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-800">Your Preferences</h2>
            </div>
            
            <div className="space-y-4 mb-6">
              <div className="flex flex-wrap gap-2">
                <span className="text-sm font-semibold text-slate-600 w-full sm:w-auto">Keywords:</span>
                {preferences.keywords.map((keyword, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800 border border-indigo-200"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
              
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="text-sm font-medium text-slate-700">
                  <strong>Location:</strong> {preferences.location}
                </span>
              </div>
              
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span className="text-sm font-medium text-slate-700">
                  <strong>Remote:</strong> {preferences.remote ? "Yes" : "No"}
                </span>
              </div>
            </div>
            
            <button
              onClick={handleSearchJobs}
              disabled={loading}
              className="w-full sm:w-auto bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold py-3 px-8 rounded-xl hover:from-emerald-600 hover:to-teal-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Searching...
                </span>
              ) : (
                "🔍 Search Jobs"
              )}
            </button>
          </section>
        )}

        {/* Jobs Section */}
        {jobs.length > 0 && (
          <section className="bg-white/80 backdrop-blur-lg p-6 sm:p-8 rounded-2xl shadow-xl border border-white/20 mb-6 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-slate-800">
                  Job Matches <span className="text-lg font-normal text-slate-500">({jobs.length})</span>
                </h2>
              </div>
            </div>
            
            <div className="space-y-4 mb-6">
              {jobs.map((job, idx) => (
                <div
                  key={idx}
                  className="group border-2 border-slate-200 p-5 rounded-xl hover:border-indigo-300 hover:shadow-lg bg-gradient-to-r from-white to-slate-50 transition-all duration-300"
                >
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-slate-800 mb-2 group-hover:text-indigo-600 transition-colors">
                        {job.title}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                          {job.company}
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          {job.location}
                        </span>
                      </div>
                    </div>
                    {job.url && (
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all transform hover:scale-105 active:scale-95 shadow-md hover:shadow-lg"
                      >
                        View Job
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            <button
              onClick={handleGetAdvice}
              disabled={loading}
              className="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-8 rounded-xl hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </span>
              ) : (
                "💡 Get Match Analysis"
              )}
            </button>
          </section>
        )}

        {/* Advice Section */}
        {advice && (
          <section className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 sm:p-8 rounded-2xl shadow-xl border-2 border-indigo-200 animate-slide-up">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-indigo-600 rounded-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-800">Match Analysis</h2>
            </div>
            <div className="prose prose-slate max-w-none">
              <p className="text-slate-700 leading-relaxed whitespace-pre-wrap bg-white/60 p-4 rounded-lg border border-indigo-100">
                {advice}
              </p>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}