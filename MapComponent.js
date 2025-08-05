import React, { useEffect, useState } from "react";
import Map, { Marker, Popup } from "react-map-gl/mapbox"; // Import Mapbox map and components
import "mapbox-gl/dist/mapbox-gl.css";

// Your Mapbox access token (replace with your own)
const MAPBOX_TOKEN =
  "pk.eyJ1IjoiaWZhcmFoIiwiYSI6ImNtY24xaDNwYjBua20ybHFxM2J0a3h0bm0ifQ.2ddJkeYNsyB7Ynedk6XAFw";

const MapComponent = () => {
  // State to store neighborhoods data fetched from API
  const [neighborhoods, setNeighborhoods] = useState([]);
  // State to control which neighborhood's popup is open
  const [popupInfo, setPopupInfo] = useState(null);
  // State to store the selected indicator (default: HCI)
  const [indicator, setIndicator] = useState("HCI");

  // useEffect to fetch neighborhoods data whenever the selected indicator changes
  useEffect(() => {
    fetch("http://localhost:5000/api/neighborhoods-data")
      .then((res) => res.json()) // Parse response JSON
      .then((data) => {
        let sorted;

        // Sort data based on selected indicator
        if (indicator === "HCI") {
          // Sort descending by HCI value
          sorted = [...data].sort((a, b) => b.HCI - a.HCI);
        } else if (indicator === "CDD") {
          // Sort ascending by CDD value
          sorted = [...data].sort((a, b) => a.CDD - b.CDD);
        } else if (indicator === "HDD") {
          // Sort ascending by HDD value
          sorted = [...data].sort((a, b) => a.HDD - b.HDD);
        } else if (indicator === "public_stations") {
          // Sort descending by public stations count
          sorted = [...data].sort((a, b) => b.public_stations - a.public_stations);
        } else if (indicator === "population_density") {
          // Sort descending by population density
          sorted = [...data].sort((a, b) => b.population_density - a.population_density);
        } else {
          // If indicator unknown, keep original order
          sorted = [...data];
        }

        // Add a 'Rank' property based on sorted order (starting from 1)
        const ranked = sorted.map((n, index) => ({
          ...n,
          Rank: index + 1,
        }));

        // Update neighborhoods state with ranked data
        setNeighborhoods(ranked);
      })
      .catch((err) => console.error("Fetch error:", err)); // Handle fetch errors
  }, [indicator]); // Dependency array: runs whenever 'indicator' changes

  // Handler function for changing selected indicator from dropdown
  const handleIndicatorChange = (e) => {
    setIndicator(e.target.value);
    setPopupInfo(null); // Close any open popup when changing indicator
  };

  // Get color legend for the selected indicator
  const legend = getLegend(indicator);

  return (
    <div style={{ position: "relative" }}>
      {/* Dropdown to select indicator */}
      <div style={dropdownStyle}>
        <label style={{ marginRight: 10 }}>Select Indicator:</label>
        <select value={indicator} onChange={handleIndicatorChange}>
          <option value="HCI">HCI</option>
          <option value="CDD">CDD</option>
          <option value="HDD">HDD</option>
          <option value="public_stations">Public Stations</option>
          <option value="population_density">Population Density</option>
        </select>
      </div>

      {/* Map component */}
      <Map
        mapboxAccessToken={MAPBOX_TOKEN}
        initialViewState={{ longitude: 46.7, latitude: 24.7, zoom: 10 }}
        style={{ width: "100%", height: "100vh" }}
        mapStyle="mapbox://styles/mapbox/streets-v11"
      >
        {/* Render a Marker for each neighborhood */}
        {neighborhoods.map((n, i) => (
          <Marker key={i} longitude={n.Longitude_x} latitude={n.Latitude_x}>
            <div
              style={{ display: "flex", alignItems: "center", cursor: "pointer" }}
              onClick={(e) => {
                e.stopPropagation(); // Prevent map click event
                setPopupInfo(n); // Open popup for this neighborhood
              }}
            >
              <div
                style={{
                  width: 20,
                  height: 20,
                  backgroundColor: getColor(indicator, n[indicator]),
                  borderRadius: "50%",
                  border: "2px solid white",
                }}
              />
              <div
                style={{
                  marginLeft: 6,
                  fontWeight: "bold",
                  fontSize: 14,
                  color: "#000",
                  userSelect: "none",
                }}
              >
                {n.Rank}
              </div>
            </div>
          </Marker>
        ))}

        {/* Popup showing detailed info when a marker is clicked */}
        {popupInfo && (
          <Popup
            longitude={Number(popupInfo.Longitude_x)}
            latitude={Number(popupInfo.Latitude_x)}
            anchor="top"
            onClose={() => setPopupInfo(null)}
            closeOnClick={false}
          >
            <div style={{ minWidth: 150 }}>
              <strong>{popupInfo.Neighborhood}</strong>
              <br />
              Population: {popupInfo.Population_x}
              <br />
              Area: {popupInfo.Area_km2} km²
              <br />
              {indicator}:{" "}
              {typeof popupInfo[indicator] === "number"
                ? popupInfo[indicator].toFixed(2)
                : popupInfo[indicator]}
              <br />
              Rank: {popupInfo.Rank}
            </div>
          </Popup>
        )}
      </Map>

      {/* Legend showing color meaning */}
      <div style={legendStyle}>
        {legend.items.map((item, index) => (
          <LegendItem key={index} color={item.color} label={item.label} />
        ))}

        {/* Optional note for legend */}
        {legend.note && (
          <div
            style={{
              marginTop: 10,
              fontStyle: "italic",
              fontSize: 12,
              color: "#444",
              maxWidth: 180,
              lineHeight: "1.2em",
            }}
          >
            {legend.note}
          </div>
        )}
      </div>
    </div>
  );
};

// Function to return color for marker based on indicator value
const getColor = (indicator, value) => {
  switch (indicator) {
    case "HCI":
      if (value >= 25) return "green";
      if (value > 10) return "yellow";
      return "orange";

    case "CDD":
      if (value < 4) return "green";
      if (value < 12) return "yellow";
      return "orange";

    case "HDD":
      if (value < 2.5) return "green";
      if (value < 5) return "yellow";
      return "orange";

    case "public_stations":
      if (value < 15) return "orange";
      if (value < 40) return "yellow";
      return "green";

    case "population_density":
      if (value < 7000) return "green";
      if (value < 14000) return "yellow";
      return "orange";

    default:
      return "gray";
  }
};

// Function to return legend info (colors and descriptions) based on selected indicator
const getLegend = (indicator) => {
  switch (indicator) {
    case "HCI":
      return {
        items: [
          { color: "green", label: "High coverage" },
          { color: "yellow", label: "Medium coverage" },
          { color: "orange", label: "Low coverage" },
        ],
        note: "Higher values indicate better coverage.",
      };
    case "CDD":
      return {
        items: [
          { color: "green", label: "Low CDD" },
          { color: "yellow", label: "Medium CDD" },
          { color: "orange", label: "High CDD" },
        ],
        note: "Higher values indicate greater cooling demand.",
      };
    case "HDD":
      return {
        items: [
          { color: "green", label: "Low HDD" },
          { color: "yellow", label: "Medium HDD" },
          { color: "orange", label: "High HDD" },
        ],
        note: "Higher values indicate greater heating demand.",
      };
    case "public_stations":
      return {
        items: [
          { color: "orange", label: "Few stations" },
          { color: "yellow", label: "Moderate stations" },
          { color: "green", label: "Many stations" },
        ],
        note: "Higher values indicate more public stations.",
      };
    case "population_density":
      return {
        items: [
          { color: "green", label: "Low density" },
          { color: "yellow", label: "Medium density" },
          { color: "orange", label: "High density" },
        ],
        note: "Higher values indicate greater population density.",
      };
    default:
      return { items: [], note: "" };
  }
};

// Component to render a single legend item (colored circle + label)
const LegendItem = ({ color, label }) => (
  <div style={{ display: "flex", alignItems: "center", marginBottom: 6 }}>
    <span
      style={{
        width: 12,
        height: 12,
        borderRadius: "50%",
        backgroundColor: color,
        display: "inline-block",
        marginRight: 8,
      }}
    />
    {label}
  </div>
);

// Styles for the dropdown menu
const dropdownStyle = {
  position: "absolute",
  top: 20,
  left: 20,
  backgroundColor: "white",
  padding: "10px 15px",
  borderRadius: "10px",
  boxShadow: "0 0 10px rgba(0,0,0,0.2)",
  zIndex: 2,
  fontSize: "14px",
};

// Styles for the legend container
const legendStyle = {
  position: "absolute",
  top: 80,
  right: 20,
  backgroundColor: "white",
  padding: "10px 15px",
  borderRadius: "10px",
  boxShadow: "0 0 10px rgba(0,0,0,0.2)",
  fontSize: "14px",
  zIndex: 1,
};

export default MapComponent;
