import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import type { Recommendation } from "../types/recommendation";
import L from "leaflet";
import { useEffect, useState, useRef } from "react";
import { CircleMarker } from "react-leaflet";
import "leaflet-routing-machine";
import "leaflet-routing-machine/dist/leaflet-routing-machine.css";
import type { Map as LeafletMap } from "leaflet";
import { useMapEvents } from "react-leaflet";

// Fix marker icon issue (Leaflet + Vite)
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

interface Props {
  recommendations: Recommendation[];
}

export default function MapView({ recommendations }: Props) {
  

  
  const firstWithCoords = recommendations.find(
  (r) => r.event.latitude != null && r.event.longitude != null
  );
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);

  const center: [number, number] =
    userLocation ||
      (firstWithCoords
        ? [firstWithCoords.event.latitude!, firstWithCoords.event.longitude!]
        : [-1.286389, 36.817223]);
  
  const [routeControl, setRouteControl] = useState<any>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const [routeInfo, setRouteInfo] = useState<{distanceKm: number;durationMin: number;} | null>(null);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  if (recommendations.length === 0) return null;
  
  
  
  
  useEffect(() => {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation([pos.coords.latitude, pos.coords.longitude]);
      },
      (err) => {
        console.log("Location permission denied or unavailable", err);
      }
    );
  }, []);

  function MapClickHandler({ onMapClick }: { onMapClick: () => void }) {
    useMapEvents({
      click: () => {
        onMapClick();
      },
    });
    return null;
  }
  
  function drawRoute(eventId: string, lat: number, lng: number) {
    const map = mapRef.current;
    if (!map || !userLocation) return;

    setSelectedEventId(eventId);

    // Remove previous route
    if (routeControl) {
      map.removeControl(routeControl);
    }

    const control = (L as any).Routing.control({
      waypoints: [
        L.latLng(userLocation[0], userLocation[1]),
        L.latLng(lat, lng),
      ],
      lineOptions: {
        styles: [{ color: "#2563EB", weight: 4 }],
      },
      addWaypoints: false,
      draggableWaypoints: false,
      routeWhileDragging: false,
      show: false,
      fitSelectedRoutes: true,
    }).addTo(map);

    // When route is calculated
    control.on("routesfound", function (e: any) {
      const route = e.routes[0];

      // Distance (meters → km)
      const distanceKm = route.summary.totalDistance / 1000;

      // Duration (seconds → minutes)
      const durationMin = route.summary.totalTime / 60;

      setRouteInfo({
        distanceKm: Number(distanceKm.toFixed(1)),
        durationMin: Math.round(durationMin),
      });

      // Auto-fit bounds
      const bounds = L.latLngBounds(route.coordinates);
      map.fitBounds(bounds, {
        padding: [40, 40],
        animate: true,
        duration: 1,
      });
    });

    setRouteControl(control);
  }
  
  function clearRoute() {
  const map = mapRef.current;
  if (!map) return;

  if (routeControl) {
    map.removeControl(routeControl);
    setRouteControl(null);
  }

  setRouteInfo(null);
  setSelectedEventId(null);
  }


  return (
    <MapContainer
      center={center}
      zoom={12}
      ref={mapRef}
      style={{ height: "400px", width: "100%", marginTop: 20 }} 
      
    >
      <MapClickHandler onMapClick={clearRoute} />

      {userLocation && (
        <CircleMarker
          center={userLocation}
          radius={8}
          pathOptions={{
          color: "#2563EB",
          fillColor: "#3B82F6",
          fillOpacity: 0.8,
          }}
        >
          <Popup>Your location</Popup>
        </CircleMarker>
      )}


      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      {recommendations.map((rec) => {
        const { event } = rec;

        if (event.latitude == null || event.longitude == null) return null;

        return (
          <Marker
            key={event.id}
            position={[event.latitude, event.longitude]}
            eventHandlers={{
              click: () => drawRoute(event.id, event.latitude!, event.longitude!),
            }}
          >
            <Popup>
              <strong>{event.name}</strong>
              <br />
              {event.date} • {event.genre}

              {routeInfo && selectedEventId === event.id && (
                <>
                <br />
                <span style={{ color: "#2563EB", fontWeight: 600 }}>
                  🚗 {routeInfo.durationMin} min • {routeInfo.distanceKm} km
                </span>
              </>
              )}
            </Popup>


          </Marker>
        );
      })}
    </MapContainer>
  );
}