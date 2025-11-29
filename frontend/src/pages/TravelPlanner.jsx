import React, { useState } from 'react';
import { Plane, Users, Calendar, DollarSign, Clock } from 'lucide-react';
import { useNavigate } from "react-router-dom";

export default function TravelPlanner() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    destination: '',
    startDate: '',
    endDate: '',
    travelers: 1,
    budget: '',
    interests: []
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const interestOptions = [
    'Adventure', 'Culture', 'Food', 'Nature',
    'History', 'Relaxation', 'Shopping', 'Nightlife'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const toggleInterest = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.destination || !formData.startDate || !formData.endDate) {
      setError("Please fill in all required fields");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/api/plan-trip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      if (!res.ok) throw new Error("Backend not available");

      const data = await res.json();

      navigate("/result", { state: { travelPlan: data } });

    } catch {
      const demo = generateDemoData(formData);
      navigate("/result", { state: { travelPlan: demo } });
    } finally {
      setLoading(false);
    }
  };

  const generateDemoData = (data) => ({
    destination: data.destination,
    duration: calculateDays(data.startDate, data.endDate),
    overview: {
      totalCost: data.budget || "2500",
      travelers: data.travelers,
      startDate: data.startDate,
      endDate: data.endDate
    },
    attractions: [
      { name: "Golden Gate Bridge", type: "Landmark", bestTime: "Morning" },
      { name: "Alcatraz Island", type: "Historical", bestTime: "Afternoon" }
    ],
    restaurants: [
      { name: "Tartine Bakery", cuisine: "Bakery", priceRange: "$$" },
      { name: "Zuni Café", cuisine: "Mediterranean", priceRange: "$$$" }
    ],
    accommodation: [
      { hotel: "Marriott Downtown", pricePerNight: 189 }
    ],
    activities: [
      { day: 1, morning: "Bridge", afternoon: "Wharf", evening: "Dinner" },
      { day: 2, morning: "Alcatraz", afternoon: "Chinatown", evening: "Sunset" }
    ],
    localTips: [
      "Dress in layers",
      "Use public transport"
    ]
  });

  const calculateDays = (s, e) => {
    const diff = new Date(e) - new Date(s);
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 px-4 py-10">
      <div className="max-w-5xl mx-auto">
        
        {/* Title */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Plane className="w-12 h-12 text-blue-600" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              AI Travel Planner
            </h1>
          </div>
          <p className="text-gray-600 text-lg">Let's make your trip memorable</p>
        </div>

        {/* FORM */}
        <form className="bg-white shadow-xl rounded-2xl p-8" onSubmit={handleSubmit}>
          <div className="grid md:grid-cols-2 gap-6">

            {/* Destination */}
            <div>
              <label className="font-semibold text-sm">Destination *</label>
              <input
                type="text"
                name="destination"
                className="w-full mt-1 px-4 py-3 border rounded-lg"
                value={formData.destination}
                onChange={handleInputChange}
              />
            </div>

            {/* Travelers */}
            <div>
              <label className="font-semibold text-sm">
                <Users className="inline w-4 h-4 mr-1" /> Travelers
              </label>
              <input
                type="number"
                name="travelers"
                min="1"
                className="w-full mt-1 px-4 py-3 border rounded-lg"
                value={formData.travelers}
                onChange={handleInputChange}
              />
            </div>

            {/* Start date */}
            <div>
              <label className="font-semibold text-sm">
                <Calendar className="inline w-4 h-4 mr-1" /> Start Date
              </label>
              <input
                type="date"
                name="startDate"
                className="w-full mt-1 px-4 py-3 border rounded-lg"
                value={formData.startDate}
                onChange={handleInputChange}
              />
            </div>

            {/* End date */}
            <div>
              <label className="font-semibold text-sm">
                <Calendar className="inline w-4 h-4 mr-1" /> End Date
              </label>
              <input
                type="date"
                name="endDate"
                className="w-full mt-1 px-4 py-3 border rounded-lg"
                value={formData.endDate}
                onChange={handleInputChange}
              />
            </div>

            {/* Budget */}
            <div>
              <label className="font-semibold text-sm">
                <DollarSign className="inline w-4 h-4 mr-1" /> Budget
              </label>
              <input
                type="text"
                name="budget"
                className="w-full mt-1 px-4 py-3 border rounded-lg"
                value={formData.budget}
                onChange={handleInputChange}
              />
            </div>

            {/* Interests */}
            <div>
              <label className="font-semibold text-sm">Interests</label>
              <div className="flex flex-wrap gap-2 mt-2">
                {interestOptions.map(opt => {
                  const active = formData.interests.includes(opt);
                  return (
                    <button
                      type="button"
                      key={opt}
                      onClick={() => toggleInterest(opt)}
                      className={`px-3 py-1 rounded-full border ${
                        active ? "bg-blue-600 text-white" : "bg-white text-gray-700"
                      }`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Submit */}
          <div className="mt-6 flex items-center justify-between">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Generating..." : "Generate Travel Plan"}
            </button>

            <p className="text-gray-500 text-sm flex gap-1 items-center">
              <Clock className="w-4 h-4" /> Quick demo
            </p>
          </div>

          {error && <p className="text-red-600 mt-2 text-sm">{error}</p>}
        </form>
      </div>
    </div>
  );
}
