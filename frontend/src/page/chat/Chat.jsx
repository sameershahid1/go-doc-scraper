import { useRef, useState } from 'react';
import ChatSidebar from '../../components/shared/ChatSideBar';
import Header from '../../components/shared/Header';
import "./style.css"


const ChatPage = () => {
    const [chats, setChats] = useState([])
    const [currentMessage, setCurrentMessage] = useState({
        id: 0,
        title: "Starting New chat",
        result: "Starting New chat"
    })
    const [selectedModel, setSelectedModel] = useState("gemini");
    const queryInput = useRef(null)
    const [isLoading, setIsLoading] = useState(false);

    const handleSend = async () => {
        const query = queryInput.current.value
        if (query.trim().length === 0) {
            alert("No query is forward")
            return
        }

        setIsLoading(true)
        setCurrentMessage("")
        const response = await fetch("http://127.0.0.1:8001/chat/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                model: selectedModel
            }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let result = ""
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const decoded = decoder.decode(value, { stream: true });
            result += decoded
            setCurrentMessage((prev) => ({ ...prev, result: prev.result + decoded }));
            await new Promise(requestAnimationFrame);
        }


        setChats((prev) => ([...prev, { id: prev.length + 1, title: query, result: result }]))
        setIsLoading(false)
    }

    const handleInputChange = () => {
        queryInput.current.style.height = "auto";
        queryInput.current.style.height = `${queryInput.current.scrollHeight}px`;
    };

    const handleSelectLLM = (e) => {
        setSelectedModel(e.target.value)
    }

    const handlerNewChat = () => {
        setCurrentMessage({
            id: 0,
            title: "Starting New chat",
            result: "Starting New chat"
        })
    }

    const handlerOnSelectChat = (chat) => {
        setCurrentMessage(chat)
    }

    return (
        <div className="flex h-full">
            <ChatSidebar
                pastChats={chats}
                handlerOnSelectChat={handlerOnSelectChat}
                handlerNewChat={handlerNewChat}
                selectedModel={selectedModel}
                handleSelectLLM={handleSelectLLM}
            />
            <div className='w-full h-full'>
                <Header />
                <div className='flex flex-col items-center gap-10 justify-center p-6'>
                    <pre className="w-full bg-gray-700 p-4 rounded-lg mt-3 text-sm font-mono overflow-y-auto max-h-64 whitespace-pre-wrap border border-gray-600">
                        <code className="text-green-400">{isLoading ? "LOADING..." : currentMessage.result}</code>
                    </pre>

                    <div className="justify-self-end w-full p-5 bg-gray-700 rounded-xl shadow-lg">
                        <div className='flex items-center gap-2'>
                            <textarea
                                rows={1}
                                ref={queryInput}
                                placeholder="Ask anything..."
                                onChange={handleInputChange}
                                className="w-full outline-none border-none p-3 bg-gray-700 text-white border border-gray-600 rounded-xl placeholder-gray-400 resize-none overflow-y-auto custom-scroll max-h-[150px]"
                            />

                            <button
                                onClick={() => handleSend(selectedModel)}
                                className="flex items-center space-x-3 bg-blue-500 hover:bg-blue-400 text-white px-6 py-3 rounded-lg shadow-lg transition-all"
                            >
                                Send
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ChatPage

