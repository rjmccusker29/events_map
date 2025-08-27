import React from 'react';
import dayjs from 'dayjs';

interface EventPopupProps {
    name: string;
    date: string;
    views: number;
    wikiUrl: string;
    onClose: () => void;
}

const EventPopup: React.FC<EventPopupProps> = ({ name, date, views, wikiUrl, onClose }) => {
    const formattedDate = dayjs(date).format('MMMM D, YYYY');

    return (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 relative max-w-xs">
            <button
                onClick={onClose}
                className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-xl leading-none p-1"
                aria-label="Close popup"
            >
                ×
            </button>
        
            <div className="p-4">
                <h3 className="font-semibold text-gray-900 text-lg mb-2 leading-tight pr-4">{name}</h3>
                <p className="text-gray-600 text-sm mb-1">{formattedDate}</p>
                <p className="text-gray-600 text-sm mb-3">{views} views</p>
                <a
                    href={wikiUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block text-blue-600 hover:text-blue-800 text-sm font-medium hover:underline transition-colors"
                >
                    Wikipedia
                </a>
            </div>
        </div>
    );
}

export default EventPopup;