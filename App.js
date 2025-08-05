import React from "react";
import MapComponent from "./MapComponent";

// Main app component rendering a header and the map component
function App() {
  return (
    <div>
      <h2 style={{ textAlign: "center" }}>Riyadh Neighborhoods Map</h2>
      <MapComponent />
    </div>
  );
}

export default App;


//Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
