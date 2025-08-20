import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import 'mapbox-gl/dist/mapbox-gl.css';

const Map = () => {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<mapboxgl.Map | null>(null);

    useEffect(() => {
        if (map.current || !mapContainer.current) return;

        mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/dark-v11',
            center: [0,20],
            zoom: 2,
        });

        map.current.on('load', () => {
            map.current?.addSource('events-source', {
                type: 'vector',
                tiles: ['http://localhost:8000/tiles/{z}/{x}/{y}.mvt'],
            });

            map.current?.addLayer({
                id: 'events-layer',
                type: 'symbol',
                source: 'events-source',
                'source-layer': 'events',
                layout: {
                    'text-field': ['get', 'name'],
                    'text-font': ['Open Sans Regular', 'Arial Unicode MS Regular'],
                    'text-size': 12,
                    'text-anchor': 'center',
                },
                paint: {
                    'text-color': '#ffffff',
                    'text-halo-color': '#000000',
                    'text-halo-width': 1
                }
            });

            map.current?.resize();
        });

        return () => {
            if (map.current) {
                map.current.remove();
                map.current = null;
            }
        };
    }, []);

    return <div ref={mapContainer} className="h-screen w-full" />;
};

export default Map;