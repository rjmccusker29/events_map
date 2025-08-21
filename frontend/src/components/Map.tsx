import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import { createRoot } from 'react-dom/client';
import 'mapbox-gl/dist/mapbox-gl.css';
import EventPopup from './EventPopup';

const Map = () => {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<mapboxgl.Map | null>(null);
    const popup = useRef<mapboxgl.Popup | null>(null);

    useEffect(() => {
        if (map.current || !mapContainer.current) return;

        mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/dark-v11',
            center: [0,20],
            zoom: 2,
        });

        map.current.on('style.load', () => {
            const style = map.current?.getStyle();
            if (style?.layers) {
                style.layers.forEach(layer => {
                    // Hide layers that contain labels/text
                    if (layer.type === 'symbol' && 
                        (layer.id.includes('label') || 
                         layer.id.includes('place') ||
                         layer.id.includes('poi') ||
                         layer.id.includes('road') ||
                         layer.id.includes('transit'))) {
                        map.current?.setLayoutProperty(layer.id, 'visibility', 'none');
                    }
                });
            }

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
                    'text-size': 15,
                    'text-anchor': 'center',
                },
                paint: {
                    'text-color': '#ffffff',
                    'text-halo-color': '#000000',
                    'text-halo-width': 1
                }
            });

            // Add click event listener for the events layer
            map.current?.on('click', 'events-layer', (e) => {
                if (!map.current || !e.features || e.features.length === 0) return;

                const feature = e.features[0];
                const properties = feature.properties;

                if (!properties) return;

                // Close existing popup if any
                if (popup.current) {
                    popup.current.remove();
                }

                const coordinates = (feature.geometry as any).coordinates.slice();

                // div element for the popup content
                const popupContainer = document.createElement('div');

                const root = createRoot(popupContainer);
                root.render(
                    <EventPopup
                        name={properties.name}
                        date={properties.date}
                        wikiUrl={properties.wiki_url}
                        onClose={() => {
                            if (popup.current) {
                                popup.current.remove();
                            }
                        }}
                    />
                );

                popup.current = new mapboxgl.Popup({
                    closeButton: false, 
                    closeOnClick: false,
                    maxWidth: '300px',
                    className: 'custom-popup'
                })
                    .setLngLat(coordinates)
                    .setDOMContent(popupContainer)
                    .addTo(map.current);

                popup.current.on('close', () => {
                    root.unmount();
                });
            });

            // change the cursor to a pointer when hovering over the events layer
            map.current?.on('mouseenter', 'events-layer', () => {
                if (map.current) {
                    map.current.getCanvas().style.cursor = 'pointer';
                }
            });

            map.current?.on('mouseleave', 'events-layer', () => {
                if (map.current) {
                    map.current.getCanvas().style.cursor = '';
                }
            });

            map.current?.resize();
        });

        return () => {
            if (popup.current) {
                popup.current.remove();
                popup.current = null;
            }
            if (map.current) {
                map.current.remove();
                map.current = null;
            }
        };
    }, []);

    return <div ref={mapContainer} className="h-screen w-full" />;
};

export default Map;