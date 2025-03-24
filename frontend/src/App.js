import { Route, Routes } from 'react-router-dom';
import KnowledgePage from './page/chat/Knowledge';
import EditorPage from './page/chat/Editor';
import ChatPage from './page/chat/Chat';


function App() {

    return (
        <div className='bg-gray-800 text-white min-h-[100vh]'>
            <Routes>
                <Route path="/" element={<ChatPage />} />
                <Route path="/editor" element={<EditorPage />} />
                <Route path="/knowledge" element={<KnowledgePage />} />
            </Routes>
        </div>
    );
}


export default App;




