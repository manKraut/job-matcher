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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleClarify = async () => {
    setLoading(true);
    setError("");
    setPreferences(null);
    try {
      const res = await fetch("http://localhost:8000/api/agents/preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input }),
      });
      const data = await res.json();
      setPreferences(data);
    } catch (err) {
      setError("Failed to clarify preferences.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearchJobs = async () => {
    if (!preferences) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`http://localhost:8000/api/jobs?location=${encodeURIComponent(preferences.location)}`);
      const data = await res.json();
      setJobs(data || []);
    } catch (err) {
      setError("Failed to fetch jobs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 px-6 py-12">
      <div className="max-w-xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-center">🧠 Open Job Matcher</h1>

        <div>
          <label className="block mb-2 font-semibold">Describe your ideal job:</label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={3}
            className="w-full border px-4 py-2 rounded-md"
            placeholder="e.g., Remote React developer job in Europe"
          />
          <button
            onClick={handleClarify}
            className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Clarify Preferences
          </button>
        </div>

        {loading && <p>Loading...</p>}
        {error && <p className="text-red-500">{error}</p>}

        {preferences && (
          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-lg font-semibold mb-2">🎯 Clarified Preferences</h2>
            <pre className="text-sm bg-gray-100 p-2 rounded">
              {JSON.stringify(preferences, null, 2)}
            </pre>
            <button
              onClick={handleSearchJobs}
              className="mt-3 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              Search Jobs
            </button>
          </div>
        )}

        {jobs.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">💼 Job Results</h2>
            {jobs.map((job, idx) => (
              <div key={idx} className="p-4 border rounded bg-white shadow-sm">
                <h3 className="font-semibold">{job.title}</h3>
                <p className="text-sm text-gray-600">{job.company} — {job.location}</p>
                {job.url && (
                  <a href={job.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline text-sm">
                    View Job →
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
