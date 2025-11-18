import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import {
  createBrowserRouter,
  RouterProvider,
  useNavigate,
  useSearchParams,
  Link,
} from 'react-router-dom';

// Tailwind CSS is assumed to be set up in your Vite project.
// If not, follow the Vite Tailwind installation guide.

//==============================================================================
// 1. SEARCH PAGE COMPONENT (The Form)
//==============================================================================
function SearchPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    lastName: '',
    firstName: '',
    year: '',
    county: 'All',
    record_type: 'BIRTH', // Default to birth records
  });
  const [activeTab, setActiveTab] = useState('BIRTH');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleTabClick = (recordType) => {
    setActiveTab(recordType);
    setFormData((prev) => ({ ...prev, record_type: recordType }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Create query parameters from the form state
    // This will turn { lastName: 'Smith' } into 'lastName=Smith'
    const params = new URLSearchParams();
    
    // Only add parameters if they have a value
    if (formData.firstName) params.append('first_name', formData.firstName);
    if (formData.lastName) params.append('last_name', formData.lastName);
    if (formData.year) params.append('year', formData.year);
    if (formData.county && formData.county !== 'All') params.append('county', formData.county);
    if (formData.record_type) params.append('record_type', formData.record_type);

    // Navigate to the results page with the query parameters
    navigate(`/results?${params.toString()}`);
  };

  // Tab styling
  const tabClass = (type) =>
    `px-4 py-2 font-semibold rounded-full cursor-pointer transition-all duration-200 ${
      activeTab === type
        ? 'bg-[#115e5c] text-white'
        : 'text-gray-600 hover:bg-gray-200'
    }`;

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-2xl p-8 bg-white rounded-lg shadow-lg">
        <h1 className="text-4xl font-bold text-center text-[#115e5c] mb-6">
          Search Records
        </h1>

        {/* --- TABS --- */}
        <nav className="flex justify-center space-x-2 mb-8">
          <button
            type="button"
            className={tabClass('BIRTH')}
            onClick={() => handleTabClick('BIRTH')}
          >
            BIRTH RECORDS
          </button>
          <button
            type="button"
            className={tabClass('DEATH')}
            onClick={() => handleTabClick('DEATH')}
          >
            DEATH RECORDS
          </button>
          <button
            type="button"
            className={tabClass('MARRIAGE')}
            onClick={() => handleTabClick('MARRIAGE')}
          >
            MARRIAGE RECORDS
          </button>
        </nav>

        {/* --- SEARCH FORM --- */}
        <form className="grid grid-cols-1 md:grid-cols-2 gap-6" onSubmit={handleSubmit}>
          {/* Last Name */}
          <div>
            <label
              htmlFor="lastName"
              className="block text-sm font-medium text-gray-700"
            >
              Last Name
            </label>
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#115e5c] focus:border-[#115e5c] sm:text-sm"
            />
          </div>
          
          {/* First Name */}
          <div>
            <label
              htmlFor="firstName"
              className="block text-sm font-medium text-gray-700"
            >
              First Name
            </label>
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#115e5c] focus:border-[#115e5c] sm:text-sm"
            />
          </div>

          {/* Birth Year */}
          <div>
            <label
              htmlFor="year"
              className="block text-sm font-medium text-gray-700"
            >
              Birth Year
            </label>
            <input
              type="text"
              id="year"
              name="year"
              value={formData.year}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#115e5c] focus:border-[#115e5c] sm:text-sm"
            />
          </div>

          {/* County */}
          <div>
            <label
              htmlFor="county"
              className="block text-sm font-medium text-gray-700"
            >
              County
            </label>
            <select
              id="county"
              name="county"
              value={formData.county}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-[#115e5c] focus:border-[#115e5c] sm:text-sm"
            >
              <option>All</option>
              <option>St. Clair</option>
              <option>Madison</option>
              <option>Monroe</option>
              <option>Clinton</option>
              {/* Add more counties as needed */}
            </select>
          </div>

          {/* --- SUBMIT BUTTON --- */}
          <div className="md:col-span-2">
            <button
              type="submit"
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-full shadow-sm text-lg font-bold text-white bg-[#115e5c] hover:bg-[#0e4b48] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#115e5c] transition-all duration-200"
            >
              SEARCH
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

//==============================================================================
// 2. RESULTS PAGE COMPONENT (The Table)
//==============================================================================
function ResultsPage() {
  const [searchParams] = useSearchParams();
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get the record type from the URL, default to 'Birth'
  const recordType = (searchParams.get('record_type') || 'Birth').toLowerCase();

  useEffect(() => {
    // This function runs when the page loads
    const fetchResults = async () => {
      setIsLoading(true);
      setError(null);
      
      // Get the full query string from the URL
      const queryString = searchParams.toString();

      // Construct the API URL. This relative path will work 
      // on both localhost and your deployed server.
      const apiUrl = `/iivrd?${queryString}`;

      try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setResults(data.results); // Assuming your Django API returns { "results": [...] }
      } catch (e) {
        console.error("Fetch error:", e);
        setError("Failed to fetch results. Please check the connection or server status.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [searchParams]); // Re-run this effect if the search parameters change

  return (
    <div className="p-4 md:p-10 min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-[#115e5c]">Search Results</h1>
          <Link
            to="/"
            className="px-4 py-2 font-semibold rounded-full text-white bg-[#115e5c] hover:bg-[#0e4b48] transition-all duration-200"
          >
            New Search
          </Link>
        </div>

        {/* --- LOADING STATE --- */}
        {isLoading && (
          <div className="text-center py-10">
            <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full border-t-[#115e5c] border-gray-200" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-2 font-medium text-gray-600">Loading results...</p>
          </div>
        )}

        {/* --- ERROR STATE --- */}
        {error && (
          <div className="text-center py-10 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}

        {/* --- RESULTS TABLE --- */}
        {!isLoading && !error && (
          <>
            {results.length === 0 ? (
              <p className="text-center py-10 text-gray-500">No results found for your query.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {/* Note: I am using the columns from your DB schema (image_990813.png) */}
                      {/* Your mockup shows a full date, but your DB schema only has 'year'. */}
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider"
                      >
                        Last Name
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider"
                      >
                        First Name
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider"
                      >
                        Year of {recordType}
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider"
                      >
                        County
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.map((record) => (
                      <tr key={record.record_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 underline cursor-pointer">
                          {record.last_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 underline cursor-pointer">
                          {record.first_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {record.year}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {record.county}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

//==============================================================================
// 3. ROUTER SETUP (This is the changed part)
//==============================================================================
const router = createBrowserRouter(
  [
    {
      path: '/',
      element: <SearchPage />,
    },
    {
      path: '/results',
      element: <ResultsPage />,
    },
  ],
  {
    // This new `basename` property tells React Router
    // that the app lives at '/iivrd'
    basename: '/iivrd',
  }
);

//==============================================================================
// 4. APP ENTRY POINT
//==============================================================================
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);