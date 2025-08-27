import { useState, useEffect } from 'react';
import { X, Clock } from 'lucide-react';

interface TimeFilterProps {
    onFilterChange: (startDate: string | null, endDate: string | null) => void;
    isOpen: boolean;
    onClose: () => void;
}

const TimeFilter = ({ onFilterChange, isOpen, onClose }: TimeFilterProps) => {
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');
    const [activePreset, setActivePreset] = useState<string | null>(null);

    const presets = [
        { label: '21st Century', start: '2001-01-01', end: '', id: '21st' },
        { label: '20th Century', start: '1901-01-01', end: '2000-12-31', id: '20th' },
        { label: '19th Century', start: '1801-01-01', end: '1900-12-31', id: '19th' },
        { label: '18th Century', start: '1701-01-01', end: '1800-12-31', id: '18th' },
        { label: 'Medieval (500-1500)', start: '0500-01-01', end: '1500-12-31', id: 'medieval' },
    ];

    const handlePresetClick = (preset: typeof presets[0]) => {
        setStartDate(preset.start);
        setEndDate(preset.end);
        setActivePreset(preset.id);
        onFilterChange(preset.start || null, preset.end || null);
    };

    const handleCustomDateChange = () => {
        setActivePreset(null);
        onFilterChange(startDate || null, endDate || null);
    };

    const handleClearFilter = () => {
        setStartDate('');
        setEndDate('');
        setActivePreset(null);
        onFilterChange(null, null);
    };

    useEffect(() => {
        if (startDate || endDate) {
            handleCustomDateChange();
        }
    }, [startDate, endDate]);

    if (!isOpen) return null;

    return (
        <>
            <div 
                className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:hidden"
                onClick={onClose}
            />
            
            <div className={`
                fixed top-0 left-0 md:left-4 md:top-4
                w-full md:w-80 h-full md:h-auto md:max-h-[calc(100vh-8rem)]
                bg-black/40 backdrop-blur-md border border-white/10
                md:rounded-xl shadow-2xl z-50 flex flex-col
                ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
                transition-transform duration-300 ease-out
            `}>
                <div className="flex items-center justify-between p-4 md:p-6 border-b border-white/10 flex-shrink-0">
                    <div className="flex items-center gap-3">
                        <Clock className="w-5 h-5 text-white/80" />
                        <h3 className="text-lg font-semibold text-white">Time Filter</h3>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-white/60" />
                    </button>
                </div>

                <div className="p-4 md:p-6 space-y-6 overflow-y-auto flex-1 min-h-0">
                    <div>
                        <h4 className="text-sm font-medium text-white/80 mb-3">Quick Filters</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-1 gap-2">
                            {presets.map((preset) => (
                                <button
                                    key={preset.id}
                                    onClick={() => handlePresetClick(preset)}
                                    className={`
                                        p-3 text-left rounded-lg border transition-all duration-200
                                        hover:bg-white/10 hover:border-white/20
                                        ${activePreset === preset.id 
                                            ? 'bg-blue-500/20 border-blue-400/40 text-blue-100' 
                                            : 'bg-white/5 border-white/10 text-white/90'
                                        }
                                    `}
                                >
                                    <div className="font-medium text-sm">{preset.label}</div>
                                    <div className="text-xs text-white/60 mt-1">
                                        {preset.start || 'Beginning'} - {preset.end || 'Present'}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <h4 className="text-sm font-medium text-white/80 mb-3">Custom Range</h4>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs text-white/60 mb-1">From Date (optional)</label>
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    min="0001-01-01"
                                    max="2024-12-31"
                                    className="
                                        w-full px-3 py-2 bg-white/10 border border-white/20 
                                        rounded-lg text-white placeholder-white/40
                                        focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400/50
                                        backdrop-blur-sm
                                    "
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-white/60 mb-1">To Date (optional)</label>
                                <input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    min="0001-01-01"
                                    max="2024-12-31"
                                    className="
                                        w-full px-3 py-2 bg-white/10 border border-white/20 
                                        rounded-lg text-white placeholder-white/40
                                        focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400/50
                                        backdrop-blur-sm
                                    "
                                />
                            </div>
                        </div>
                    </div>

                    {(startDate || endDate || activePreset) && (
                        <button
                            onClick={handleClearFilter}
                            className="
                                w-full py-3 px-4 bg-red-500/20 hover:bg-red-500/30 
                                border border-red-400/30 hover:border-red-400/50
                                text-red-100 rounded-lg transition-all duration-200
                                font-medium
                            "
                        >
                            Clear Filter
                        </button>
                    )}
                </div>
            </div>
        </>
    );
};

export default TimeFilter;