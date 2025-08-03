import React, { useEffect, useState } from "react";
import Map, { Marker, Popup } from "react-map-gl/mapbox";
import "mapbox-gl/dist/mapbox-gl.css";

const MAPBOX_TOKEN =
  "pk.eyJ1IjoiaWZhcmFoIiwiYSI6ImNtY24xaDNwYjBua20ybHFxM2J0a3h0bm0ifQ.2ddJkeYNsyB7Ynedk6XAFw";

const MapComponent = () => {
  const [neighborhoods, setNeighborhoods] = useState([]);
  const [popupInfo, setPopupInfo] = useState(null);
  const [indicator, setIndicator] = useState("HCI"); // افتراضي HCI

  useEffect(() => {
    fetch("http://localhost:5000/api/neighborhoods-data")
      .then((res) => res.json())
      .then((data) => {
        let sorted;
        if (indicator === "HCI") {
          sorted = [...data].sort((a, b) => b.HCI - a.HCI);
        } else if (indicator === "CDD") {
          sorted = [...data].sort((a, b) => a.CDD - b.CDD);
        } else if (indicator === "HDD") {
          sorted = [...data].sort((a, b) => a.HDD - b.HDD); // تصاعدي مثل CDD
        } else if (indicator === "public_stations") {
          sorted = [...data].sort(
            (a, b) => b.public_stations - a.public_stations
          );
        } else if (indicator === "population_density") {
          sorted = [...data].sort(
            (a, b) => b.population_density - a.population_density
          );
        } else {
          sorted = [...data];
        }

        const ranked = sorted.map((n, index) => ({
          ...n,
          Rank: index + 1,
        }));

        setNeighborhoods(ranked);
      })
      .catch((err) => console.error("Fetch error:", err));
  }, [indicator]);

  const handleIndicatorChange = (e) => {
    setIndicator(e.target.value);
    setPopupInfo(null);
  };

  const legend = getLegend(indicator);

  return (
    <div style={{ position: "relative" }}>
      {/* Dropdown اختيار المؤشر */}
      <div style={dropdownStyle}>
        <label style={{ marginRight: 10 }}>اختر المؤشر:</label>
        <select value={indicator} onChange={handleIndicatorChange}>
          <option value="HCI">HCI</option>
          <option value="CDD">CDD</option>
          <option value="HDD">HDD</option>
          <option value="public_stations">Public stations</option>
          <option value="population_density">Population density</option>
        </select>
      </div>

      {/* الخريطة */}
      <Map
        mapboxAccessToken={MAPBOX_TOKEN}
        initialViewState={{ longitude: 46.7, latitude: 24.7, zoom: 10 }}
        style={{ width: "100%", height: "100vh" }}
        mapStyle="mapbox://styles/mapbox/streets-v11"
      >
        {neighborhoods.map((n, i) => (
          <Marker key={i} longitude={n.Longitude_x} latitude={n.Latitude_x}>
            <div
              style={{ display: "flex", alignItems: "center", cursor: "pointer" }}
              onClick={(e) => {
                e.stopPropagation();
                setPopupInfo(n);
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

      {/* مفتاح الألوان */}
      <div style={legendStyle}>
        {legend.items.map((item, index) => (
          <LegendItem key={index} color={item.color} label={item.label} />
        ))}

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

// اللون حسب المؤشر
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

// المفتاح التوضيحي
const getLegend = (indicator) => {
  switch (indicator) {
    case "HCI":
      return {
        items: [
          { color: "green", label: "تغطية مرتفعة" },
          { color: "yellow", label: "تغطية متوسطة" },
          { color: "orange", label: "تغطية منخفضة" },
        ],
        note: "كلما ارتفع المؤشر كانت التغطية أفضل",
      };
    case "CDD":
      return {
        items: [
          { color: "green", label: "منخفض CDD" },
          { color: "yellow", label: "متوسط CDD" },
          { color: "orange", label: "مرتفع CDD" },
        ],
        note: "كلما ارتفع المؤشر أصبح الحي بحاجة لتغطية تبريد أكبر",
      };
    case "HDD":
      return {
        items: [
          { color: "green", label: "منخفض HDD" },
          { color: "yellow", label: "متوسط HDD" },
          { color: "orange", label: "مرتفع HDD" },
        ],
        note: "كلما ارتفع المؤشر زادت الحاجة للتدفئة",
      };
    case "public_stations":
      return {
        items: [
          { color: "orange", label: "عدد محطات قليل" },
          { color: "yellow", label: "عدد محطات متوسط" },
          { color: "green", label: "عدد محطات مرتفع" },
        ],
        note: "كلما ارتفع المؤشر كانت المحطات أكثر",
      };
    case "population_density":
      return {
        items: [
          { color: "green", label: "كثافة منخفضة" },
          { color: "yellow", label: "كثافة متوسطة" },
          { color: "orange", label: "كثافة عالية" },
        ],
        note: "كلما ارتفعت الكثافة السكانية زادت الاحتياجات",
      };
    default:
      return { items: [], note: "" };
  }
};

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
