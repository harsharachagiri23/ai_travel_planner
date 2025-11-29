import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Hotel } from "lucide-react";

export default function TravelResult() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state || !state.travelPlan) {
    return (
      <div className="p-10 text-center">
        <p>No travel plan found.</p>
        <button
          onClick={() => navigate("/")}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
        >
          Go Back
        </button>
      </div>
    );
  }

  const travelPlan = state.travelPlan;

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="max-w-5xl mx-auto bg-white shadow-lg p-6 rounded-2xl">

        <button
          onClick={() => navigate("/")}
          className="mb-4 px-4 py-2 bg-blue-600 text-white rounded"
        >
          ← Back
        </button>

        <div className="flex items-start gap-4">
          <Hotel className="w-10 h-10 text-purple-600" />
          <div>
            <h2 className="text-3xl font-semibold">{travelPlan.destination}</h2>
            <p className="text-gray-600">
              {travelPlan.duration} days • {travelPlan.overview.travelers} traveler(s)
            </p>
          </div>
        </div>

        <div className="mt-6 grid md:grid-cols-3 gap-6">

          {/* Overview */}
          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold mb-2">Overview</h3>
            <p>Cost: {travelPlan.overview.totalCost}</p>
            <p>{travelPlan.overview.startDate} → {travelPlan.overview.endDate}</p>
          </div>

          {/* Attractions */}
          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold mb-2">Top Attractions</h3>
            {travelPlan.attractions.map(a => (
              <div key={a.name} className="mb-2">
                <div className="font-medium">{a.name}</div>
                <div className="text-sm text-gray-600">{a.type} • {a.bestTime}</div>
              </div>
            ))}
          </div>

          {/* Restaurants */}
          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold mb-2">Restaurants</h3>
            {travelPlan.restaurants.map(r => (
              <div key={r.name} className="mb-2">
                <div className="font-medium text-blue-600">{r.name}</div>
                <div className="text-sm text-gray-600">{r.cuisine} • {r.priceRange}</div>
              </div>
            ))}
          </div>

        </div>

        {/* Activities */}
        <div className="mt-6">
          <h3 className="font-semibold text-lg mb-2">Daily Activities</h3>
          <div className="space-y-4">
            {travelPlan.activities.map(act => (
              <div key={act.day} className="p-4 border rounded-lg">
                <div className="font-semibold">Day {act.day}</div>
                <div className="text-sm">{act.morning}</div>
                <div className="text-sm">{act.afternoon}</div>
                <div className="text-sm">{act.evening}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Tips */}
        <div className="mt-6">
          <h3 className="font-semibold">Local Tips</h3>
          <ul className="list-disc pl-5 text-sm mt-2">
            {travelPlan.localTips.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>

      </div>
    </div>
  );
}
