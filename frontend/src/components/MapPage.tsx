import { useState } from 'react';
import { Calendar, Info } from 'lucide-react';
import Map from './Map';
import TimeFilter from './TimeFilter';
import { useNavigate } from 'react-router-dom';

const MapPage = () => {
    const [startDate, setStartDate] = useState<string | null>(null);
    const [endDate, setEndDate] = useState<string | null>(null);
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const navigate = useNavigate();

    const handleFilterChange = (newStartDate: string | null, newEndDate: string | null) => {
        setStartDate(newStartDate);
        setEndDate(newEndDate);
    };

    const getActiveFilterText = () => {
        if (!startDate && !endDate) return null;
        
        const start = startDate ? new Date(startDate).getFullYear() : 'Beginning';
        const end = endDate ? new Date(endDate).getFullYear() : 'Present';
        
        return `${start} - ${end}`;
    };

    const activeFilterText = getActiveFilterText();

    return (
        <div className="w-full h-full relative">
            <div className="absolute top-4 left-4 right-4 z-30 flex justify-between items-start">
                <button
                    onClick={() => setIsFilterOpen(!isFilterOpen)}
                    className={`
                        flex items-center gap-2 px-4 py-3 
                        bg-black/40 backdrop-blur-md border border-white/10
                        rounded-xl shadow-lg transition-all duration-200
                        hover:bg-black/50 hover:border-white/20
                        ${activeFilterText ? 'text-blue-100 border-blue-400/30' : 'text-white/90'}
                        md:relative
                    `}
                >
                    <Calendar className="w-5 h-5" />
                    <div className="hidden sm:block">
                        <span className="font-medium">
                            {activeFilterText || 'All Time'}
                        </span>
                        {activeFilterText && (
                            <div className="text-xs text-white/60">
                                Click to change
                            </div>
                        )}
                    </div>
                </button>

                {/* About Button */}
                <button
                    onClick={() => navigate('/about')}
                    className="
                        flex items-center gap-2 px-4 py-3
                        bg-black/40 backdrop-blur-md border border-white/10
                        rounded-xl shadow-lg text-white/90
                        hover:bg-black/50 hover:border-white/20 hover:text-white
                        transition-all duration-200
                    "
                >
                    <Info className="w-5 h-5" />
                    <span className="hidden sm:inline font-medium">About</span>
                </button>
            </div>

            {activeFilterText && (
                <div className="absolute top-20 left-4 z-20 sm:hidden">
                    <div className="
                        px-3 py-2 bg-blue-500/20 backdrop-blur-md 
                        border border-blue-400/30 rounded-lg
                        text-blue-100 text-sm font-medium
                    ">
                        {activeFilterText}
                    </div>
                </div>
            )}

            <TimeFilter
                isOpen={isFilterOpen}
                onClose={() => setIsFilterOpen(false)}
                onFilterChange={handleFilterChange}
            />

            <Map startDate={startDate} endDate={endDate} />
        </div>
    );
};

export default MapPage;