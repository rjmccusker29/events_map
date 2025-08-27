import { useNavigate } from "react-router-dom";

const AboutPage = () => {
    const navigate = useNavigate();

    return (
        <>
            <div className="w-screen min-h-screen flex flex-col items-center justify-center">
                <div className="max-w-180 px-2">
                    <div className="text-3xl font-bold">About</div>
                    <div className="mt-3">This map shows the locations of notable events. All data collected from Wikidata and Wikipedia</div>
                    <div className="mt-3">I tried to find all Wikipedia articles that correspond to an event. Some articles made it through that are not events because I'm a little silly.</div>
                    <div className="mt-3">Page view-counts are from May 2025, at the time of writing this. I intend to update this data for less biased statistics.</div>
                    <div className="mt-3">Created by Ryan McCusker</div>
                    <div  className="mt-3">
                        <a href="https://github.com/rjmccusker29/events_map" target="_blank" rel="noopener noreferrer" className="hover:text-gray-500">https://github.com/rjmccusker29/events_map</a>
                    </div>
                    <button className='cursor-pointer mt-3 border py-1 px-2 rounded hover:bg-gray-200' onClick={() => navigate('/')}>Return to map</button>
                </div>
            </div>
        </>
    );
};

export default AboutPage;