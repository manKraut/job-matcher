import { useState } from "react";

type Job = {
  title: string;
  locationAddress: string;
  owner: {
    name: string;
  };
};

export default function App() {
  const [location, setLocation] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`http://localhost:8000/api/jobs?location=${encodeURIComponent(location)}`);
      const data = await res.json();
      console.log("Fetched job data:", data);
  
      setJobs(data.result.jobs || []);
    } catch (err) {
      setError("Failed to fetch jobs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 px-6 py-12">
      <div className="max-w-xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">🔍 Open Job Matcher</h1>

        <div className="flex gap-2 mb-6">
          <input
            type="text"
            className="flex-grow border px-4 py-2 rounded-md"
            placeholder="Enter a city or country"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Search
          </button>
        </div>

        {loading && <p>Loading jobs...</p>}
        {error && <p className="text-red-500">{error}</p>}

        <ul className="space-y-4 mt-6">
          {jobs.map((job, idx) => (
            <li key={idx} className="p-4 border rounded-md bg-white shadow-sm">
              <h3 className="text-lg font-semibold">{job.title}</h3>
              <p className="text-sm text-gray-600">{job.owner?.name || "Unknown Company"} — {job.locationAddress}</p>
              <a
                href="#"
                className="text-blue-500 hover:underline text-sm"
                onClick={(e) => e.preventDefault()}
              >
                View Job →
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
