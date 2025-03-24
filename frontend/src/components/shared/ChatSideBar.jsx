import { IoChatbubbleEllipsesOutline } from "react-icons/io5";
import { FaPlus } from "react-icons/fa";



const ChatSidebar = ({ pastChats, handlerOnSelectChat, handlerNewChat, selectedModel, handleSelectLLM }) => {

    return (
        <aside className="w-72 h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white p-5 shadow-xl flex flex-col relative">
            <h2 className="text-2xl font-extrabold mb-4 tracking-wide text-blue-400">Chats</h2>
            <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar">
                {pastChats.length > 0 ? (
                    pastChats.map((chat) => (
                        <button
                            key={chat.id}
                            onClick={() => handlerOnSelectChat(chat)}
                            className="flex items-center space-x-3 p-4 w-full text-left rounded-lg bg-gray-800 hover:bg-blue-600 transition-all shadow-sm"
                        >
                            <IoChatbubbleEllipsesOutline size={20} className="text-blue-300" />
                            <span className="truncate text-sm font-medium">{chat.title || `New Chat ${chat.id}`}</span>
                        </button>
                    ))
                ) : (
                    <p className="text-gray-400 text-sm text-center mt-4">No chats available</p>
                )}
            </div>

            <button
                onClick={handlerNewChat}
                className="flex items-center space-x-3 bg-blue-500 hover:bg-blue-400 text-white px-6 py-3 rounded-full shadow-lg transition-all"
            >
                <FaPlus size={16} />
                <span className="text-sm font-semibold">New Chat</span>
            </button>
            <select
                value={selectedModel}
                onChange={handleSelectLLM}
                className="w-full p-3 my-3 bg-gray-700 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
            >
                <option value="gemini">Gemini</option>
                <option value="deepseek-r1:1.5b">Deepseek-r1:1.5b</option>
            </select>
        </aside>
    );
};

export default ChatSidebar;


