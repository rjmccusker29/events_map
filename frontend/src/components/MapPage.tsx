import Map from './Map';
import { useNavigate } from 'react-router-dom';

const MapPage = () => {
    const navigate = useNavigate();

    return (
        <>
            <div className='w-full h-full relative'>
                <button className='absolute top-4 right-6 z-50 text-white hover:text-gray-300 cursor-pointer' onClick={() => navigate('/about')}>About</button>
                <Map />;
            </div>
        </>
    );
};

export default MapPage;